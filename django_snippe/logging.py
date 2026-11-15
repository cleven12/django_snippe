"""Audit logging utilities for Snippe payments, payouts, sessions, and webhooks."""

import logging
from typing import Any, Optional

from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger("django_snippe.audit")


class PaymentLogger:
    """Logs payment lifecycle activities for audit trails."""

    @staticmethod
    def log_payment_created(
        reference: str,
        payment_type: str,
        amount: int,
