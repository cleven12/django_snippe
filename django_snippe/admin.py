"""Django Admin configuration for Snippe models."""

from django.contrib import admin

from .admin_actions import (
    cancel_selected_sessions,
    mark_payment_completed,
    mark_payment_failed,
    mark_payout_completed,
    mark_payout_failed,
    retry_payment,
    retry_payout,
    void_payment,
)
from .models import SnippePayment, SnippePayout, SnippeSession, SnippeWebhookEvent


@admin.register(SnippePayment)
class SnippePaymentAdmin(admin.ModelAdmin):
    list_display = ["reference", "payment_type", "amount", "currency", "status", "created_at"]
    list_filter = ["status", "payment_type", "currency"]
    search_fields = ["reference", "phone_number", "customer_email", "psp_reference"]
    readonly_fields = ["reference", "created_at", "updated_at"]
    ordering = ["-created_at"]
    actions = [
        mark_payment_completed,
        mark_payment_failed,
        retry_payment,
        void_payment,
    ]


@admin.register(SnippePayout)
class SnippePayoutAdmin(admin.ModelAdmin):
    list_display = [
        "reference",
