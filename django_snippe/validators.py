"""Input validation utilities for Snippe payments, payouts, and sessions (API 2026-01-25)."""

from typing import List, Optional, Sequence, Tuple

from django.core.exceptions import ValidationError

from .conf import get_min_payment_amount, get_min_payout_amount

SUPPORTED_CURRENCIES = {"TZS", "KES", "UGX"}

SUPPORTED_PAYMENT_TYPES = {"mobile", "card", "dynamic-qr"}

