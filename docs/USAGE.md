# Usage guide

Full reference for `django-snippe`. See the [README](../README.md) for a quick start.

## Request flow

```
Customer
   |
   v
create_mobile_payment()  -->  Snippe API
   |                             |
   +-- SnippePayment saved       |
                                 v
                          Webhook (POST /payments/webhook/)
                                 |
                                 v
                          Update status + dispatch signal
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `SNIPPE_API_KEY` | Yes | — | Your Snippe API key |
| `SNIPPE_WEBHOOK_SECRET` | No | `None` | Webhook signing secret for verification |
| `SNIPPE_BASE_URL` | No | Snippe default | Override API base URL (useful for testing) |
| `SNIPPE_TIMEOUT` | No | `30.0` | Request timeout in seconds |

## Creating payments

```python
from django_snippe.helpers import PaymentHelper

# Mobile money (USSD push)
payment = PaymentHelper.create_mobile_payment(
    amount=5000,
    currency="TZS",
    phone_number="0712345678",
    customer_firstname="John",
    customer_lastname="Doe",
    webhook_url="https://yourdomain.com/payments/webhook/",
    metadata={"order_id": "ORD-123"},
)

print(payment.reference, payment.status)

# Card
card_payment = PaymentHelper.create_card_payment(
    amount=15000,
    currency="KES",
    customer_firstname="Amina",
    customer_lastname="Yusuf",
    webhook_url="https://...",
)
```

Low-level access is still available via `django_snippe.conf.get_client()`.

## Payment types

- **Mobile Money** — USSD push (Airtel, Mixx by Yas, HaloPesa)
- **Card** — returns a `payment_url` to redirect the customer
- **QR Code** — returns a QR code for the customer to scan

## Payouts

```python
from django_snippe.helpers import PayoutHelper

payout = PayoutHelper.create_mobile_payout(
    amount=5000,
    currency="TZS",
    recipient_name="Jane Doe",
    recipient_phone="255781000000",
    narration="Salary payment",
    webhook_url="https://yourdomain.com/payments/webhook/",
)
```

## Reacting to events with signals

```python
from django.dispatch import receiver
from django_snippe.signals import payment_completed, payment_failed

@receiver(payment_completed)
def on_payment_completed(sender, payment, **kwargs):
    print("Payment succeeded:", payment.reference)

@receiver(payment_failed)
def on_payment_failed(sender, payment, **kwargs):
    print("Payment failed:", payment.reference)
```

### Available signals

| Signal                | Description                     |
|-----------------------|----------------------------------|
| `payment_completed`   | Payment succeeded               |
| `payment_failed`      | Payment declined or failed      |
| `payment_expired`     | Payment timed out               |
| `payment_voided`      | Payment cancelled               |
| `payout_completed`    | Payout completed                |
| `payout_failed`       | Payout failed                   |

## Supported currencies

| Currency | Country |
|---|---|
| TZS | Tanzania |
| KES | Kenya |
| UGX | Uganda |

## Manual / no-pip install

You can use the package without `pip` at all:

1. Download or clone the repository.
2. Copy the `django_snippe/` folder into your Django project directory (next to `manage.py`).
3. Add it to `INSTALLED_APPS` (see README).

This works because `django_snippe` is a standard Django application package. You can also add the parent directory to `PYTHONPATH`:

```bash
export PYTHONPATH="/path/to/django-snippe:$PYTHONPATH"
```
