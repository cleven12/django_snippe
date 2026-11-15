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
