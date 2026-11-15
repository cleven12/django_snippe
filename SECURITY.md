# Security Policy

## Supported Versions

`django-snippe` supports security fixes on the latest release and the `main` branch.

| Version | Supported |
| ------- | --------- |
| 1.0.x (`main`) | Yes |
| < 1.0.0 | No |

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead, report vulnerabilities privately via
[GitHub Security Advisories](https://github.com/cleven12/django_snippe/security/advisories/new).

Include, where possible:

- A clear description of the vulnerability and its potential impact
- Steps to reproduce or a minimal proof of concept
- The version or commit hash affected

You will receive an initial response within 72 hours. Once a fix is verified, we will coordinate disclosure and credit the reporter (unless anonymity is requested).

## Scope

In scope:

- `django_snippe/` package code: `X-Webhook-Signature` HMAC-SHA256 verification, replay protection, idempotency deduplication, model/field validators, Django admin actions, and signals
- Local test harness in `tests/` and `tests_ts/`
- GitHub Actions workflows in `.github/workflows/`

Out of scope:

- The upstream [Snippe API](https://docs.snippe.sh/docs/2026-01-25) and [snippe-python-sdk](https://github.com/Neurotech-HQ/snippe-python-sdk)
- Deployments where `SNIPPE_WEBHOOK_SECRET` is intentionally omitted in production

## Automated Scanning

This repository runs [Dependabot](.github/dependabot.yml) for dependency updates and [CodeQL](.github/workflows/codeql.yml) static analysis on pushes and pull requests to `main`.
