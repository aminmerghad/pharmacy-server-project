from enum import Enum, auto

class PaymentMethod(str, Enum):
    """Enumeration of possible payment methods."""
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    CASH = "CASH"
    INSURANCE = "INSURANCE"
    EDAHABIA = "EDAHABIA"
    CIB = "CIB"
    OTHER = "OTHER" 