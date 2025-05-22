from datetime import date, datetime, UTC
from typing import  Optional
from uuid import UUID
from pydantic import BaseModel

from app.services.inventory_service.domain.enums.movement_type import MovementType
from app.shared.contracts.inventory.enums import StockStatusContract
from app.shared.contracts.inventory.stock_check import StockItemValidationContract


class InventoryEntity(BaseModel):
    
    
    quantity: int
    price: float
    max_stock: int
    min_stock: int
    expiry_date: date
    id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    manufacturer_id:Optional[UUID] = None
    supplier_id: Optional[UUID] = None

    

    

    def _validate_base_stock(self) -> StockItemValidationContract:
        """
        Base validation for product status, expiry, and out-of-stock checks.
        Returns a contract with validation results for the current inventory state.
        """
        warnings = []
        status = []
        is_available = True
        days_until_expiry = None

        
        # Check expiry if applicable
        if self.expiry_date:
            days_until_expiry = (self.expiry_date - datetime.now(UTC).date()).days
            if days_until_expiry <= 0:
                is_available = False
                warnings.append(f"Product expired {abs(days_until_expiry)} days ago")
                status.append(StockStatusContract.EXPIRED)
            elif days_until_expiry <= 30:
                warnings.append(f"Product expires in {days_until_expiry} days")
                status.append(StockStatusContract.EXPIRING_SOON)
            elif days_until_expiry <= 90:
                warnings.append(f"Product is approaching expiration ({days_until_expiry} days remaining)")
                status.append(StockStatusContract.EXPIRING_SOON)

        # Check stock availability
        if self.quantity == 0:
            is_available = False
            warnings.append("Product is out of stock")
            status.append(StockStatusContract.OUT_OF_STOCK)
        elif self.quantity <= self.min_stock:
            warnings.append(f"Low stock alert: {self.quantity} units available (minimum threshold: {self.min_stock})")
            status.append(StockStatusContract.LOW_STOCK)

        return StockItemValidationContract(
            is_available=is_available,
            remaining_stock=self.quantity,
            warnings=warnings,
            status=status,
            days_until_expiry=days_until_expiry
        )

    def check_stock_status(self) -> StockItemValidationContract:
        """
        Checks general stock status without considering a requested quantity.
        Returns a complete status assessment of the current inventory item.
        """
        contract = self._validate_base_stock()
        
        # Only add AVAILABLE if no other issues make the product unavailable
        if contract.is_available and not any(s in [
            StockStatusContract.INACTIVE,
            StockStatusContract.EXPIRED,
            StockStatusContract.OUT_OF_STOCK,
            StockStatusContract.INSUFFICIENT_STOCK
        ] for s in contract.status):
            contract.status.append(StockStatusContract.AVAILABLE)
        
        return contract

    def validate_stock_request(self, requested_quantity: int,status:str) -> StockItemValidationContract:
        """
        Validates a stock request considering the requested quantity.
        Returns a detailed validation result including availability and warnings.
        
        Args:
            requested_quantity: The quantity being requested
            
        Returns:
            StockItemValidationContract with validation results including availability,
            remaining stock, warnings, and status codes
        """
        if status != "ACTIVE":
            contract = self._validate_base_stock()
            contract.is_available = False
            contract.warnings.append(f"Product is not active (status: {status})")
            contract.status.append(StockStatusContract.INACTIVE)
            return contract
        # Handle zero or negative requested quantity gracefully
        if requested_quantity <= 0:
            contract = self._validate_base_stock()
            if contract.is_available:
                contract.status.append(StockStatusContract.AVAILABLE)
            return contract
        
        # Start with base validation
        contract = self._validate_base_stock()
        remaining_stock = self.quantity - requested_quantity

        # Check for insufficient stock
        if remaining_stock < 0:
            contract.is_available = False
            contract.warnings.append(
                f"Insufficient stock. Requested: {requested_quantity}, " 
                f"Available: {self.quantity}, Short by: {abs(remaining_stock)}"
            )
            contract.status.append(StockStatusContract.INSUFFICIENT_STOCK)
        # Check if request would bring stock below minimum level (but still possible)
        elif remaining_stock < self.min_stock:
            # Only add this warning if we don't already have LOW_STOCK status
            if StockStatusContract.LOW_STOCK not in contract.status:
                contract.warnings.append(
                    f"Request would reduce stock below minimum threshold. " 
                    f"Remaining after request: {remaining_stock}, Minimum: {self.min_stock}"
                )
                contract.status.append(StockStatusContract.LOW_STOCK)

        # Update remaining stock in contract (clamped at current stock if negative)
        contract.remaining_stock = max(0, remaining_stock)

        # Only add AVAILABLE if product is available and no blocking issues
        if contract.is_available and not any(s in [
            StockStatusContract.INACTIVE,
            StockStatusContract.EXPIRED,
            StockStatusContract.OUT_OF_STOCK,
            StockStatusContract.INSUFFICIENT_STOCK
        ] for s in contract.status):
            contract.status.append(StockStatusContract.AVAILABLE)

        return contract

    def reserve_stock(self, quantity: int) -> bool:
        """
        Attempts to reserve stock for an order.
        Returns True if successful, False if insufficient stock.
        """
        validation = self.validate_stock_request(quantity)
        if validation.is_available:
            self.quantity -= quantity
            return True
        return False

    def release_stock(self, quantity: int) -> None:
        """
        Releases previously reserved stock back to available inventory.
        Raises ValueError if release would exceed maximum stock level.
        """
        new_quantity = self.quantity + quantity
        if new_quantity > self.max_stock:
            raise ValueError(f"Stock release would exceed maximum stock level of {self.max_stock}")
        self.quantity = new_quantity

    def adjust_stock(self, quantity: int, reason: str, movement_type: MovementType) -> None:
        """
        Adjusts stock level by the specified quantity (positive or negative).
        Validates against min/max stock levels.
        
        Args:
            quantity: Amount to adjust (positive for increase, negative for decrease)
            reason: Reason for the adjustment
            movement_type: Type of movement (should be ADJUSTMENT_INCREASE or ADJUSTMENT_DECREASE)
        
        Returns:
            None
            
        Raises:
            ValueError: If adjustment would result in negative stock or exceed max stock
        """
        if not reason:
            raise ValueError("Reason must be provided for stock adjustments")
            
        if movement_type not in [MovementType.ADJUSTMENT_INCREASE, MovementType.ADJUSTMENT_DECREASE]:
            raise ValueError(f"Invalid movement type for adjustment: {movement_type}")
            
        # Ensure quantity matches movement type
        if movement_type == MovementType.ADJUSTMENT_INCREASE and quantity < 0:
            raise ValueError("Quantity must be positive for ADJUSTMENT_INCREASE")
        elif movement_type == MovementType.ADJUSTMENT_DECREASE and quantity > 0:
            raise ValueError("Quantity must be negative for ADJUSTMENT_DECREASE")
            
        new_quantity = self.quantity + quantity
        
        if new_quantity < 0:
            raise ValueError("Stock adjustment would result in negative stock")
        if new_quantity > self.max_stock:
            raise ValueError(f"Stock adjustment would exceed maximum stock level of {self.max_stock}")
            
        self.quantity = new_quantity

    def receive_stock(self, quantity: int, batch_number: Optional[str] = None, 
                     expiry_date: Optional[date] = None, supplier_id: Optional[UUID] = None) -> None:
        """
        Receive new stock into inventory with batch tracking information.
        
        Args:
            quantity: Amount of stock received
            batch_number: Batch or lot number for tracking
            expiry_date: Expiration date for this batch
            supplier_id: ID of the supplier providing this stock
            
        Raises:
            ValueError: If quantity is invalid or would exceed max stock
        """
        if quantity <= 0:
            raise ValueError("Received quantity must be positive")
            
        new_quantity = self.quantity + quantity
        if new_quantity > self.max_stock:
            raise ValueError(f"Receiving stock would exceed maximum stock level of {self.max_stock}")
            
        # Update inventory with new batch information
        self.quantity = new_quantity
        
        if batch_number:
            self.batch_number = batch_number
            
        if expiry_date:
            self.expiry_date = expiry_date
            
        if supplier_id:
            self.supplier_id = supplier_id
            
        self.last_restock_date = datetime.now(UTC).date()

    def is_near_expiry(self, days_threshold: int = 90) -> bool:
        """Check if inventory is nearing expiration"""
        if not self.expiry_date:
            return False
            
        days_until_expiry = (self.expiry_date - datetime.now(UTC).date()).days
        return 0 < days_until_expiry <= days_threshold
        
    def is_expired(self) -> bool:
        """Check if inventory is expired"""
        if not self.expiry_date:
            return False
            
        return datetime.now(UTC).date() >= self.expiry_date
        
    def needs_reordering(self) -> bool:
        """Check if inventory needs reordering based on quantity and reorder point"""
        if self.reorder_point is None:
            # Fall back to min_stock if reorder_point not set
            return self.quantity <= self.min_stock
            
        return self.quantity <= self.reorder_point
        
    def days_until_reorder(self) -> Optional[int]:
        """
        Calculate approximate days until reorder will be needed
        based on current quantity and average daily usage.
        
        Returns None if usage rate is unknown or zero.
        """
        # This would require additional usage data to implement
        # Placeholder for future enhancement
        return None
        