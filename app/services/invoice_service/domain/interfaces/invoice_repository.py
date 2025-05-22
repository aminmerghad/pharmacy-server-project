from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.services.invoice_service.domain.entities.invoice import Invoice
from app.services.invoice_service.domain.enums.invoice_status import InvoiceStatus

class InvoiceRepository(ABC):
    """Repository interface for invoice entities."""
    
    @abstractmethod
    def add(self, invoice: Invoice) -> Invoice:
        """
        Add a new invoice to the repository.
        
        Args:
            invoice: The invoice to add
            
        Returns:
            The added invoice with any generated IDs
        """
        pass
        
    @abstractmethod
    def get(self, invoice_id: UUID) -> Optional[Invoice]:
        """
        Get an invoice by its ID.
        
        Args:
            invoice_id: The ID of the invoice to retrieve
            
        Returns:
            The invoice if found, None otherwise
        """
        pass
        
    @abstractmethod
    def update(self, invoice: Invoice) -> Invoice:
        """
        Update an existing invoice.
        
        Args:
            invoice: The invoice to update
            
        Returns:
            The updated invoice
        """
        pass
        
    @abstractmethod
    def delete(self, invoice_id: UUID) -> bool:
        """
        Delete an invoice by its ID.
        
        Args:
            invoice_id: The ID of the invoice to delete
            
        Returns:
            True if the invoice was deleted, False otherwise
        """
        pass
        
    @abstractmethod
    def get_all(self, limit: Optional[int] = None) -> List[Invoice]:
        """
        Get all invoices.
        
        Args:
            limit: Optional maximum number of invoices to return
            
        Returns:
            List of invoices
        """
        pass
        
    @abstractmethod
    def find_by_order_id(self, order_id: UUID) -> Optional[Invoice]:
        """
        Find an invoice by its associated order ID.
        
        Args:
            order_id: The order ID to find the invoice for
            
        Returns:
            The invoice if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: str) -> List[Invoice]:
        """Get all invoices for a specific user."""
        pass
    
    @abstractmethod
    def get_by_status(self, status: InvoiceStatus) -> List[Invoice]:
        """Get all invoices with a specific status."""
        pass
    
    @abstractmethod
    def get_overdue_invoices(self) -> List[Invoice]:
        """Get all overdue invoices."""
        pass
    
    @abstractmethod
    def get_invoices_due_soon(self, days: int) -> List[Invoice]:
        """Get all invoices due within a certain number of days."""
        pass
    
    @abstractmethod
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Invoice]:
        """Get all invoices created within a date range."""
        pass 