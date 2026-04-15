"""Reads Snippe settings from Django settings.py."""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_setting(name, default=None, required=False):
    value = getattr(settings, f"SNIPPE_{name}", default)
    if required and not value:
        raise ImproperlyConfigured(
            f"SNIPPE_{name} is required. Add it to your settings.py."
        )
    return value


def get_client():
    """Return a ready-to-use Snippe client using settings.py config."""
    from snippe import Snippe

    api_key = get_setting("API_KEY", required=True)
    base_url = get_setting("BASE_URL")
    timeout = get_setting("TIMEOUT", default=30.0)

    return Snippe(api_key=api_key, base_url=base_url, timeout=timeout)
