from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

@dataclass
class InvoiceEvent:
    """Base class for all invoice events."""
    invoice_id: str
    order_id: str
    user_id: str
    timestamp: datetime
    
    @classmethod
    def create(cls, **kwargs):
        """Factory method to create an event with current timestamp."""
        if 'timestamp' not in kwargs:
            kwargs['timestamp'] = datetime.now()
        return cls(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary representation."""
        return {
            'invoice_id': self.invoice_id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class InvoiceCreatedEvent(InvoiceEvent):
    """Event emitted when a new invoice is created."""
    due_date: datetime
    total_amount: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary representation."""
        data = super().to_dict()
        data.update({
            'event_type': 'invoice.created',
            'total_amount': self.total_amount,
            'due_date': self.due_date.isoformat()
        })
        return data

@dataclass
class InvoiceStatusChangedEvent(InvoiceEvent):
    """Event emitted when an invoice's status changes."""
    previous_status: str
    new_status: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary representation."""
        data = super().to_dict()
        data.update({
            'event_type': 'invoice.status_changed',
            'previous_status': self.previous_status,
            'new_status': self.new_status
        })
        return data

@dataclass
class InvoicePaidEvent(InvoiceEvent):
    """Event emitted when an invoice is paid."""
    amount_paid: float
    payment_method: str
    transaction_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary representation."""
        data = super().to_dict()
        data.update({
            'event_type': 'invoice.paid',
            'amount_paid': self.amount_paid,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id
        })
        return data

@dataclass
class InvoiceCancelledEvent(InvoiceEvent):
    """Event emitted when an invoice is cancelled."""
    reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary representation."""
        data = super().to_dict()
        data.update({
            'event_type': 'invoice.cancelled',
            'reason': self.reason
        })
        return data

@dataclass
class InvoiceOverdueEvent(InvoiceEvent):
    """Event emitted when an invoice becomes overdue."""
    due_date: datetime
    days_overdue: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary representation."""
        data = super().to_dict()
        data.update({
            'event_type': 'invoice.overdue',
            'due_date': self.due_date.isoformat(),
            'days_overdue': self.days_overdue
        })
        return data 