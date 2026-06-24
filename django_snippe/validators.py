"""Input validation for payments and payouts."""

from typing import Tuple, List


SUPPORTED_CURRENCIES = {"TZS", "KES", "UGX"}

# East Africa phone patterns (loose but practical)
# Accepts:
# - Local: 0712345678, 255712345678, +255712345678, 2567..., etc.
# - Minimum 9 digits after stripping non-digits, common prefixes
EAST_AFRICA_PHONE_REGEX_PARTS = [
    r"^(\+?255|0)7[1-9]\d{7}$",      # Tanzania
    r"^(\+?254|0)7\d{8}$",            # Kenya
    r"^(\+?256|0)7\d{8}$",            # Uganda (and similar)
]


def _normalize_phone(phone: str) -> str:
    """Strip non-digits and common leading chars."""
    if not phone:
        return ""
    cleaned = "".join(c for c in phone if c.isdigit())
    # Strip leading country code variations to local-ish
    if cleaned.startswith("255") and len(cleaned) > 9:
        cleaned = "0" + cleaned[3:]
    elif cleaned.startswith("254") and len(cleaned) > 9:
        cleaned = "0" + cleaned[3:]
    elif cleaned.startswith("256") and len(cleaned) > 9:
        cleaned = "0" + cleaned[3:]
    return cleaned


def _is_valid_east_africa_phone(phone: str) -> bool:
    """Validate common East African mobile formats."""
    if not phone:
        return False
    cleaned = _normalize_phone(phone)
    if len(cleaned) < 9:
        return False
    # Basic checks for common starts
    if cleaned.startswith("0"):
        second = cleaned[1:2]
        # 07x for TZ/KE/UG rough
        if second in {"7", "6"} and len(cleaned) >= 10:
            return True
        if second in {"1", "2", "3", "4", "5"} and len(cleaned) == 10:
            return True
    # Full international forms that survived normalize
    if cleaned.startswith(("255", "254", "256")) and len(cleaned) >= 12:
        return True
    return False


class PaymentValidator:
    """Validation helpers for payment creation."""

    @staticmethod
    def validate_payment_data(
        amount: int,
        currency: str,
        phone_number: str,
        payment_type: str,
    ) -> Tuple[bool, List[str]]:
        """Validate payment input.

        Returns:
            (is_valid, list_of_errors)
        """
        errors: List[str] = []

        if not isinstance(amount, int) or amount <= 0:
            errors.append("amount must be a positive integer")

        if currency not in SUPPORTED_CURRENCIES:
            errors.append(f"currency must be one of {', '.join(sorted(SUPPORTED_CURRENCIES))}")

        if payment_type == "mobile":
            if not _is_valid_east_africa_phone(phone_number):
                errors.append("phone_number must be a valid East African mobile number")
        elif payment_type == "card":
            # Card payments usually don't require phone in initial create
            pass
        elif payment_type == "dynamic-qr":
            pass
        else:
            errors.append(f"unsupported payment_type: {payment_type}")

        return len(errors) == 0, errors


class PayoutValidator:
    """Validation helpers for payout creation."""

    @staticmethod
    def validate_payout_data(
        amount: int,
        currency: str,
        channel: str,
        recipient_name: str,
        recipient_phone: str = "",
    ) -> Tuple[bool, List[str]]:
        """Validate payout input."""
        errors: List[str] = []

        if not isinstance(amount, int) or amount <= 0:
            errors.append("amount must be a positive integer")

        if currency not in SUPPORTED_CURRENCIES:
            errors.append(f"currency must be one of {', '.join(sorted(SUPPORTED_CURRENCIES))}")

        if not recipient_name or len(recipient_name.strip()) < 2:
            errors.append("recipient_name is required")

        if channel == "mobile":
            if not _is_valid_east_africa_phone(recipient_phone):
                errors.append("recipient_phone must be a valid East African mobile number for mobile payouts")
        elif channel == "bank":
            # Bank payouts may not need phone
            pass
        else:
            errors.append(f"unsupported channel: {channel}")

        return len(errors) == 0, errors
