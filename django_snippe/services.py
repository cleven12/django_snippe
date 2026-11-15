"""Low-level service functions interacting with the Snippe 2026-01-25 API and Django ORM."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from .conf import get_client, get_default_currency
from .models import SnippePayment, SnippePayout, SnippeSession


def _opt_str(obj: Any, attr: str) -> Optional[str]:
    """Return string attribute if present and a real str, otherwise None."""
    val = getattr(obj, attr, None)
    return val if isinstance(val, str) else None


def _opt_int(obj: Any, attr: str) -> Optional[int]:
    """Return integer attribute if present and a real int (not bool), otherwise None."""
    val = getattr(obj, attr, None)
    return val if isinstance(val, int) and not isinstance(val, bool) else None


def _parse_dt(value: Any) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp string into a timezone-aware datetime object."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _extract_amount_and_currency(
    raw_amount: Any, fallback_currency: str = "TZS"
) -> tuple[int, str]:
    """Extract integer amount and currency from either an int or 2026-01-25 {value, currency} dict."""
    if isinstance(raw_amount, dict):
        return int(raw_amount.get("value", 0)), str(raw_amount.get("currency", fallback_currency))
    val = getattr(raw_amount, "value", None)
    cur = getattr(raw_amount, "currency", None)
    if isinstance(val, int) and not isinstance(val, bool):
        return val, cur if isinstance(cur, str) else fallback_currency
    if isinstance(raw_amount, int) and not isinstance(raw_amount, bool):
        return raw_amount, fallback_currency
    return 0, fallback_currency


def _save_payment(
    result: Any,
    phone_number: str,
    payment_type: str,
    webhook_url: Optional[str],
    metadata: Optional[Dict[str, Any]],
    *,
    callback_url: Optional[str] = None,
    customer: Any = None,
    idempotency_key: Optional[str] = None,
) -> SnippePayment:
    """Persist or update a SnippePayment model from an SDK Payment response."""
    cust_first = _opt_str(customer, "firstname")
    cust_last = _opt_str(customer, "lastname")
    cust_email = _opt_str(customer, "email")
    if isinstance(customer, dict):
        cust_first = customer.get("firstname") or customer.get("first_name")
        cust_last = customer.get("lastname") or customer.get("last_name")
        cust_email = customer.get("email")

    res_metadata = getattr(result, "metadata", None)
    resolved_meta = (
        metadata
        if isinstance(metadata, dict)
        else (res_metadata if isinstance(res_metadata, dict) else {})
    )

    defaults = {
        "payment_type": _opt_str(result, "payment_type") or payment_type,
        "amount": _opt_int(result, "amount") or 0,
        "currency": _opt_str(result, "currency") or get_default_currency(),
        "phone_number": phone_number or "",
        "status": _opt_str(result, "status") or SnippePayment.Status.PENDING,
        "payment_url": _opt_str(result, "payment_url"),
        "payment_qr_code": _opt_str(result, "payment_qr_code"),
        "payment_token": _opt_str(result, "payment_token"),
        "callback_url": callback_url,
