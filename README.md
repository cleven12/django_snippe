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

```bash
pip install django-snippe
```

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

Use `get_client()` to get a ready-to-use Snippe client:

```python
from django_snippe.conf import get_client
from snippe import Customer

client = get_client()

# Mobile money payment
payment = client.create_mobile_payment(
    amount=5000,
    currency="TZS",
    phone_number="0712345678",
    customer=Customer(firstname="John", lastname="Doe"),
    webhook_url="https://yourdomain.com/payments/webhook/",
)
```

Save the record to your database:

```python
from django_snippe.models import SnippePayment

SnippePayment.objects.create(
    reference=payment.reference,
    payment_type="mobile",
    amount=5000,
    currency="TZS",
    phone_number="0712345678",
)
```

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
from django_snippe.conf import get_client

client = get_client()

payout = client.create_mobile_payout(
    amount=5000,
    recipient_name="Jane Doe",
    recipient_phone="255781000000",
    narration="Salary payment",
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
