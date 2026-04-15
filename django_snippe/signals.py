from django.dispatch import Signal

# Payment signals
payment_completed = Signal()  # provides: payment (SnippePayment)
payment_failed = Signal()     # provides: payment (SnippePayment)
payment_expired = Signal()    # provides: payment (SnippePayment)
payment_voided = Signal()     # provides: payment (SnippePayment)

# Payout signals
payout_completed = Signal()   # provides: payout (SnippePayout)
payout_failed = Signal()      # provides: payout (SnippePayout)
