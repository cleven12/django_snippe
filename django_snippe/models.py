"""Django models for Snippe payments, payouts, checkout sessions, and webhook audit events."""

from django.core.validators import MinValueValidator
from django.db import models

from .logging import PaymentLogger, PayoutLogger, SessionLogger
from .validators import (
    CurrencyValidator,
    PhoneValidator,
    validate_idempotency_key,
    validate_recipient_name,
)


class SnippePayment(models.Model):
    """Stores a payment record from the Snippe API (2026-01-25)."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"
        VOIDED = "voided", "Voided"

