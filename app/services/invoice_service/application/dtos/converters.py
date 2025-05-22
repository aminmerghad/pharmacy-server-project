from typing import List

from app.services.invoice_service.domain.entities.invoice import Invoice
from app.services.invoice_service.application.dtos.invoice_dto import InvoiceDTO, InvoiceItemDTO

def invoice_to_dto(invoice: Invoice) -> InvoiceDTO:
    """
    Convert an invoice entity to a DTO.
    
    Args:
        invoice: The invoice entity to convert
        
    Returns:
        Invoice DTO
    """
    # Convert invoice items to DTOs
    item_dtos = [
        InvoiceItemDTO(
            product_id=item.product_id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal
        )
        for item in invoice.items
    ]
    
    # Create and return the invoice DTO
    return InvoiceDTO(
        id=invoice.id,
        order_id=invoice.order_id,
        user_id=invoice.user_id,
        items=item_dtos,
        total_amount=invoice.total_amount,
        tax_amount=invoice.tax_amount,
        discount_amount=invoice.discount_amount,
        status=invoice.status,
        due_date=invoice.due_date,
        created_at=invoice.created_at,
        updated_at=invoice.updated_at,
        paid_at=invoice.paid_at,
        payment_details=invoice.payment_details,
        notes=invoice.notes
    ) 