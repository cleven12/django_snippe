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
