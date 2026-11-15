# django-snippe

Production-ready Django integration for the [Snippe](https://snippe.sh) payment gateway (API version `2026-01-25`) supporting mobile money (M-Pesa, Airtel Money, Mixx by Yas, HaloPesa), card payments, dynamic QR codes, hosted checkout sessions, and instant disbursements across Tanzania, Kenya, and Uganda.

[![Tests](https://github.com/cleven12/django_snippe/actions/workflows/tests.yml/badge.svg)](https://github.com/cleven12/django_snippe/actions/workflows/tests.yml)
[![CodeQL](https://github.com/cleven12/django_snippe/actions/workflows/codeql.yml/badge.svg)](https://github.com/cleven12/django_snippe/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](pyproject.toml)
[![Django](https://img.shields.io/badge/django-4.2%20%7C%205.0%20%7C%205.1-0C4B33)](pyproject.toml)

---

## Key Features (Snippe API 2026-01-25)

- **Django ORM Models & Migrations**: `SnippePayment`, `SnippePayout`, `SnippeSession`, and `SnippeWebhookEvent` for complete transaction persistence and auditability.
- **Collections (`/v1/payments`)**: Mobile money USSD push (`mobile`), hosted card redirects (`card`), dynamic QR codes (`dynamic-qr`), manual USSD push retry (`/v1/payments/{reference}/push`), status sync, search, pagination, and account balance checks.
- **Hosted Checkout Sessions (`/api/v1/sessions`)**: Create, inspect, list, and cancel Snippe-hosted checkout sessions with fixed or custom amounts.
- **Disbursements / Payouts (`/v1/payouts/send`)**: Instant mobile money and Tanzanian bank transfer payouts (CRDB, NMB, NBC, ABSA, Equity, Stanbic, and 35+ supported banks) with fee calculation.
- **Webhook Verification & Idempotency**: `SnippeWebhookView` verifies `X-Webhook-Signature` HMAC-SHA256 signatures, parses `2026-01-25` nested `data.amount` (`{"value": 50000, "currency": "TZS"}`) payloads, deduplicates deliveries via `SnippeWebhookEvent`, and dispatches Django signals.
- **Django Admin & Bulk Actions**: Built-in ModelAdmin interfaces with search, status filtering, and bulk retry/void/cancel operations.
- **Fast Local Testing (Bun + TypeScript & Pytest)**: Includes a zero-dependency Bun + TypeScript mock Snippe `2026-01-25` contract server and end-to-end Django bridge test suite that runs locally in under two seconds without external API credentials.

## Installation

### Using pip

```bash
pip install django-snippe
```

### From Git

```bash
pip install git+https://github.com/cleven12/django_snippe.git
```

### Direct Package Copy (Without pip)

```bash
curl -L https://github.com/cleven12/django_snippe/archive/refs/heads/main.tar.gz | tar xz
```

Copy the `django_snippe/` directory into your Django project root alongside `manage.py`.

## Configuration

Add `django_snippe` to `INSTALLED_APPS` and configure your Snippe credentials in `settings.py`:

```python
INSTALLED_APPS = [
    ...,
    "django_snippe",
]

SNIPPE_API_KEY = "snp_live_your_api_key"
SNIPPE_WEBHOOK_SECRET = "whsec_your_signing_secret"
SNIPPE_API_VERSION = "2026-01-25"
SNIPPE_DEFAULT_CURRENCY = "TZS"
```

Run database migrations:

```bash
python manage.py migrate
```

Mount the webhook route in your project's `urls.py`:

```python
from django.urls import include, path

urlpatterns = [
