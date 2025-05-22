from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Union

@dataclass(frozen=True)
class Money:
    """
    Value object for monetary amounts in a specific currency.
    This ensures consistent handling of money throughout the system.
    """
    amount: Decimal
    currency: str = "DZD"  # Default to Algerian Dinar for Chargily compatibility
    
    def __post_init__(self):
        """Validate money object after initialization."""
        # Convert amount to Decimal if it's not already
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
            
        # Validate currency
        if not isinstance(self.currency, str) or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter currency code (ISO 4217)")
            
        # Ensure currency is uppercase
        if not self.currency.isupper():
            object.__setattr__(self, 'currency', self.currency.upper())
    
    def __str__(self):
        """String representation of the money object."""
        return f"{self.amount} {self.currency}"
    
    def __add__(self, other: 'Money') -> 'Money':
        """Add two money objects with the same currency."""
        if not isinstance(other, Money):
            raise TypeError("Can only add Money to Money")
            
        if self.currency != other.currency:
            raise ValueError(f"Cannot add different currencies: {self.currency} and {other.currency}")
            
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: 'Money') -> 'Money':
        """Subtract one money object from another with the same currency."""
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money from Money")
            
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract different currencies: {self.currency} and {other.currency}")
            
        return Money(self.amount - other.amount, self.currency)
    
    def __mul__(self, factor: Union[int, float, Decimal]) -> 'Money':
        """Multiply the amount by a factor."""
        if not isinstance(factor, (int, float, Decimal)):
            raise TypeError("Can only multiply Money by a number")
            
        return Money(self.amount * Decimal(str(factor)), self.currency)
    
    def __eq__(self, other: object) -> bool:
        """Compare two money objects for equality."""
        if not isinstance(other, Money):
            return False
            
        return self.amount == other.amount and self.currency == other.currency
    
    def __lt__(self, other: 'Money') -> bool:
        """Compare if self is less than other."""
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
            
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare different currencies: {self.currency} and {other.currency}")
            
        return self.amount < other.amount
    
    def __gt__(self, other: 'Money') -> bool:
        """Compare if self is greater than other."""
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
            
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare different currencies: {self.currency} and {other.currency}")
            
        return self.amount > other.amount
    
    @classmethod
    def zero(cls, currency: str = "DZD") -> 'Money':
        """Create a zero money object with the given currency."""
        return cls(Decimal('0'), currency) 