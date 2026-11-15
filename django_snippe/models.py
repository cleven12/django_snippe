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
    customer_firstname = models.CharField(max_length=100, blank=True, null=True)
    customer_lastname = models.CharField(max_length=100, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    idempotency_key = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        validators=[validate_idempotency_key],
    )
    fee_amount = models.PositiveIntegerField(blank=True, null=True)
    net_amount = models.PositiveIntegerField(blank=True, null=True)
    psp_reference = models.CharField(max_length=100, blank=True, null=True)
    payment_channel = models.CharField(max_length=50, blank=True, null=True)
    failure_reason = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
