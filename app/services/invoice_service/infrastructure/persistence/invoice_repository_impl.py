from typing import List, Optional
from datetime import datetime
import uuid
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.services.invoice_service.domain.interfaces.invoice_repository import InvoiceRepository
from app.services.invoice_service.domain.entities.invoice import Invoice
from app.services.invoice_service.domain.entities.invoice_item import InvoiceItem
from app.services.invoice_service.domain.value_objects.money import Money
from app.services.invoice_service.domain.value_objects.payment_details import PaymentDetails
from app.services.invoice_service.domain.enums.invoice_status import InvoiceStatus
from app.services.invoice_service.domain.enums.payment_method import PaymentMethod
from app.services.invoice_service.infrastructure.persistence.models import (
    InvoiceModel,
    InvoiceItemModel,
    PaymentDetailsModel
)

class SQLAlchemyInvoiceRepository():
    """SQLAlchemy implementation of the invoice repository."""
    
    def __init__(self, session: Session):
        self.session = session
    def get_by_id(self, invoice_id: str) -> Invoice:
        """Get an invoice from the repository."""
        invoice_model =self.session.query(InvoiceModel).filter_by(invoice_id=invoice_id).first()
        if not invoice_model:
            return None
        return Invoice(
            order_id=invoice_model.order_id,
            user_id=invoice_model.user_id,
            due_date=invoice_model.due_date,
            invoice_id=invoice_model.invoice_id,
            status=invoice_model.status,
            payment_details=invoice_model.payment_details,
            created_at=invoice_model.created_at,
            updated_at=invoice_model.updated_at,
            paid_at=invoice_model.paid_at,
            notes=invoice_model.notes,
            items=[InvoiceItem(
                product_id="",
                description="",
                quantity=5,
                unit_price=Money(Decimal('0.00')),
                item_id="",
            )]
        )
    
    def save(self, invoice: Invoice) -> Invoice:
        """Save an invoice to the repository."""
        # Check if this is an update or new invoice
        existing_model = self.session.query(InvoiceModel).filter_by(invoice_id=invoice.invoice_id).first()
        
        if existing_model:
            # Update existing model
            existing_model.status = invoice.status
            existing_model.subtotal = float(invoice.subtotal.amount)
            existing_model.tax_amount = float(invoice.tax_amount.amount)
            existing_model.discount_amount = float(invoice.discount_amount.amount)
            existing_model.total_amount = float(invoice.total_amount.amount)
            existing_model.due_date = invoice.due_date
            existing_model.updated_at = invoice.updated_at
            existing_model.paid_at = invoice.paid_at
            existing_model.notes = invoice.notes
            
            # Handle items - first remove deleted items
            item_ids = [item.item_id for item in invoice.items if item.item_id]
            for item_model in existing_model.items[:]:
                if item_model.item_id not in item_ids:
                    self.session.delete(item_model)
            
            # Then update or add items
            for item in invoice.items:
                if not item.item_id:
                    item.item_id = str(uuid.uuid4())
                    
                existing_item = next(
                    (i for i in existing_model.items if i.item_id == item.item_id), 
                    None
                )
                
                if existing_item:
                    # Update existing item
                    existing_item.product_id = item.product_id
                    existing_item.description = item.description
                    existing_item.quantity = item.quantity
                    existing_item.unit_price = float(item.unit_price.amount)
                    existing_item.subtotal = float(item.subtotal.amount)
                else:
                    # Add new item
                    item_model = InvoiceItemModel(
                        item_id=item.item_id,
                        invoice_id=invoice.invoice_id,
                        product_id=item.product_id,
                        description=item.description,
                        quantity=item.quantity,
                        unit_price=float(item.unit_price.amount),
                        subtotal=float(item.subtotal.amount)
                    )
                    existing_model.items.append(item_model)
            
            # Handle payment details
            if invoice.payment_details:
                if existing_model.payment_details:
                    # Update existing payment details
                    existing_model.payment_details.payment_method = invoice.payment_details.payment_method.value
                    existing_model.payment_details.transaction_id = invoice.payment_details.transaction_id
                    existing_model.payment_details.payment_date = invoice.payment_details.payment_date
                    existing_model.payment_details.payer_name = invoice.payment_details.payer_name
            return invoice
        self.session.add(InvoiceModel(
            invoice_id=invoice.invoice_id,
            order_id=invoice.order_id,
            user_id=invoice.user_id,
            status=invoice.status,
            subtotal=invoice.subtotal.amount,
            tax_amount=invoice.tax_amount.amount,
            discount_amount=invoice.discount_amount.amount, 
            total_amount=invoice.total_amount.amount,
            due_date=invoice.due_date,
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
            paid_at=invoice.paid_at,
            notes=invoice.notes,
        ))
        self.session.flush()
        return invoice
    
        
        