"""Reads Snippe settings from Django settings.py."""

from django.conf import settings

from .exceptions import SnippeConfigError


def get_setting(name, default=None, required=False):
    """
    Get a Snippe setting from Django settings.

    Args:
        name: Setting name (without SNIPPE_ prefix)
        default: Default value if not found
        required: If True, raises SnippeConfigError if not found

    Raises:
        SnippeConfigError: If required setting is missing

    Returns:
        Setting value or default
    """
    value = getattr(settings, f"SNIPPE_{name}", default)
    if required and not value:
        raise SnippeConfigError(
            f"SNIPPE_{name} is required. Add it to your settings.py."
        )
    return value


def get_client():
    """
    Return a ready-to-use Snippe client using settings.py config.

    Raises:
        SnippeConfigError: If SNIPPE_API_KEY is not configured

    Returns:
        Snippe: Initialized Snippe API client
    """
    from snippe import Snippe

    api_key = get_setting("API_KEY", required=True)
    base_url = get_setting("BASE_URL")
    timeout = get_setting("TIMEOUT", default=30.0)

    try:
        return Snippe(api_key=api_key, base_url=base_url, timeout=timeout)
    except Exception as e:
        raise SnippeConfigError(f"Failed to initialize Snippe client: {e}") from e
