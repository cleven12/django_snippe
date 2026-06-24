# django-snippe

Django payment integration for Snippe.

Accept mobile money, card, and QR code payments across East Africa (Tanzania, Kenya, Uganda).

Built on [snippe-python-sdk](https://github.com/Neurotech-HQ/snippe-python-sdk).

---

**Features**

- Django models for payments and payouts
- Automatic webhook handling + signature verification
- Signals for payment lifecycle events
- Admin interface with filters
- High-level helpers for common operations
- Input validation + audit logging

---

## What it adds

- Django models + migrations for payments and payouts
- Secure webhook endpoint with signature verification
- Django signals for reacting to payment events
- Ready-to-use admin
- High-level helper classes (PaymentHelper, PayoutHelper)
- Validators and audit logging out of the box

### Request flow

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

## Installation

### From PyPI (recommended)

```bash
pip install django-snippe
```

### Alternative installation methods (no PyPI publish required)

**From Git (latest development version)**

```bash
pip install git+https://github.com/cleven12/django-snippe.git
```

Or a specific branch/tag:

```bash
pip install git+https://github.com/cleven12/django-snippe.git@feature/helpers
```

**From local source (editable development install)**

```bash
git clone https://github.com/cleven12/django-snippe.git
cd django-snippe
pip install -e .
```

**Manual / no-pip environments**

You can use the package without `pip` at all:

1. Download or clone the repository.
2. Copy the `django_snippe/` folder into your Django project directory (next to `manage.py`).
3. Add it to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...,
    "django_snippe",
]
```

This works because `django_snippe` is a standard Django application package.

You can also add the parent directory to `PYTHONPATH`:

```bash
export PYTHONPATH="/path/to/django-snippe:$PYTHONPATH"
```

### Basic setup

Add to `INSTALLED_APPS` and configure:

```python
# settings.py
INSTALLED_APPS = [
    ...
    "django_snippe",
]

SNIPPE_API_KEY = "snp_live_xxxx"
SNIPPE_WEBHOOK_SECRET = "your_webhook_secret"   # strongly recommended
```

Run migrations:

```bash
python manage.py migrate
```

## Wire up the webhook

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    ...
    path("payments/", include("django_snippe.urls")),
]
```

This registers: `POST /payments/webhook/`

Register this full URL in your Snippe dashboard.

## Creating payments (high level)

Use the built-in helpers:

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
```

Card and QR payments are also supported:

```python
card_payment = PaymentHelper.create_card_payment(
    amount=15000,
    currency="KES",
    customer_firstname="Amina",
    customer_lastname="Yusuf",
    webhook_url="https://...",
)
```

Low-level access is still available via `get_client()`.

## Reacting to events with signals

```python
from django.dispatch import receiver
from django_snippe.signals import payment_completed, payment_failed

@receiver(payment_completed)
def on_payment_completed(sender, payment, **kwargs):
    # payment is a SnippePayment instance
    # fulfill order, send receipt, etc.
    print("Payment succeeded:", payment.reference)

@receiver(payment_failed)
def on_payment_failed(sender, payment, **kwargs):
    print("Payment failed:", payment.reference)
```

### Available signals

| Signal                | Description                     |
|-----------------------|---------------------------------|
| payment_completed     | Payment succeeded               |
| payment_failed        | Payment declined or failed      |
| payment_expired       | Payment timed out               |
| payment_voided        | Payment cancelled               |
| payout_completed      | Payout completed                |
| payout_failed         | Payout failed                   |

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

## Supported currencies

| Currency | Country |
|---|---|
| TZS | Tanzania |
| KES | Kenya |
| UGX | Uganda |

## Publishing to PyPI (maintainers)

### Recommended: Trusted Publishers (no API token needed)

PyPI + TestPyPI support "Trusted Publishing" via GitHub OIDC. No tokens or passwords.

#### Step-by-step setup (TestPyPI first)

1. On TestPyPI, go to **Publishing** → "Add a new pending publisher"
2. Fill exactly:

   - **Project Name**: `django-snippe`
   - **Owner**: your GitHub username or org (see your repo URL)
   - **Repository name**: `django-snippe`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `testpypi`

3. In your **GitHub repository**:
   - Go to **Settings → Environments**
   - Create a new environment named **`testpypi`**

4. Push your code (including `.github/workflows/publish.yml`) to the default branch.

5. Trigger a publish:
   - GitHub → **Actions** tab → "Publish to PyPI" → **Run workflow**
   - Choose target: `testpypi`
   - Run

6. Check the run logs. If it succeeds, your project will appear at:
   https://test.pypi.org/project/django-snippe/

You can now install it for testing:

```bash
pip install --index-url https://test.pypi.org/simple/ django-snippe
```

Once comfortable, repeat the process on the real PyPI (use environment `pypi` and the same workflow).

### Testing uploads with TestPyPI

1. Create account at https://test.pypi.org
2. Go to Account Settings > API tokens
3. Create a token scoped to your project
4. Use it with twine:

```bash
python -m build
python -m twine upload --repository testpypi dist/*
```

Install test version:

```bash
pip install --index-url https://test.pypi.org/simple/ django-snippe
```

### Manual publish (once ready)

```bash
pip install build twine
python -m build
twine upload dist/*
```

## Status

Beta. The package builds cleanly, installs from source or wheel, and provides complete functionality.

Contributions welcome.

## License

MIT
