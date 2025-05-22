from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from app.services.invoice_service.domain.entities.invoice import Invoice
from app.services.invoice_service.domain.enums.invoice_status import InvoiceStatus

logger = logging.getLogger(__name__)

class InvoiceStatisticsCalculator:
    """
    Utility class for calculating various invoice statistics and metrics.
    """
    
    @staticmethod
    def calculate_summary_statistics(invoices: List[Invoice]) -> Dict[str, Any]:
        """
        Calculate summary statistics for a collection of invoices.
        
        Args:
            invoices: List of invoice entities
            
        Returns:
            Dictionary containing summary statistics
        """
        logger.info(f"Calculating summary statistics for {len(invoices)} invoices")
        
        # Initialize counters
        total_count = len(invoices)
        paid_count = 0
        pending_count = 0
        overdue_count = 0
        cancelled_count = 0
        
        total_amount = 0.0
        paid_amount = 0.0
        pending_amount = 0.0
        overdue_amount = 0.0
        
        current_date = datetime.now().date()
        
        # Process each invoice
        for invoice in invoices:
            # Add to total amount
            total_amount += invoice.total_amount
            
            # Categorize by status
            if invoice.status == InvoiceStatus.PAID:
                paid_count += 1
                paid_amount += invoice.total_amount
            elif invoice.status == InvoiceStatus.PENDING:
                pending_count += 1
                pending_amount += invoice.total_amount
                
                # Check if overdue
                if invoice.due_date.date() < current_date:
                    overdue_count += 1
                    overdue_amount += invoice.total_amount
            elif invoice.status == InvoiceStatus.CANCELLED:
                cancelled_count += 1
        
        # Calculate percentages (avoid division by zero)
        paid_percentage = (paid_count / total_count * 100) if total_count > 0 else 0
        pending_percentage = (pending_count / total_count * 100) if total_count > 0 else 0
        overdue_percentage = (overdue_count / total_count * 100) if total_count > 0 else 0
        cancelled_percentage = (cancelled_count / total_count * 100) if total_count > 0 else 0
        
        collection_rate = (paid_amount / total_amount * 100) if total_amount > 0 else 0
        
        # Create the result dictionary
        result = {
            "total_invoices": total_count,
            "paid_invoices": {
                "count": paid_count,
                "percentage": round(paid_percentage, 2),
                "amount": round(paid_amount, 2)
            },
            "pending_invoices": {
                "count": pending_count,
                "percentage": round(pending_percentage, 2),
                "amount": round(pending_amount, 2)
            },
            "overdue_invoices": {
                "count": overdue_count,
                "percentage": round(overdue_percentage, 2),
                "amount": round(overdue_amount, 2)
            },
            "cancelled_invoices": {
                "count": cancelled_count,
                "percentage": round(cancelled_percentage, 2)
            },
            "total_amount": round(total_amount, 2),
            "collection_rate": round(collection_rate, 2),
            "average_invoice_value": round(total_amount / total_count, 2) if total_count > 0 else 0
        }
        
        logger.info("Successfully calculated invoice summary statistics")
        return result
    
    @staticmethod
    def calculate_time_series(invoices: List[Invoice], interval: str = "monthly", start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Calculate time series data for invoices.
        
        Args:
            invoices: List of invoice entities
            interval: Time interval ('daily', 'weekly', 'monthly')
            start_date: Start date for the time series (defaults to earliest invoice date)
            end_date: End date for the time series (defaults to today)
            
        Returns:
            Dictionary with time series data
        """
        logger.info(f"Calculating {interval} time series for {len(invoices)} invoices")
        
        if not invoices:
            return {"series": []}
        
        # Determine date range
        if not start_date:
            earliest_invoice = min(invoices, key=lambda inv: inv.created_at)
            start_date = earliest_invoice.created_at
        
        if not end_date:
            end_date = datetime.now()
        
        # Sort invoices by created_at date
        sorted_invoices = sorted(invoices, key=lambda inv: inv.created_at)
        
        # Prepare periods based on interval
        periods = []
        if interval == "daily":
            current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            while current_date <= end_date:
                next_date = current_date + timedelta(days=1)
                periods.append((current_date, next_date, current_date.strftime("%Y-%m-%d")))
                current_date = next_date
        elif interval == "weekly":
            # Start from the beginning of the week
            current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            current_date = current_date - timedelta(days=current_date.weekday())
            
            while current_date <= end_date:
                next_date = current_date + timedelta(days=7)
                periods.append((current_date, next_date, f"Week of {current_date.strftime('%Y-%m-%d')}"))
                current_date = next_date
        else:  # monthly (default)
            current_date = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            while current_date <= end_date:
                # Get the first day of the next month
                if current_date.month == 12:
                    next_date = datetime(current_date.year + 1, 1, 1)
                else:
                    next_date = datetime(current_date.year, current_date.month + 1, 1)
                
                periods.append((current_date, next_date, current_date.strftime("%Y-%m")))
                current_date = next_date
        
        # Calculate data for each period
        series = []
        invoice_index = 0
        total_invoices = len(sorted_invoices)
        
        for period_start, period_end, period_label in periods:
            # Initialize period data
            period_data = {
                "period": period_label,
                "invoice_count": 0,
                "total_amount": 0.0,
                "paid_amount": 0.0,
                "paid_count": 0,
                "pending_count": 0,
                "overdue_count": 0,
                "cancelled_count": 0
            }
            
            # Find invoices in this period
            while invoice_index < total_invoices and sorted_invoices[invoice_index].created_at < period_end:
                invoice = sorted_invoices[invoice_index]
                
                if invoice.created_at >= period_start:
                    period_data["invoice_count"] += 1
                    period_data["total_amount"] += invoice.total_amount
                    
                    if invoice.status == InvoiceStatus.PAID:
                        period_data["paid_count"] += 1
                        period_data["paid_amount"] += invoice.total_amount
                    elif invoice.status == InvoiceStatus.PENDING:
                        period_data["pending_count"] += 1
                        
                        # Check if overdue
                        if invoice.due_date.date() < datetime.now().date():
                            period_data["overdue_count"] += 1
                    elif invoice.status == InvoiceStatus.CANCELLED:
                        period_data["cancelled_count"] += 1
                
                invoice_index += 1
            
            # Round amounts
            period_data["total_amount"] = round(period_data["total_amount"], 2)
            period_data["paid_amount"] = round(period_data["paid_amount"], 2)
            
            series.append(period_data)
        
        logger.info(f"Successfully calculated {interval} time series with {len(series)} periods")
        return {"series": series}
        
    @staticmethod
    def calculate_aging_analysis(invoices: List[Invoice]) -> Dict[str, Any]:
        """
        Perform aging analysis on pending invoices.
        
        Args:
            invoices: List of invoice entities
            
        Returns:
            Dictionary with aging analysis data
        """
        logger.info(f"Performing aging analysis on {len(invoices)} invoices")
        
        current_date = datetime.now().date()
        
        # Filter to only pending invoices
        pending_invoices = [inv for inv in invoices if inv.status == InvoiceStatus.PENDING]
        
        # Initialize age buckets
        buckets = {
            "current": {"count": 0, "amount": 0.0},
            "1_30_days": {"count": 0, "amount": 0.0},
            "31_60_days": {"count": 0, "amount": 0.0},
            "61_90_days": {"count": 0, "amount": 0.0},
            "over_90_days": {"count": 0, "amount": 0.0}
        }
        
        # Categorize each invoice into the appropriate bucket
        for invoice in pending_invoices:
            due_date = invoice.due_date.date()
            days_overdue = (current_date - due_date).days
            
            if days_overdue <= 0:
                buckets["current"]["count"] += 1
                buckets["current"]["amount"] += invoice.total_amount
            elif days_overdue <= 30:
                buckets["1_30_days"]["count"] += 1
                buckets["1_30_days"]["amount"] += invoice.total_amount
            elif days_overdue <= 60:
                buckets["31_60_days"]["count"] += 1
                buckets["31_60_days"]["amount"] += invoice.total_amount
            elif days_overdue <= 90:
                buckets["61_90_days"]["count"] += 1
                buckets["61_90_days"]["amount"] += invoice.total_amount
            else:
                buckets["over_90_days"]["count"] += 1
                buckets["over_90_days"]["amount"] += invoice.total_amount
        
        # Calculate totals
        total_count = sum(bucket["count"] for bucket in buckets.values())
        total_amount = sum(bucket["amount"] for bucket in buckets.values())
        
        # Round amounts and add percentages
        result = {"total_count": total_count, "total_amount": round(total_amount, 2), "buckets": {}}
        
        for key, bucket in buckets.items():
            result["buckets"][key] = {
                "count": bucket["count"],
                "amount": round(bucket["amount"], 2),
                "count_percentage": round((bucket["count"] / total_count * 100) if total_count > 0 else 0, 2),
                "amount_percentage": round((bucket["amount"] / total_amount * 100) if total_amount > 0 else 0, 2)
            }
        
        logger.info("Successfully calculated invoice aging analysis")
        return result 