from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from app.services.invoice_service.domain.repositories.invoice_repository import InvoiceRepository
from app.services.invoice_service.application.utilities.invoice_statistics import InvoiceStatisticsCalculator

logger = logging.getLogger(__name__)

class GetInvoiceStatisticsUseCase:
    """
    Use case for retrieving various invoice statistics and metrics.
    """
    
    def __init__(self, invoice_repository: InvoiceRepository):
        self.invoice_repository = invoice_repository
    
    def execute(self, stats_type: str, filters: Optional[Dict[str, Any]] = None, 
                interval: str = "monthly", start_date: Optional[datetime] = None, 
                end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Retrieve invoice statistics based on the requested type.
        
        Args:
            stats_type: Type of statistics to retrieve ('summary', 'time_series', 'aging')
            filters: Optional filters to apply when fetching invoices
            interval: Time interval for time series data ('daily', 'weekly', 'monthly')
            start_date: Start date for filtering invoices or time series
            end_date: End date for filtering invoices or time series
            
        Returns:
            Dictionary containing the requested statistics
        """
        logger.info(f"Retrieving invoice statistics of type: {stats_type}")
        
        # Initialize filters if not provided
        if filters is None:
            filters = {}
            
        # Add date filters if provided
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
            
        # Fetch invoices with the applied filters
        invoices = self.invoice_repository.find_all(filters)
        logger.info(f"Found {len(invoices)} invoices matching the filters")
        
        # Calculate the requested statistics
        if stats_type == "summary":
            return InvoiceStatisticsCalculator.calculate_summary_statistics(invoices)
        elif stats_type == "time_series":
            return InvoiceStatisticsCalculator.calculate_time_series(
                invoices, interval=interval, start_date=start_date, end_date=end_date)
        elif stats_type == "aging":
            return InvoiceStatisticsCalculator.calculate_aging_analysis(invoices)
        else:
            logger.error(f"Invalid statistics type requested: {stats_type}")
            raise ValueError(f"Invalid statistics type: {stats_type}. Valid types are 'summary', 'time_series', and 'aging'.")
            
    def get_customer_invoice_summary(self, customer_id: str) -> Dict[str, Any]:
        """
        Get invoice statistics summary for a specific customer.
        
        Args:
            customer_id: ID of the customer
            
        Returns:
            Dictionary with customer invoice statistics
        """
        logger.info(f"Retrieving invoice statistics for customer: {customer_id}")
        
        # Fetch all invoices for the customer
        filters = {"customer_id": customer_id}
        invoices = self.invoice_repository.find_all(filters)
        
        if not invoices:
            logger.info(f"No invoices found for customer {customer_id}")
            return {
                "customer_id": customer_id,
                "total_invoices": 0,
                "total_amount": 0,
                "paid_amount": 0,
                "pending_amount": 0,
                "overdue_amount": 0
            }
        
        # Calculate statistics
        stats = InvoiceStatisticsCalculator.calculate_summary_statistics(invoices)
        
        # Create customer-specific summary
        customer_summary = {
            "customer_id": customer_id,
            "total_invoices": stats["total_invoices"],
            "total_amount": stats["total_amount"],
            "paid_amount": stats["paid_invoices"]["amount"],
            "paid_invoices": stats["paid_invoices"]["count"],
            "pending_amount": stats["pending_invoices"]["amount"],
            "pending_invoices": stats["pending_invoices"]["count"],
            "overdue_amount": stats["overdue_invoices"]["amount"],
            "overdue_invoices": stats["overdue_invoices"]["count"],
            "collection_rate": stats["collection_rate"],
            "average_invoice_value": stats["average_invoice_value"]
        }
        
        logger.info(f"Successfully calculated invoice statistics for customer {customer_id}")
        return customer_summary 