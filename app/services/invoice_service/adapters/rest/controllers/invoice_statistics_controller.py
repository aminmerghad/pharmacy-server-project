from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, jsonify
from flask_restful import Resource
import logging

from app.services.invoice_service.application.use_cases.get_invoice_statistics_use_case import GetInvoiceStatisticsUseCase
from app.services.invoice_service.domain.repositories.invoice_repository import InvoiceRepository
from app.shared.error_handling import handle_exceptions

logger = logging.getLogger(__name__)

class InvoiceStatisticsResource(Resource):
    """Resource for fetching invoice statistics data."""
    
    def __init__(self, invoice_repository: InvoiceRepository):
        self.use_case = GetInvoiceStatisticsUseCase(invoice_repository)
    
    def get(self, stats_type: Optional[str] = "summary") -> Dict[str, Any]:
        """
        Get invoice statistics based on the specified type.
        
        Args:
            stats_type: Type of statistics to retrieve (summary, time_series, aging)
            
        Returns:
            Dictionary containing the requested statistics
        """
        # Parse query parameters
        start_date = self._parse_date(request.args.get("start_date"))
        end_date = self._parse_date(request.args.get("end_date"))
        interval = request.args.get("interval", "month")
        
        # Extract filters from query parameters
        filters = {}
        for key, value in request.args.items():
            if key not in ["start_date", "end_date", "interval"]:
                filters[key] = value
        
        # Execute the use case
        return self.use_case.execute(
            stats_type=stats_type,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            filters=filters
        )
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse a date string into a datetime object."""
        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                return None


class CustomerInvoiceStatisticsResource(Resource):
    """Resource for fetching invoice statistics data for a specific customer."""
    
    def __init__(self, invoice_repository: InvoiceRepository):
        self.use_case = GetInvoiceStatisticsUseCase(invoice_repository)
    
    def get(self, customer_id: str) -> Dict[str, Any]:
        """
        Get invoice statistics for a specific customer.
        
        Args:
            customer_id: ID of the customer to retrieve statistics for
            
        Returns:
            Dictionary containing customer-specific invoice statistics
        """
        # Parse query parameters
        stats_type = request.args.get("type", "summary")
        start_date = self._parse_date(request.args.get("start_date"))
        end_date = self._parse_date(request.args.get("end_date"))
        interval = request.args.get("interval", "month")
        
        # Extract filters from query parameters
        filters = {}
        for key, value in request.args.items():
            if key not in ["type", "start_date", "end_date", "interval"]:
                filters[key] = value
        
        # Execute the use case
        return self.use_case.execute(
            stats_type=stats_type,
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            filters=filters
        )
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse a date string into a datetime object."""
        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                return None 