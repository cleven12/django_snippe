# django-snippe

Django integration for the [Snippe Payment API](https://snippe.sh) — accept mobile money, card, and QR code payments in East Africa, directly from your Django project.

> Built on top of the official [snippe-python-sdk](https://github.com/Neurotech-HQ/snippe-python-sdk).

## What it adds on top of the SDK

- Django models to store payments and payouts in your database
- Webhook view that verifies, parses, and saves incoming events automatically
- Django signals so your app can react to payment events (`payment_completed`, `payment_failed`, etc.)
- Django admin panel support for payments and payouts
- Settings integration via `settings.py`

## Installation


>><del>pip install django-snippe</del>


Add to `INSTALLED_APPS` and run migrations:

```python
# settings.py
INSTALLED_APPS = [
    ...
    "django_snippe",
]

SNIPPE_API_KEY = "snp_live_xxxx"
SNIPPE_WEBHOOK_SECRET = "your_webhook_secret"  # optional but recommended
```

```bash
python manage.py migrate
```

## Wire up the webhook URL

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    ...
    path("payments/", include("django_snippe.urls")),
]
```

This exposes: `POST /payments/webhook/`

Set this URL in your Snippe dashboard so Snippe can send you payment events.

## Creating payments

Use the service helpers to call the Snippe API and save the record to your database in one step:

```python
from django_snippe.services import create_mobile_payment, create_card_payment, create_qr_payment
from snippe import Customer

customer = Customer(firstname="John", lastname="Doe")

# Mobile money payment (USSD push)
payment = create_mobile_payment(
    amount=5000,
    currency="TZS",
    phone_number="0712345678",
    customer=customer,
    webhook_url="https://yourdomain.com/payments/webhook/",
)
# payment is a SnippePayment model instance, already saved to the database

# Card payment — redirect the customer to payment.payment_url
payment = create_card_payment(
    amount=5000,
    currency="TZS",
    phone_number="0712345678",
    customer=customer,
    callback_url="https://yourdomain.com/payments/done/",
    webhook_url="https://yourdomain.com/payments/webhook/",
)

# QR code payment — display payment.payment_qr_code to the customer
payment = create_qr_payment(
    amount=5000,
    currency="TZS",
    phone_number="0712345678",
    customer=customer,
    webhook_url="https://yourdomain.com/payments/webhook/",
)
```

All helpers return a `SnippePayment` instance. If you need lower-level control, `get_client()` from `django_snippe.conf` still gives you direct SDK access.

## Reacting to payment events with signals

```python
from django.dispatch import receiver
from django_snippe.signals import payment_completed, payment_failed

@receiver(payment_completed)
def on_payment_completed(sender, payment, **kwargs):
    # payment is a SnippePayment model instance
    print(f"Payment {payment.reference} completed!")
    # fulfill the order, send confirmation email, etc.

@receiver(payment_failed)
def on_payment_failed(sender, payment, **kwargs):
    print(f"Payment {payment.reference} failed")
    # notify the customer
```

## Available signals

| Signal | When it fires |
|---|---|
| `payment_completed` | Payment successful |
| `payment_failed` | Payment declined or failed |
| `payment_expired` | Payment timed out |
| `payment_voided` | Payment cancelled |
| `payout_completed` | Payout sent successfully |
| `payout_failed` | Payout failed |

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `SNIPPE_API_KEY` | Yes | — | Your Snippe API key |
| `SNIPPE_WEBHOOK_SECRET` | No | `None` | Webhook signing secret for verification |
| `SNIPPE_BASE_URL` | No | Snippe default | Override API base URL (useful for testing) |
| `SNIPPE_TIMEOUT` | No | `30.0` | Request timeout in seconds |

## Payment types

Supports all payment types from the Snippe SDK:

- **Mobile Money** — USSD push (Airtel, Mixx by Yas, HaloPesa)
- **Card** — returns a `payment_url` to redirect the customer
- **QR Code** — returns a QR code for the customer to scan

## Payouts

```python
from django_snippe.services import create_mobile_payout, create_bank_payout

# Mobile money payout
payout = create_mobile_payout(
    amount=5000,
    recipient_name="Jane Doe",
    recipient_phone="255781000000",
    narration="Salary payment",
    webhook_url="https://yourdomain.com/payments/webhook/",
)
# payout is a SnippePayout model instance, already saved to the database

# Bank transfer payout
payout = create_bank_payout(
    amount=50000,
    recipient_name="Jane Doe",
    recipient_bank="CRDB",
    recipient_account="0150123456789",
    narration="Invoice payment",
    webhook_url="https://yourdomain.com/payments/webhook/",
)
```

## Supported currencies

| Currency | Country |
|---|---|
| TZS | Tanzania |
| KES | Kenya |
| UGX | Uganda |

## Status

This is an early-stage boilerplate. Contributions are welcome.

## License

MIT
