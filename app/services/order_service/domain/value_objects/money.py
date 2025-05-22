from dataclasses import dataclass
from decimal import Decimal
from typing import Union

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __init__(self, amount: Union[Decimal, int, float, str], currency: str = "USD"):
        object.__setattr__(self, 'amount', Decimal(str(amount)).quantize(Decimal('0.01')))
        object.__setattr__(self, 'currency', currency)

    def __add__(self, other: 'Money') -> 'Money':
        if not isinstance(other, Money):
            raise TypeError("Can only add Money to Money")
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: 'Money') -> 'Money':
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money from Money")
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, multiplier: Union[int, float, Decimal]) -> 'Money':
        if not isinstance(multiplier, (int, float, Decimal)):
            raise TypeError("Can only multiply Money by a number")
        return Money(self.amount * Decimal(str(multiplier)), self.currency)

    def __truediv__(self, divisor: Union[int, float, Decimal]) -> 'Money':
        if not isinstance(divisor, (int, float, Decimal)):
            raise TypeError("Can only divide Money by a number")
        if Decimal(str(divisor)) == 0:
            raise ValueError("Cannot divide by zero")
        return Money(self.amount / Decimal(str(divisor)), self.currency)

    def __lt__(self, other: 'Money') -> bool:
        self._validate_currency(other)
        return self.amount < other.amount

    def __le__(self, other: 'Money') -> bool:
        self._validate_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: 'Money') -> bool:
        self._validate_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: 'Money') -> bool:
        self._validate_currency(other)
        return self.amount >= other.amount

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.currency == other.currency and self.amount == other.amount

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:,.2f}"

    def _validate_currency(self, other: 'Money') -> None:
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies") 