from django.db import models


class SnippePayment(models.Model):
    """Stores a payment record from the Snippe API."""

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
    amount = models.PositiveIntegerField()
    currency = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_url = models.URLField(blank=True, null=True)
    payment_qr_code = models.TextField(blank=True, null=True)
    payment_token = models.CharField(max_length=100, blank=True, null=True)
    webhook_url = models.URLField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"{self.reference} — {self.status} ({self.amount} {self.currency})"


class SnippePayout(models.Model):
    """Stores a payout record from the Snippe API."""

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
    amount = models.PositiveIntegerField()
    currency = models.CharField(max_length=10, default="TZS")
    recipient_name = models.CharField(max_length=100)
    recipient_phone = models.CharField(max_length=20, blank=True, null=True)
    recipient_bank = models.CharField(max_length=50, blank=True, null=True)
    recipient_account = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    narration = models.CharField(max_length=255, blank=True, null=True)
    failure_reason = models.TextField(blank=True, null=True)
    webhook_url = models.URLField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Payout"
        verbose_name_plural = "Payouts"

    def __str__(self):
        return f"{self.reference} — {self.status} ({self.amount} {self.currency})"
