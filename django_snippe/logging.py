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
        currency: str,
        phone_number: str,
        user: Any = None,
    ) -> None:
        """Log when a payment record is created."""
        message = (
            f"Payment created | ref={reference} | type={payment_type} | "
            f"amount={amount} {currency} | phone={phone_number} | user={_get_user(user)}"
        )
        logger.info(message)

    @staticmethod
    def log_payment_status_change(
        reference: str,
        old_status: str,
        new_status: str,
        reason: Optional[str] = None,
    ) -> None:
        """Log when a payment status transitions."""
        message = f"Payment status changed | ref={reference} | {old_status} -> {new_status}"
        if reason:
            message += f" | reason={reason}"
        logger.info(message)

    @staticmethod
    def log_payment_failed(reference: str, error_message: str) -> None:
        """Log when a payment creation or push operation fails."""
        logger.error(f"Payment creation failed | ref={reference} | error={error_message}")

    @staticmethod
