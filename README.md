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
