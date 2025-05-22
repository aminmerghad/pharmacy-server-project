from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal
# from value_objects.insurance_details import InsuranceDetails  # Assuming this exists
# from value_objects.medication_details import MedicationDetails  # Assuming this exists

class InsuranceDetails:
    pass

class MedicationDetails:
    pass

@dataclass
class PriceCalculator:
    """
    A value object to handle complex pricing rules for orders, medications, or other products.
    """

    @staticmethod
    def calculate_base_price(unit_price: Decimal, quantity: int) -> Decimal:
        """
        Calculate the base price for a product (unit price * quantity).
        """
        return unit_price * Decimal(quantity)

    @staticmethod
    def apply_discount(base_price: Decimal, discount_percentage: Decimal) -> Decimal:
        """
        Apply a discount percentage to the base price.
        """
        if discount_percentage < 0 or discount_percentage > 100:
            raise ValueError("Discount percentage must be between 0 and 100.")
        return base_price * (1 - discount_percentage / 100)

    @staticmethod
    def apply_tax(base_price: Decimal, tax_rate: Decimal) -> Decimal:
        """
        Apply a tax rate to the base price.
        """
        if tax_rate < 0:
            raise ValueError("Tax rate cannot be negative.")
        return base_price * (1 + tax_rate / 100)

    @staticmethod
    def calculate_insurance_coverage(
        base_price: Decimal, insurance_details: Optional[InsuranceDetails]
    ) -> Decimal:
        """
        Calculate the insurance coverage amount based on the insurance details.
        """
        if not insurance_details:
            return Decimal(0)
        return base_price * (insurance_details.coverage_percentage / 100)

    @staticmethod
    def calculate_final_price(
        unit_price: Decimal,
        quantity: int,
        discount_percentage: Decimal = Decimal(0),
        tax_rate: Decimal = Decimal(0),
        insurance_details: Optional[InsuranceDetails] = None,
    ) -> Decimal:
        """
        Calculate the final price after applying discounts, taxes, and insurance coverage.
        """
        base_price = PriceCalculator.calculate_base_price(unit_price, quantity)
        discounted_price = PriceCalculator.apply_discount(base_price, discount_percentage)
        price_after_tax = PriceCalculator.apply_tax(discounted_price, tax_rate)
        insurance_coverage = PriceCalculator.calculate_insurance_coverage(
            price_after_tax, insurance_details
        )
        final_price = price_after_tax - insurance_coverage
        return final_price

    @staticmethod
    def calculate_medication_price(
        medication_details: MedicationDetails,
        quantity: int,
        discount_percentage: Decimal = Decimal(0),
        tax_rate: Decimal = Decimal(0),
        insurance_details: Optional[InsuranceDetails] = None,
    ) -> Decimal:
        """
        Calculate the final price for a medication, including dosage and insurance considerations.
        """
        base_price = PriceCalculator.calculate_base_price(
            medication_details.unit_price, quantity
        )
        discounted_price = PriceCalculator.apply_discount(base_price, discount_percentage)
        price_after_tax = PriceCalculator.apply_tax(discounted_price, tax_rate)
        insurance_coverage = PriceCalculator.calculate_insurance_coverage(
            price_after_tax, insurance_details
        )
        final_price = price_after_tax - insurance_coverage
        return final_price