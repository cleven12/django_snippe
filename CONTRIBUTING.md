# Contributing

## Setup

```bash
git clone https://github.com/cleven12/django_snippe.git
cd django_snippe
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Running tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=django_snippe --cov-report=term-missing
```

Lint:

```bash
ruff check django_snippe tests
```

Tests use a minimal standalone Django settings module at `tests/settings.py` (SQLite in-memory DB) — no separate Django project is required.

## Pull requests

- Keep changes focused; one concern per PR.
- Add or update tests for behavior changes.
- CI (`.github/workflows/tests.yml`) must pass: lint, test matrix (Python 3.9–3.13 × Django 4.2–5.1), and a package build check.

## Publishing to PyPI

See [docs/PUBLISHING.md](docs/PUBLISHING.md) — maintainers only.
