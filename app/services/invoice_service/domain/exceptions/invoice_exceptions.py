class InvoiceServiceException(Exception):
    """Base exception for all invoice service exceptions."""
    pass


class InvoiceNotFoundException(InvoiceServiceException):
    """Exception raised when an invoice is not found."""
    def __init__(self, invoice_id: str):
        self.invoice_id = invoice_id
        super().__init__(f"Invoice with ID {invoice_id} not found")


class InvoiceAlreadyPaidException(InvoiceServiceException):
    """Exception raised when trying to modify a paid invoice."""
    def __init__(self, invoice_id: str):
        self.invoice_id = invoice_id
        super().__init__(f"Invoice with ID {invoice_id} is already paid and cannot be modified")


class InvoiceAlreadyCancelledException(InvoiceServiceException):
    """Exception raised when trying to modify a cancelled invoice."""
    def __init__(self, invoice_id: str):
        self.invoice_id = invoice_id
        super().__init__(f"Invoice with ID {invoice_id} is already cancelled and cannot be modified")


class InvalidInvoiceStatusTransitionException(InvoiceServiceException):
    """Exception raised when trying to perform an invalid status transition."""
    def __init__(self, invoice_id: str, current_status: str, target_status: str):
        self.invoice_id = invoice_id
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(
            f"Cannot transition invoice {invoice_id} from {current_status} to {target_status}"
        )


class InvoiceCreationException(InvoiceServiceException):
    """Exception raised when invoice creation fails due to validation errors."""
    def __init__(self, message: str):
        super().__init__(message)


class InvoiceUpdateException(InvoiceServiceException):
    """Exception raised when invoice update fails due to validation errors."""
    def __init__(self, message: str):
        super().__init__(message)


class InvoiceOperationException(InvoiceServiceException):
    """Exception raised when an operation on an invoice fails."""
    def __init__(self, message: str):
        super().__init__(message)


class InvalidInvoiceStateException(InvoiceServiceException):
    """Exception raised when an invoice is in an invalid state for the requested operation."""
    def __init__(self, message: str):
        super().__init__(message)


class PaymentProcessingException(InvoiceServiceException):
    """Exception raised when payment processing fails."""
    def __init__(self, invoice_id: str, reason: str):
        self.invoice_id = invoice_id
        self.reason = reason
        super().__init__(f"Payment processing failed for invoice {invoice_id}: {reason}")


class InvoiceItemNotFoundException(InvoiceServiceException):
    """Exception raised when an invoice item is not found."""
    def __init__(self, invoice_id: str, item_id: str):
        self.invoice_id = invoice_id
        self.item_id = item_id
        super().__init__(f"Item with ID {item_id} not found in invoice {invoice_id}")


class EmptyInvoiceException(InvoiceServiceException):
    """Exception raised when an invoice has no items."""
    def __init__(self, invoice_id: str):
        self.invoice_id = invoice_id
        super().__init__(f"Invoice {invoice_id} must have at least one item")


class InvalidDiscountException(InvoiceServiceException):
    """Exception raised when applying an invalid discount."""
    def __init__(self, invoice_id: str, reason: str):
        self.invoice_id = invoice_id
        self.reason = reason
        super().__init__(f"Invalid discount for invoice {invoice_id}: {reason}") 