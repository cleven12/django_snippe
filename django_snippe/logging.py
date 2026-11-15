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
    def log_payment_push_triggered(reference: str, phone_number: Optional[str] = None) -> None:
        """Log when a USSD push retry is triggered for a pending payment."""
        phone_part = f" | phone={phone_number}" if phone_number else ""
        logger.info(f"Payment USSD push triggered | ref={reference}{phone_part}")

    @staticmethod
    def log_webhook_received(event: str, reference: str) -> None:
        """Log incoming webhook events."""
        logger.info(f"Webhook received | event={event} | ref={reference}")

    @staticmethod
    def log_webhook_processing(
        event: str,
        reference: str,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """Log webhook processing outcome."""
        status = "success" if success else "failed"
        message = f"Webhook processed | event={event} | ref={reference} | status={status}"
        if error:
            message += f" | error={error}"
            logger.error(message)
        else:
