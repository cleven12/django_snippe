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

    class PaymentType(models.TextChoices):
        MOBILE = "mobile", "Mobile Money"
        CARD = "card", "Card"
        QR = "dynamic-qr", "QR Code"

    reference = models.CharField(max_length=100, unique=True)
    payment_type = models.CharField(max_length=20, choices=PaymentType.choices)
    amount = models.PositiveIntegerField(validators=[MinValueValidator(100)])
    currency = models.CharField(max_length=10, validators=[CurrencyValidator.validate_currency])
    phone_number = models.CharField(
        max_length=20, blank=True, default="", validators=[PhoneValidator.validate_phone]
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_url = models.URLField(blank=True, null=True)
    payment_qr_code = models.TextField(blank=True, null=True)
    payment_token = models.CharField(max_length=100, blank=True, null=True)
    callback_url = models.URLField(blank=True, null=True)
    webhook_url = models.URLField(blank=True, null=True)
