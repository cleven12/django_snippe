"""Input validation utilities for Snippe payments, payouts, and sessions (API 2026-01-25)."""

from typing import List, Optional, Sequence, Tuple

from django.core.exceptions import ValidationError

from .conf import get_min_payment_amount, get_min_payout_amount

SUPPORTED_CURRENCIES = {"TZS", "KES", "UGX"}

SUPPORTED_PAYMENT_TYPES = {"mobile", "card", "dynamic-qr"}

SUPPORTED_PAYOUT_CHANNELS = {"mobile", "bank"}

SUPPORTED_SESSION_METHODS = {"mobile_money", "card", "qr", "mobile", "dynamic-qr"}

SUPPORTED_BANK_CODES = {
    "ABSA",
    "ACCESS",
    "AKIBA",
    "AMANA",
    "AZANIA",
    "BOA",
    "BARODA",
    "BANCABC",
    "CITIBANK",
    "CRDB",
    "DCB",
    "DTB",
    "ECOBANK",
    "EQUITY",
    "EXIM",
    "FINCA",
    "GTBANK",
    "HABIB",
    "ICBANK",
    "IMBANK",
    "KCB",
    "LETSHEGO",
    "MKOMBOZI",
    "MWALIMU",
    "MWANGA",
    "NBC",
    "NCBA",
    "NMB",
    "PBZ",
    "SELCOM",
    "STANBIC",
    "SCB",
    "TCB",
    "TPB",
    "UBA",
    "UCHUMI",
    "YETU",
}

MAX_IDEMPOTENCY_KEY_LENGTH = 30

EAST_AFRICA_PHONE_REGEX_PARTS = [
    r"^(\+?255|0)[67]\d{8}$",
    r"^(\+?254|0)[17]\d{8}$",
    r"^(\+?256|0)7\d{8}$",
]


def _normalize_phone(phone: str) -> str:
    """Normalize East African mobile number to local 10-digit 0XXXXXXXXX form."""
    if not phone or not isinstance(phone, str):
        return ""
    cleaned = "".join(c for c in phone if c.isdigit())
    if cleaned.startswith(("255", "254", "256")) and len(cleaned) > 9:
        cleaned = "0" + cleaned[3:]
    return cleaned


def normalize_phone_e164(phone: str, default_country_code: str = "255") -> str:
    """Normalize phone number into 12-digit country code format (e.g. 255712345678)."""
    if not phone or not isinstance(phone, str):
        return ""
    cleaned = "".join(c for c in phone if c.isdigit())
    if cleaned.startswith(("255", "254", "256")) and len(cleaned) == 12:
        return cleaned
    if cleaned.startswith("0") and len(cleaned) == 10:
        return f"{default_country_code}{cleaned[1:]}"
    if len(cleaned) == 9 and cleaned[0] in {"6", "7", "1"}:
        return f"{default_country_code}{cleaned}"
    return cleaned


def _is_valid_east_africa_phone(phone: str) -> bool:
    """Return True if phone is a valid Tanzanian, Kenyan, or Ugandan mobile number."""
    if not phone or not isinstance(phone, str):
        return False
    cleaned = _normalize_phone(phone)
    if len(cleaned) != 10:
        return False
    if not cleaned.startswith("0"):
        return False
    second = cleaned[1:2]
    return second in {"1", "2", "3", "4", "5", "6", "7"}


def validate_idempotency_key(value: Optional[str]) -> None:
    """Validate idempotency key per Snippe 2026-01-25 rules (1-30 chars)."""
    if value is None or value == "":
        return
    if not isinstance(value, str):
        raise ValidationError("idempotency_key must be a string.")
    stripped = value.strip()
    if not stripped or len(stripped) > MAX_IDEMPOTENCY_KEY_LENGTH:
        raise ValidationError(
            f"idempotency_key must be between 1 and {MAX_IDEMPOTENCY_KEY_LENGTH} characters."
        )


def validate_bank_code(value: Optional[str]) -> None:
    """Validate Tanzanian bank code for bank payouts."""
    if not value:
        return
    normalized = str(value).strip().upper()
    if normalized not in SUPPORTED_BANK_CODES:
        raise ValidationError(
            f"{value!r} is not a recognized bank code. Supported examples: CRDB, NMB, NBC, ABSA."
        )


class CurrencyValidator:
    """Django model field validator for currency codes."""

    @staticmethod
    def validate_currency(value: str) -> None:
        if not value or str(value).upper() not in SUPPORTED_CURRENCIES:
            supported = ", ".join(sorted(SUPPORTED_CURRENCIES))
            raise ValidationError(f"{value!r} is not a supported currency. Use one of {supported}.")


class PhoneValidator:
    """Django model field validator for East African mobile numbers."""

    @staticmethod
    def validate_phone(value: str) -> None:
        if not _is_valid_east_africa_phone(value):
            raise ValidationError(f"{value!r} is not a valid East African mobile number.")


def validate_recipient_name(value: str) -> None:
    """Django model field validator for payout recipient names."""
    if not value or not isinstance(value, str) or len(value.strip()) < 2:
        raise ValidationError("recipient_name must be at least 2 characters.")


class PaymentValidator:
    """Validation helpers for payment creation requests."""

    @staticmethod
    def validate_payment_data(
        amount: int,
        currency: str,
        phone_number: str,
        payment_type: str,
        *,
        enforce_minimum: bool = False,
        idempotency_key: Optional[str] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Validate payment creation parameters.

        Returns:
            Tuple of (is_valid, list_of_error_messages).
        """
        errors: List[str] = []

        if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            errors.append("amount must be a positive integer")
        elif enforce_minimum:
            min_amount = get_min_payment_amount()
            if amount < min_amount:
                errors.append(f"amount must be at least {min_amount}")

        if not currency or currency not in SUPPORTED_CURRENCIES:
            errors.append(f"currency must be one of {', '.join(sorted(SUPPORTED_CURRENCIES))}")

        if payment_type == "mobile":
            if not _is_valid_east_africa_phone(phone_number):
                errors.append("phone_number must be a valid East African mobile number")
        elif payment_type in {"card", "dynamic-qr"}:
            if phone_number and not _is_valid_east_africa_phone(phone_number):
                errors.append("phone_number must be a valid East African mobile number")
        else:
            errors.append(f"unsupported payment_type: {payment_type}")

        if idempotency_key is not None:
            try:
                validate_idempotency_key(idempotency_key)
            except ValidationError as exc:
                errors.extend(exc.messages)

        return len(errors) == 0, errors
