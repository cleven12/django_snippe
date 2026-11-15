"""Reads and validates Snippe configuration from Django settings."""

from typing import Any

from django.conf import settings

from .__version__ import API_VERSION
from .exceptions import SnippeConfigError

DEFAULT_BASE_URL = "https://api.snippe.sh"
DEFAULT_TIMEOUT = 30.0
DEFAULT_CURRENCY = "TZS"
