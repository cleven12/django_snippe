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
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self) -> str:
        return f"{self.reference} - {self.status} ({self.amount} {self.currency})"

    @property
    def is_terminal(self) -> bool:
        """Return True if the payment is in a final state."""
        return self.status in {
            self.Status.COMPLETED,
            self.Status.FAILED,
            self.Status.EXPIRED,
            self.Status.VOIDED,
        }

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = SnippePayment.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.status != self.status:
                PaymentLogger.log_payment_status_change(
                    self.reference, old_instance.status, self.status
                )
        super().save(*args, **kwargs)


class SnippePayout(models.Model):
    """Stores a payout disbursement record from the Snippe API (2026-01-25)."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        REVERSED = "reversed", "Reversed"

    class Channel(models.TextChoices):
        MOBILE = "mobile", "Mobile Money"
        BANK = "bank", "Bank Transfer"

    reference = models.CharField(max_length=100, unique=True)
    channel = models.CharField(max_length=20, choices=Channel.choices)
    provider = models.CharField(max_length=50, blank=True, null=True)
    amount = models.PositiveIntegerField(validators=[MinValueValidator(100)])
    fee_amount = models.PositiveIntegerField(default=0)
    total_amount = models.PositiveIntegerField(default=0)
    currency = models.CharField(
        max_length=10,
        default="TZS",
        validators=[CurrencyValidator.validate_currency],
    )
    recipient_name = models.CharField(max_length=100, validators=[validate_recipient_name])
    recipient_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[PhoneValidator.validate_phone],
    )
    recipient_bank = models.CharField(max_length=50, blank=True, null=True)
    recipient_account = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    narration = models.CharField(max_length=255, blank=True, null=True)
    external_reference = models.CharField(max_length=100, blank=True, null=True)
    idempotency_key = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        validators=[validate_idempotency_key],
    )
