"""Logging utilities for payment and payout tracking."""

import json
import logging
from datetime import datetime

from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger("django_snippe.audit")


class PaymentLogger:
    """Logs payment activities for audit trails."""

    @staticmethod
    def log_payment_created(reference, payment_type, amount, currency, phone_number, user=None):
        """Log when a payment is created."""
        message = (
            f"Payment created | ref={reference} | type={payment_type} | "
            f"amount={amount} {currency} | phone={phone_number} | user={_get_user(user)}"
        )
        logger.info(message)

    @staticmethod
    def log_payment_status_change(reference, old_status, new_status, reason=None):
        """Log when a payment status changes."""
        message = f"Payment status changed | ref={reference} | {old_status} → {new_status}"
        if reason:
            message += f" | reason={reason}"
        logger.info(message)

    @staticmethod
    def log_payment_failed(reference, error_message):
        """Log when a payment creation fails."""
        logger.error(f"Payment creation failed | ref={reference} | error={error_message}")

    @staticmethod
    def log_webhook_received(event, reference):
        """Log incoming webhook events."""
        logger.info(f"Webhook received | event={event} | ref={reference}")

    @staticmethod
    def log_webhook_processing(event, reference, success, error=None):
        """Log webhook processing result."""
        status = "success" if success else "failed"
        message = f"Webhook processed | event={event} | ref={reference} | status={status}"
        if error:
            message += f" | error={error}"
            logger.error(message)
        else:
            logger.info(message)


class PayoutLogger:
    """Logs payout activities for audit trails."""

    @staticmethod
    def log_payout_created(reference, channel, amount, currency, recipient_name, user=None):
        """Log when a payout is created."""
        message = (
            f"Payout created | ref={reference} | channel={channel} | "
            f"amount={amount} {currency} | recipient={recipient_name} | user={_get_user(user)}"
        )
        logger.info(message)

    @staticmethod
    def log_payout_status_change(reference, old_status, new_status, reason=None):
        """Log when a payout status changes."""
        message = f"Payout status changed | ref={reference} | {old_status} → {new_status}"
        if reason:
            message += f" | reason={reason}"
        logger.info(message)

    @staticmethod
    def log_payout_failed(reference, error_message):
        """Log when a payout creation fails."""
        logger.error(f"Payout creation failed | ref={reference} | error={error_message}")


def _get_user(user):
    """Get user identifier from request user."""
    if user is None or isinstance(user, AnonymousUser):
        return "anonymous"
    if hasattr(user, "username"):
        return user.username
    return str(user)
