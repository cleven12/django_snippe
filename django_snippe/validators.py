"""Validation functions for payment and payout data."""

import re
from typing import Tuple

from django.core.exceptions import ValidationError


class CurrencyValidator:
    """Validates currency codes and amounts."""

    SUPPORTED_CURRENCIES = {"TZS", "KES", "UGX"}
    MIN_AMOUNTS = {"TZS": 100, "KES": 100, "UGX": 1000}
    MAX_AMOUNTS = {"TZS": 50000000, "KES": 5000000, "UGX": 50000000}

    @classmethod
    def validate_currency(cls, currency: str) -> bool:
        """Check if currency is supported."""
        if currency not in cls.SUPPORTED_CURRENCIES:
            raise ValidationError(
                f"Currency {currency} not supported. Use: {', '.join(cls.SUPPORTED_CURRENCIES)}"
            )
        return True

    @classmethod
    def validate_amount(cls, amount: int, currency: str) -> bool:
        """Validate amount is within allowed range for currency."""
        cls.validate_currency(currency)
        
        min_amount = cls.MIN_AMOUNTS.get(currency, 0)
        max_amount = cls.MAX_AMOUNTS.get(currency, 999999999)

        if amount < min_amount:
            raise ValidationError(f"Amount {amount} below minimum for {currency}: {min_amount}")
        if amount > max_amount:
            raise ValidationError(f"Amount {amount} above maximum for {currency}: {max_amount}")
        
        return True


class PhoneValidator:
    """Validates phone numbers."""

    @staticmethod
    def validate_phone(phone_number: str, country_code: str = "TZ") -> bool:
        """Validate phone number format."""
        # Remove spaces, hyphens, plus signs
        cleaned = re.sub(r"[\s\-\+]", "", phone_number)

        # Tanzania: 255... or 0... (10-13 digits)
        if country_code == "TZ":
            if cleaned.startswith("255"):
                return len(cleaned) == 12
            elif cleaned.startswith("0"):
                return len(cleaned) == 10
            raise ValidationError(f"Invalid Tanzania phone: {phone_number}")

        # Kenya: 254... or 0... (10-13 digits)
        if country_code == "KE":
            if cleaned.startswith("254"):
                return len(cleaned) == 12
            elif cleaned.startswith("0"):
                return len(cleaned) == 10
            raise ValidationError(f"Invalid Kenya phone: {phone_number}")

        # Uganda: 256... or 0... (10-13 digits)
        if country_code == "UG":
            if cleaned.startswith("256"):
                return len(cleaned) == 12
            elif cleaned.startswith("0"):
                return len(cleaned) == 10
            raise ValidationError(f"Invalid Uganda phone: {phone_number}")

        raise ValidationError(f"Unknown country code: {country_code}")


class PaymentValidator:
    """Validates payment data."""

    @staticmethod
    def validate_payment_data(
        amount: int, currency: str, phone_number: str, payment_type: str
    ) -> Tuple[bool, list]:
        """Validate all payment fields together."""
        errors = []

        try:
            CurrencyValidator.validate_amount(amount, currency)
        except ValidationError as e:
            errors.append(str(e))

        try:
            PhoneValidator.validate_phone(phone_number)
        except ValidationError as e:
            errors.append(str(e))

        if payment_type not in ["mobile", "card", "dynamic-qr"]:
            errors.append(f"Invalid payment type: {payment_type}")

        return len(errors) == 0, errors


class PayoutValidator:
    """Validates payout data."""

    @staticmethod
    def validate_payout_data(
        amount: int, currency: str, channel: str, recipient_name: str, recipient_phone: str = None
    ) -> Tuple[bool, list]:
        """Validate all payout fields together."""
        errors = []

        try:
            CurrencyValidator.validate_amount(amount, currency)
        except ValidationError as e:
            errors.append(str(e))

        if channel not in ["mobile", "bank"]:
            errors.append(f"Invalid payout channel: {channel}")

        if channel == "mobile" and not recipient_phone:
            errors.append("Phone number required for mobile payouts")

        if channel == "mobile" and recipient_phone:
            try:
                PhoneValidator.validate_phone(recipient_phone)
            except ValidationError as e:
                errors.append(str(e))

        if not recipient_name or len(recipient_name.strip()) < 2:
            errors.append("Recipient name must be at least 2 characters")

        return len(errors) == 0, errors
