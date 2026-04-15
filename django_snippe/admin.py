from django.contrib import admin

from .models import SnippePayment, SnippePayout


@admin.register(SnippePayment)
class SnippePaymentAdmin(admin.ModelAdmin):
    list_display = ["reference", "payment_type", "amount", "currency", "status", "created_at"]
    list_filter = ["status", "payment_type", "currency"]
    search_fields = ["reference", "phone_number"]
    readonly_fields = ["reference", "created_at", "updated_at"]
    ordering = ["-created_at"]


@admin.register(SnippePayout)
class SnippePayoutAdmin(admin.ModelAdmin):
    list_display = ["reference", "channel", "amount", "currency", "recipient_name", "status", "created_at"]
    list_filter = ["status", "channel", "currency"]
    search_fields = ["reference", "recipient_name", "recipient_phone"]
    readonly_fields = ["reference", "created_at", "updated_at"]
    ordering = ["-created_at"]
