"""Low-level service functions interacting with the Snippe 2026-01-25 API and Django ORM."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from .conf import get_client, get_default_currency
