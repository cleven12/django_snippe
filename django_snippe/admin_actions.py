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
        payment.status = payment.Status.FAILED
        payment.save()
        count += 1
    messages.success(request, f"Marked {count} payment(s) as failed")


mark_payment_failed.short_description = "Mark selected payments as failed"


def retry_payment(modeladmin, request, queryset):
    """Retry failed payments by resetting their status to pending."""
    count = 0
    for payment in queryset.filter(status="failed"):
        payment.status = payment.Status.PENDING
        payment.save()
        count += 1
        PaymentLogger.log_payment_status_change(
            payment.reference, "failed", "pending", reason="Manual retry from admin"
        )
    messages.success(request, f"Retried {count} payment(s)")


retry_payment.short_description = "Retry failed payments (reset to pending)"


def void_payment(modeladmin, request, queryset):
    """Void selected pending payments."""
    count = 0
    for payment in queryset.filter(status="pending"):
        payment.status = payment.Status.VOIDED
        payment.save()
        count += 1
    messages.warning(request, f"Voided {count} payment(s)")


void_payment.short_description = "Void selected payments"
