from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from app.services.invoice_service.domain.enums.invoice_status import InvoiceStatus
from app.dataBase import db
class InvoiceModel(db.Model):
    """SQLAlchemy model for invoices."""
    __tablename__ = 'invoices'
    
    invoice_id = Column(String(36), primary_key=True)
    order_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    status = Column(Enum(InvoiceStatus), nullable=False, default=InvoiceStatus.PENDING)
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False, default=0.0)
    discount_amount = Column(Float, nullable=False, default=0.0)
    total_amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    paid_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    items = relationship("InvoiceItemModel", back_populates="invoice", cascade="all, delete-orphan")
    payment_details = relationship("PaymentDetailsModel", back_populates="invoice", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Invoice {self.invoice_id} for order {self.order_id}, status: {self.status.value}>"


class InvoiceItemModel(db.Model):
    """SQLAlchemy model for invoice items."""
    __tablename__ = 'invoice_items'
    
    item_id = Column(String(36), primary_key=True)
    invoice_id = Column(String(36), ForeignKey('invoices.invoice_id'), nullable=False)
    product_id = Column(String(36), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    
    # Relationships
    invoice = relationship("InvoiceModel", back_populates="items")
    
    def __repr__(self):
        return f"<InvoiceItem {self.item_id} for invoice {self.invoice_id}, product: {self.product_id}>"


class PaymentDetailsModel(db.Model):
    """SQLAlchemy model for payment details."""
    __tablename__ = 'payment_details'
    
    payment_id = Column(String(36), primary_key=True)
    invoice_id = Column(String(36), ForeignKey('invoices.invoice_id'), nullable=False, unique=True)
    payment_method = Column(String(50), nullable=False)
    transaction_id = Column(String(255), nullable=True)
    payment_date = Column(DateTime, nullable=True)
    payer_name = Column(String(255), nullable=True)
    payment_reference = Column(String(255), nullable=True)
    
    # Relationships
    invoice = relationship("InvoiceModel", back_populates="payment_details")
    
    def __repr__(self):
        return f"<PaymentDetails for invoice {self.invoice_id}, method: {self.payment_method}>" 