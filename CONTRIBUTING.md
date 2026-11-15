# Contributing to django-snippe

## Local Environment Setup

```bash
git clone https://github.com/cleven12/django_snippe.git
cd django_snippe
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests Locally

### 1. Fast Bun + TypeScript API Contract & Bridge Tests

The `tests_ts/` suite spins up an in-memory Snippe `2026-01-25` mock API server using `Bun.serve` and verifies all REST contracts, HMAC-SHA256 webhook signatures, error envelopes, repository hygiene, and end-to-end Django integration in under two seconds:

```bash
bun test
```

### 2. Python / Django Test Suite

