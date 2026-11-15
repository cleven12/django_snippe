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
        "channel",
        "amount",
        "currency",
        "recipient_name",
        "status",
        "created_at",
    ]
    list_filter = ["status", "channel", "currency"]
    search_fields = ["reference", "recipient_name", "recipient_phone", "recipient_account"]
    readonly_fields = ["reference", "created_at", "updated_at"]
    ordering = ["-created_at"]
    actions = [
        mark_payout_completed,
        mark_payout_failed,
        retry_payout,
    ]


@admin.register(SnippeSession)
class SnippeSessionAdmin(admin.ModelAdmin):
    list_display = [
        "reference",
        "amount",
        "currency",
        "allow_custom_amount",
        "status",
        "created_at",
    ]
    list_filter = ["status", "currency", "allow_custom_amount"]
    search_fields = ["reference", "customer_name", "customer_email", "customer_phone"]
    readonly_fields = ["reference", "created_at", "updated_at"]
    ordering = ["-created_at"]
    actions = [cancel_selected_sessions]


@admin.register(SnippeWebhookEvent)
class SnippeWebhookEventAdmin(admin.ModelAdmin):
    list_display = ["delivery_id", "event_type", "reference", "processed", "created_at"]
    list_filter = ["event_type", "processed"]
    search_fields = ["delivery_id", "reference", "event_type"]
    readonly_fields = [
        "delivery_id",
        "event_type",
        "reference",
        "payload",
        "signature",
        "timestamp",
        "processed",
        "error_message",
        "created_at",
    ]
    ordering = ["-created_at"]
