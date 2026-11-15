# Usage Guide (Snippe API 2026-01-25)

Complete integration reference for `django-snippe` aligned with the official [Snippe API `2026-01-25` documentation](https://docs.snippe.sh/docs/2026-01-25).

## Architecture Overview

```text
Customer / Merchant App
   |
   v
PaymentHelper / PayoutHelper / SessionHelper  -->  Snippe API (https://api.snippe.sh)
   |                                                      |
   +-- SnippePayment / SnippePayout / SnippeSession       |
                                                          v
                                            Webhook (POST /payments/webhook/)
                                                          |
                                                          v
                                            HMAC-SHA256 Verification + Idempotency
                                                          |
                                                          v
                                            Update ORM Model + Dispatch Django Signal
```

## Django Settings Reference

| Setting | Required | Default | Description |
|---|---|---|---|
| `SNIPPE_API_KEY` | Yes | - | Your Snippe API key (`Bearer snp_...`) |
| `SNIPPE_WEBHOOK_SECRET` | Recommended | `None` | Webhook signing key used to verify `X-Webhook-Signature` |
| `SNIPPE_API_VERSION` | No | `"2026-01-25"` | Target Snippe API schema version |
| `SNIPPE_BASE_URL` | No | `"https://api.snippe.sh/api/v1"` | Override API base URL for local testing or staging |
| `SNIPPE_TIMEOUT` | No | `30.0` | HTTP request timeout in seconds |
| `SNIPPE_DEFAULT_CURRENCY` | No | `"TZS"` | Default transaction currency (`TZS`, `KES`, `UGX`) |
| `SNIPPE_MIN_PAYMENT_AMOUNT` | No | `500` | Minimum collection amount (500 TZS per 2026-01-25 spec) |
| `SNIPPE_MIN_PAYOUT_AMOUNT` | No | `5000` | Minimum disbursement amount (5,000 TZS per 2026-01-25 spec) |
| `SNIPPE_WEBHOOK_TOLERANCE` | No | `300` | Maximum allowed webhook timestamp age in seconds |
| `SNIPPE_WEBHOOK_RAISE_EXCEPTIONS` | No | `False` | Raise exceptions instead of returning HTTP 400/401 JSON responses |

## Accepting Payments (`/v1/payments`)

```python
from django_snippe.helpers import PaymentHelper

# 1. Mobile Money (USSD Push - min 500 TZS)
mobile_payment = PaymentHelper.create_mobile_payment(
    amount=5000,
    currency="TZS",
    phone_number="0712345678",
    customer_firstname="John",
    customer_lastname="Doe",
    customer_email="john@example.com",
    webhook_url="https://yourdomain.com/payments/webhook/",
    metadata={"order_id": "ORD-123"},
    idempotency_key="ord-123-mob",
)

# Re-trigger USSD push manually (POST /v1/payments/{reference}/push)
PaymentHelper.trigger_push(mobile_payment.reference, phone_number="255712345678")

# 2. Card Payment (returns payment_url for customer redirect)
card_payment = PaymentHelper.create_card_payment(
    amount=15000,
    currency="TZS",
    phone_number="0712345678",
    customer_firstname="Amina",
    customer_lastname="Yusuf",
    redirect_url="https://yourdomain.com/payments/success/",
    cancel_url="https://yourdomain.com/payments/cancel/",
    webhook_url="https://yourdomain.com/payments/webhook/",
)

# 3. Dynamic QR Payment (returns payment_qr_code and payment_token)
qr_payment = PaymentHelper.create_qr_payment(
    amount=10000,
    currency="TZS",
    phone_number="0712345678",
    customer_firstname="Baraka",
    customer_lastname="Mushi",
    webhook_url="https://yourdomain.com/payments/webhook/",
)

# 4. Sync Status, Search, and Check Account Balance
synced = PaymentHelper.sync_payment(mobile_payment.reference)
results = PaymentHelper.search_payments("0712345678", limit=20, offset=0)
balance = PaymentHelper.get_balance()
```

## Hosted Checkout Sessions (`/api/v1/sessions`)

```python
from django_snippe.helpers import SessionHelper

session = SessionHelper.create_checkout_session(
    amount=25000,
    currency="TZS",
    allow_custom_amount=False,
    allowed_methods=["mobile_money", "card"],
    customer={
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "phone": "+255781000000",
    },
    redirect_url="https://yourdomain.com/orders/complete/",
    webhook_url="https://yourdomain.com/payments/webhook/",
    metadata={"cart_id": "CART-99"},
)

# Redirect the customer to session.checkout_url
print(session.checkout_url)

# Cancel an active session if needed
SessionHelper.cancel_checkout_session(session.reference)
```
