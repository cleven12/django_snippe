# django-snippe

Django integration for the [Snippe](https://snippe.sh) payment gateway — mobile money, cards, and QR payments for Tanzania, Kenya, and Uganda.

[![Tests](https://github.com/cleven12/django_snippe/actions/workflows/tests.yml/badge.svg)](https://github.com/cleven12/django_snippe/actions/workflows/tests.yml)
[![CodeQL](https://github.com/cleven12/django_snippe/actions/workflows/codeql.yml/badge.svg)](https://github.com/cleven12/django_snippe/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](pyproject.toml)
[![Django](https://img.shields.io/badge/django-4.2%20%7C%205.0%20%7C%205.1-0C4B33)](pyproject.toml)

---

## ✨ Features

- 🏦 Django models + migrations for payments and payouts
- 🔐 Webhook endpoint with signature verification
- 📡 Signals for payment/payout lifecycle events
- 🛠️ Admin interface with filters and search
- ⚡ High-level helpers (`PaymentHelper`, `PayoutHelper`)
- ✅ Input validation + audit logging

## 📦 Install

**pip**

```bash
pip install django-snippe
```

**From source (Linux / macOS / Windows)**

```bash
pip install git+https://github.com/cleven12/django_snippe.git
```

**No pip** — download the package folder directly:

```bash
# Linux / macOS
curl -L https://github.com/cleven12/django_snippe/archive/refs/heads/main.tar.gz | tar xz

# Windows (PowerShell)
Invoke-WebRequest -Uri https://github.com/cleven12/django_snippe/archive/refs/heads/main.zip -OutFile django_snippe.zip; Expand-Archive django_snippe.zip
```

Then copy the `django_snippe/` folder into your Django project (next to `manage.py`).

## 🔌 Plug into your project

```python
# settings.py
INSTALLED_APPS = [
    ...,
    "django_snippe",
]

SNIPPE_API_KEY = "snp_live_xxxx"
SNIPPE_WEBHOOK_SECRET = "your_webhook_secret"  # strongly recommended
```

```bash
python manage.py migrate
```

```python
# urls.py
urlpatterns = [
    ...,
    path("payments/", include("django_snippe.urls")),  # -> POST /payments/webhook/
]
```

## 🚀 Usage

```python
from django_snippe.helpers import PaymentHelper

payment = PaymentHelper.create_mobile_payment(
    amount=5000,
    currency="TZS",
    phone_number="0712345678",
    customer_firstname="John",
    customer_lastname="Doe",
    webhook_url="https://yourdomain.com/payments/webhook/",
)
```

```python
from django.dispatch import receiver
from django_snippe.signals import payment_completed

@receiver(payment_completed)
def on_payment_completed(sender, payment, **kwargs):
    print("Payment succeeded:", payment.reference)
```

Full API reference, settings table, and advanced usage: see [docs/USAGE.md](docs/USAGE.md).

## 🧪 Development & testing

```bash
git clone https://github.com/cleven12/django_snippe.git
cd django_snippe
pip install -e ".[dev]"
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md).

## 🤝 Community

PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md).

Found a security issue? Please read [SECURITY.md](SECURITY.md) — report privately, not as a public issue.

## 📄 License

MIT © [cleven](https://github.com/cleven12) — see [LICENSE](LICENSE)
