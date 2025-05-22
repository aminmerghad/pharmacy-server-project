from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.services.inventory_service.domain.entities.inventory_entity import InventoryEntity
from app.services.inventory_service.domain.enums.stock_status import StockStatus
from app.services.inventory_service.domain.exceptions.inventory_errors import InventoryNotFoundError, ProductNotFoundError
from app.services.inventory_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.product_service.domain.entities.product_entity import ProductEntity
from app.services.product_service.domain.enums.product_status import ProductStatus
from app.shared.contracts.inventory.enums import StockStatusContract
from app.shared.contracts.inventory.stock_check import (
    StockCheckErrorDetail,
    StockCheckErrorType,
    StockCheckRequestContract,
    StockCheckResponseContract,
    StockCheckSummaryContract,
    StockItemResultContract,
    StockItemValidationContract
)


class StockCheckUseCase:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
    
    def execute(self, request: StockCheckRequestContract) -> StockCheckResponseContract:
       
        try:
            stock_results, errors = self._process_stock_check(request)

            
            
            if errors:
                return self._build_error_response(errors)
            return self._build_success_response(stock_results)
        except Exception as e:
            # Handle unexpected errors
            
            return self._build_error_response([
                StockCheckErrorDetail(
                    error_type=StockCheckErrorType.GENERIC_ERROR,
                    message=f"An unexpected error occurred: {str(e)}",
                    details={"exception": str(e)}
                )
            ])
    
    def _process_stock_check(self, request: StockCheckRequestContract) -> Tuple[List[StockItemResultContract], List[StockCheckErrorDetail]]:
        
        """
        Process stock check for all items in the request.
        
        Args:
            request: The stock check request
            
        Returns:
            Tuple containing list of stock results and any errors encountered
        """
        errors = []
        results = []
        
        for item in request.items:
            try:
                # Get inventory and product data
                inventory = self._get_inventory_or_raise(item.product_id)
                # product = self._get_product_or_raise(item.product_id)

                # Check product status - highest priority
                

                
                # Validate stock request 
                validation_result = inventory.validate_stock_request(item.quantity,"ACTIVE")
                

                # Create result item
                results.append(StockItemResultContract(
                    product_id=inventory.product_id,
                    product_name="product.name",
                    requested_quantity=item.quantity,
                    available_quantity=inventory.quantity,
                    minimum_stock_level=inventory.min_stock,
                    maximum_stock_level=inventory.max_stock,
                    unit_price=inventory.price,
                    expiry_date=inventory.expiry_date,
                    stock_validation_result=validation_result,
                    # message=self._generate_status_message(validation_result)
                ))
                 
                
            except InventoryNotFoundError as e:
                errors.append(StockCheckErrorDetail(
                    error_type=StockCheckErrorType.INVENTORY_NOT_FOUND,
                    product_id=item.product_id,
                    message=str(e),
                    details=e.error
                ))
            except ProductNotFoundError as e:
                errors.append(StockCheckErrorDetail(
                    error_type=StockCheckErrorType.PRODUCT_NOT_FOUND,
                    product_id=item.product_id,
                    message=str(e),
                    details=e.error
                ))
            except Exception as e:
                errors.append(StockCheckErrorDetail(
                    error_type=StockCheckErrorType.GENERIC_ERROR,
                    product_id=item.product_id,
                    message=f"Error processing item: {str(e)}",
                    details={"exception": str(e)}
                ))
                
        return results, errors
    
    
    def _get_inventory_or_raise(self, product_id: UUID) -> InventoryEntity:
        """
        Get inventory or raise appropriate error.
        
        Args:
            product_id: The product ID to look up
            
        Returns:
            The inventory entity if found
            
        Raises:
            InventoryNotFoundError: If inventory not found for product
        """
        inventory = self._uow.inventory_repository.get_by_product_id(product_id)
        if not inventory:
            raise InventoryNotFoundError(
                f"Inventory for product {product_id} not found",
                error={"product_id": str(product_id)}
            )
        return inventory
    
    # def _get_product_or_raise(self, product_id: UUID) -> ProductEntity:
    #     """
    #     Get product or raise appropriate error.
        
    #     Args:
    #         product_id: The product ID to look up
            
    #     Returns:
    #         The product entity if found
            
    #     Raises:
    #         ProductNotFoundError: If product not found
    #     """
    #     product = self._u.get_by_id(product_id)
    #     if not product:
    #         raise ProductNotFoundError(f"Product with ID {product_id} not found")
            
        # Get inventory for this product
        inventory = self._uow.inventory_repository.get_by_product_id(product_id)
        if not inventory:
            raise InventoryNotFoundError(
                f"Inventory for product {product_id} not found",
                error={"product_id": str(product_id)}
            )
        return product
    
    def _build_success_response(
        self, 
        results: List[StockItemResultContract]
    ) -> StockCheckResponseContract:
        """
        Build successful response with summary information.
        
        Args:
            results: List of stock check results
            
        Returns:
            A complete response with summary statistics
        """
        # Initialize status counts
        status_counts = {status.value: 0 for status in StockStatusContract}
        
        # Count items by availability and status
        available_count = 0
        for result in results:
            
            for s in  result.stock_validation_result.status :
                status_counts[s.value] += 1
            
            
            if result.stock_validation_result.is_available:
                available_count += 1
        
        # Create summary
        summary = StockCheckSummaryContract(
            total_items=len(results),
            available_items=available_count,
            unavailable_items=len(results) - available_count,
            details=status_counts
        )
        
        return StockCheckResponseContract(
            success=True,
            message="Stock check completed successfully",
            data=results,
            summary=summary
        )
    
    def _build_error_response(
        self, 
        errors: List[StockCheckErrorDetail]
    ) -> StockCheckResponseContract:
        """
        Build error response.
        
        Args:
            errors: List of error details
            
        Returns:
            Error response with details
        """
        return StockCheckResponseContract(
            success=False,
            message=f"Stock check failed with {len(errors)} errors",
            errors=errors
        )