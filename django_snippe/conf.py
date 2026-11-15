"""Reads and validates Snippe configuration from Django settings."""

from typing import Any

from django.conf import settings

from .__version__ import API_VERSION
from .exceptions import SnippeConfigError

DEFAULT_BASE_URL = "https://api.snippe.sh"
DEFAULT_TIMEOUT = 30.0
DEFAULT_CURRENCY = "TZS"
DEFAULT_MIN_PAYMENT_AMOUNT = 500
DEFAULT_MIN_PAYOUT_AMOUNT = 5000
DEFAULT_WEBHOOK_TOLERANCE = 300


def get_setting(name: str, default: Any = None, required: bool = False) -> Any:
    """
    Retrieve a Snippe setting from Django settings.py.

    Args:
        name: Setting suffix without the SNIPPE_ prefix.
        default: Fallback value if the setting is not defined.
        required: If True, raises SnippeConfigError when missing or empty.

    Returns:
        The configured setting value or default.

    Raises:
        SnippeConfigError: If required is True and the setting is missing or empty.
    """
    value = getattr(settings, f"SNIPPE_{name}", default)
    if required and not value:
        raise SnippeConfigError(f"SNIPPE_{name} is required. Add it to your Django settings.py.")
    return value


def get_api_version() -> str:
    """Return the configured Snippe API version (defaults to 2026-01-25)."""
    return str(get_setting("API_VERSION", default=API_VERSION))


def get_default_currency() -> str:
    """Return the default currency code (defaults to TZS per Snippe 2026-01-25 spec)."""
    return str(get_setting("DEFAULT_CURRENCY", default=DEFAULT_CURRENCY)).upper()


def get_min_payment_amount() -> int:
    """Return minimum payment amount in smallest currency unit (500 TZS default)."""
    return int(get_setting("MIN_PAYMENT_AMOUNT", default=DEFAULT_MIN_PAYMENT_AMOUNT))


def get_min_payout_amount() -> int:
    """Return minimum payout amount in smallest currency unit (5000 TZS default)."""
    return int(get_setting("MIN_PAYOUT_AMOUNT", default=DEFAULT_MIN_PAYOUT_AMOUNT))


def get_webhook_tolerance() -> int:
    """Return webhook timestamp tolerance in seconds (300s default)."""
    return int(get_setting("WEBHOOK_TOLERANCE", default=DEFAULT_WEBHOOK_TOLERANCE))


def get_client():
    """
    Return an initialized synchronous Snippe API client from Django settings.

    Raises:
        SnippeConfigError: If SNIPPE_API_KEY is missing or client initialization fails.
    """
    from snippe import Snippe

    api_key = get_setting("API_KEY", required=True)
    base_url = get_setting("BASE_URL")
    timeout = get_setting("TIMEOUT", default=DEFAULT_TIMEOUT)

    try:
        kwargs = {"api_key": api_key, "timeout": timeout}
        if base_url:
            kwargs["base_url"] = base_url
        return Snippe(**kwargs)
    except Exception as exc:
        raise SnippeConfigError(f"Failed to initialize Snippe client: {exc}") from exc


def get_async_client():
    """
    Return an initialized asynchronous AsyncSnippe API client from Django settings.

    Raises:
