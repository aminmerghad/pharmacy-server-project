from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging

from app.services.invoice_service.domain.repositories.invoice_repository import InvoiceRepository

logger = logging.getLogger(__name__)

class GetInvoiceStatisticsUseCase:
    """
    Use case for retrieving invoice statistics based on different criteria.
    Handles the business logic for generating summary, time series, and aging statistics.
    """

    def __init__(self, invoice_repository: InvoiceRepository):
        self.invoice_repository = invoice_repository

    def execute(
        self, 
        stats_type: str, 
        customer_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: Optional[str] = "month",
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes the use case to retrieve invoice statistics.
        
        Args:
            stats_type: Type of statistics to retrieve (summary, time_series, aging)
            customer_id: Optional customer ID to filter statistics by
            start_date: Optional start date for the time range
            end_date: Optional end date for the time range
            interval: Time interval for time series data (day, week, month, quarter, year)
            filters: Additional filters to apply to the query
            
        Returns:
            Dictionary containing the requested statistics
        """
        logger.info(f"Generating {stats_type} statistics" + 
                   (f" for customer {customer_id}" if customer_id else ""))
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            # Default to 12 months for summary and time series, 
            # and 180 days for aging analysis
            if stats_type == "aging":
                start_date = end_date - timedelta(days=180)
            else:
                start_date = end_date - timedelta(days=365)
        
        # Initialize filters if not provided
        if filters is None:
            filters = {}
            
        # Add customer filter if provided
        if customer_id:
            filters["customer_id"] = customer_id
        
        if stats_type == "summary":
            return self._get_summary_statistics(start_date, end_date, filters)
        elif stats_type == "time_series":
            return self._get_time_series_statistics(start_date, end_date, interval, filters)
        elif stats_type == "aging":
            return self._get_aging_statistics(end_date, filters)
        else:
            raise ValueError(f"Invalid statistics type: {stats_type}")
    
    def _get_summary_statistics(
        self, 
        start_date: datetime,
        end_date: datetime,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate summary statistics for invoices.
        
        Returns:
            Dictionary containing summary metrics like total invoices, 
            total value, average value, paid percentage, etc.
        """
        # Get all invoices in the date range with applied filters
        invoices = self.invoice_repository.find_by_filters(
            {"created_at_gte": start_date, "created_at_lte": end_date, **filters}
        )
        
        # Initialize counters
        total_count = len(invoices)
        total_value = 0
        paid_count = 0
        paid_value = 0
        overdue_count = 0
        overdue_value = 0
        pending_count = 0
        pending_value = 0
        
        # Calculate metrics
        for invoice in invoices:
            total_value += invoice.total_amount
            
            if invoice.status == "PAID":
                paid_count += 1
                paid_value += invoice.total_amount
            elif invoice.status == "OVERDUE":
                overdue_count += 1
                overdue_value += invoice.total_amount
            elif invoice.status == "PENDING":
                pending_count += 1
                pending_value += invoice.total_amount
        
        # Calculate averages and percentages
        avg_value = total_value / total_count if total_count > 0 else 0
        paid_percentage = (paid_count / total_count * 100) if total_count > 0 else 0
        overdue_percentage = (overdue_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "total_invoices": total_count,
            "total_value": total_value,
            "average_value": avg_value,
            "paid_invoices": {
                "count": paid_count,
                "value": paid_value,
                "percentage": paid_percentage
            },
            "overdue_invoices": {
                "count": overdue_count,
                "value": overdue_value,
                "percentage": overdue_percentage
            },
            "pending_invoices": {
                "count": pending_count,
                "value": pending_value,
                "percentage": 100 - paid_percentage - overdue_percentage
            },
            "time_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    
    def _get_time_series_statistics(
        self, 
        start_date: datetime,
        end_date: datetime,
        interval: str,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate time series statistics for invoices.
        
        Returns:
            Dictionary containing data points over time for metrics like 
            invoice count, total value, etc.
        """
        # Get all invoices in the date range with applied filters
        invoices = self.invoice_repository.find_by_filters(
            {"created_at_gte": start_date, "created_at_lte": end_date, **filters}
        )
        
        # Generate time periods based on the interval
        time_periods = self._generate_time_periods(start_date, end_date, interval)
        
        # Initialize the result structure
        result = {
            "interval": interval,
            "time_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "data_points": []
        }
        
        # Process invoices into time periods
        for period_start, period_end, period_label in time_periods:
            period_invoices = [
                invoice for invoice in invoices 
                if period_start <= invoice.created_at < period_end
            ]
            
            # Calculate metrics for this period
            total_count = len(period_invoices)
            total_value = sum(invoice.total_amount for invoice in period_invoices)
            paid_count = sum(1 for invoice in period_invoices if invoice.status == "PAID")
            paid_value = sum(invoice.total_amount for invoice in period_invoices if invoice.status == "PAID")
            
            result["data_points"].append({
                "period": period_label,
                "start_date": period_start.isoformat(),
                "end_date": period_end.isoformat(),
                "invoice_count": total_count,
                "total_value": total_value,
                "paid_count": paid_count,
                "paid_value": paid_value
            })
        
        return result
    
    def _get_aging_statistics(
        self, 
        reference_date: datetime,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate aging statistics for unpaid invoices.
        
        Returns:
            Dictionary containing aging buckets (0-30 days, 31-60 days, etc.)
            with invoice counts and values.
        """
        # Get all unpaid invoices with applied filters
        if "status" not in filters:
            filters["status_in"] = ["PENDING", "OVERDUE"]
        
        invoices = self.invoice_repository.find_by_filters(filters)
        
        # Define aging buckets (in days)
        buckets = [
            (0, 30, "0-30 days"),
            (31, 60, "31-60 days"),
            (61, 90, "61-90 days"),
            (91, float('inf'), "90+ days")
        ]
        
        # Initialize result structure
        result = {
            "reference_date": reference_date.isoformat(),
            "total_outstanding": {
                "count": len(invoices),
                "value": sum(invoice.total_amount for invoice in invoices)
            },
            "aging_buckets": []
        }
        
        # Process invoices into aging buckets
        for min_days, max_days, label in buckets:
            min_date = reference_date - timedelta(days=max_days if max_days != float('inf') else 36500)
            max_date = reference_date - timedelta(days=min_days)
            
            bucket_invoices = [
                invoice for invoice in invoices 
                if min_date <= invoice.due_date < max_date
            ]
            
            bucket_count = len(bucket_invoices)
            bucket_value = sum(invoice.total_amount for invoice in bucket_invoices)
            
            result["aging_buckets"].append({
                "range": label,
                "count": bucket_count,
                "value": bucket_value,
                "percentage": (bucket_value / result["total_outstanding"]["value"] * 100) 
                              if result["total_outstanding"]["value"] > 0 else 0
            })
        
        return result
    
    def _generate_time_periods(
        self, 
        start_date: datetime,
        end_date: datetime,
        interval: str
    ) -> List[Tuple[datetime, datetime, str]]:
        """
        Generate time periods based on the specified interval.
        
        Returns:
            List of tuples (period_start, period_end, period_label)
        """
        periods = []
        current = start_date
        
        while current < end_date:
            if interval == "day":
                next_date = datetime(current.year, current.month, current.day) + timedelta(days=1)
                label = current.strftime("%Y-%m-%d")
            elif interval == "week":
                # Start from Monday of the week
                monday = current - timedelta(days=current.weekday())
                next_date = monday + timedelta(days=7)
                label = f"{monday.strftime('%Y-%m-%d')} to {(next_date - timedelta(days=1)).strftime('%Y-%m-%d')}"
            elif interval == "month":
                next_month = current.month + 1
                next_year = current.year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                next_date = datetime(next_year, next_month, 1)
                label = current.strftime("%Y-%m")
            elif interval == "quarter":
                quarter = (current.month - 1) // 3 + 1
                next_quarter = quarter + 1
                next_year = current.year
                if next_quarter > 4:
                    next_quarter = 1
                    next_year += 1
                next_date = datetime(next_year, (next_quarter - 1) * 3 + 1, 1)
                label = f"{current.year} Q{quarter}"
            elif interval == "year":
                next_date = datetime(current.year + 1, 1, 1)
                label = str(current.year)
            else:
                raise ValueError(f"Invalid interval: {interval}")
            
            # Make sure we don't go beyond end_date
            actual_end = min(next_date, end_date)
            periods.append((current, actual_end, label))
            current = next_date
        
        return periods 