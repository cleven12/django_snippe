"""Django Admin bulk actions for Snippe payments, payouts, and checkout sessions."""

from django.contrib import messages

from .logging import PaymentLogger, PayoutLogger, SessionLogger


def mark_payment_completed(modeladmin, request, queryset):
    """Mark selected pending or expired payments as completed."""
    count = 0
    for payment in queryset.filter(status__in=["pending", "expired"]):
        payment.status = payment.Status.COMPLETED
