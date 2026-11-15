"""Django signals dispatched on Snippe payment, payout, and session lifecycle events."""

from django.dispatch import Signal

# Payment signals (provides: payment=SnippePayment)
payment_completed = Signal()
payment_failed = Signal()
payment_expired = Signal()
payment_voided = Signal()

# Payout signals (provides: payout=SnippePayout)
payout_completed = Signal()
payout_failed = Signal()
payout_reversed = Signal()

# Session signals (provides: session=SnippeSession)
session_completed = Signal()
session_expired = Signal()
session_cancelled = Signal()
