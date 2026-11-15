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


