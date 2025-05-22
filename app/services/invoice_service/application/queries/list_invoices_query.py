from typing import List, Optional
from datetime import datetime

from app.services.invoice_service.domain.interfaces.invoice_repository import InvoiceRepository
from app.services.invoice_service.domain.enums.invoice_status import InvoiceStatus
from app.services.invoice_service.application.dtos.invoice_dto import InvoiceDTO

class ListInvoicesQuery:
    """Query for retrieving lists of invoices with various filtering options."""
    
    def __init__(self, invoice_repository: InvoiceRepository):
        self.invoice_repository = invoice_repository
    
    def execute(self) -> List[InvoiceDTO]:
        """
        Execute the query to retrieve all invoices.
        
        Returns:
            A list of DTO representations of invoices
        """
        invoices = self.invoice_repository.get_all()
        return [InvoiceDTO.from_entity(invoice) for invoice in invoices]
    
    def get_by_user_id(self, user_id: str) -> List[InvoiceDTO]:
        """
        Get all invoices for a specific user.
        
        Args:
            user_id: ID of the user to get invoices for
            
        Returns:
            A list of DTO representations of invoices
        """
        invoices = self.invoice_repository.get_by_user_id(user_id)
        return [InvoiceDTO.from_entity(invoice) for invoice in invoices]
    
    def get_by_status(self, status: str) -> List[InvoiceDTO]:
        """
        Get all invoices with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            A list of DTO representations of invoices
            
        Raises:
            ValueError: If the status is invalid
        """
        try:
            status_enum = InvoiceStatus(status)
        except ValueError:
            raise ValueError(f"Invalid invoice status: {status}")
            
        invoices = self.invoice_repository.get_by_status(status_enum)
        return [InvoiceDTO.from_entity(invoice) for invoice in invoices]
    
    def get_overdue_invoices(self) -> List[InvoiceDTO]:
        """
        Get all overdue invoices.
        
        Returns:
            A list of DTO representations of overdue invoices
        """
        invoices = self.invoice_repository.get_overdue_invoices()
        return [InvoiceDTO.from_entity(invoice) for invoice in invoices]
    
    def get_invoices_due_soon(self, days: int = 7) -> List[InvoiceDTO]:
        """
        Get all invoices due within a certain number of days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            A list of DTO representations of invoices due soon
        """
        invoices = self.invoice_repository.get_invoices_due_soon(days)
        return [InvoiceDTO.from_entity(invoice) for invoice in invoices]
    
    def get_by_date_range(self, 
                          start_date: datetime, 
                          end_date: Optional[datetime] = None) -> List[InvoiceDTO]:
        """
        Get all invoices created within a date range.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range, or None for up to current time
            
        Returns:
            A list of DTO representations of invoices in the date range
        """
        if end_date is None:
            end_date = datetime.now()
            
        invoices = self.invoice_repository.get_by_date_range(start_date, end_date)
        return [InvoiceDTO.from_entity(invoice) for invoice in invoices] 