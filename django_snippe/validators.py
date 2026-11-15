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
