"""Django signals dispatched on Snippe payment, payout, and session lifecycle events."""

from django.dispatch import Signal

# Payment signals (provides: payment=SnippePayment)
payment_completed = Signal()
