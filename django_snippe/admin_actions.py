"""Django Admin bulk actions for Snippe payments, payouts, and checkout sessions."""

from django.contrib import messages

from .logging import PaymentLogger, PayoutLogger, SessionLogger


def mark_payment_completed(modeladmin, request, queryset):
    """Mark selected pending or expired payments as completed."""
    count = 0
    for payment in queryset.filter(status__in=["pending", "expired"]):
        payment.status = payment.Status.COMPLETED
        payment.save()
        count += 1
    messages.success(request, f"Marked {count} payment(s) as completed")


mark_payment_completed.short_description = "Mark selected payments as completed"


def mark_payment_failed(modeladmin, request, queryset):
    """Mark selected pending payments as failed."""
    count = 0
    for payment in queryset.filter(status="pending"):
