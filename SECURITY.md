# Security Policy

## Supported Versions

`django-snippe` is currently in Beta (pre-1.0). Security fixes are made against
the latest release on the `main` branch only.

| Version | Supported |
| ------- | --------- |
| latest (`main`) | ✅ |
| < latest | ❌ |

## Reporting a Vulnerability

Please **do not** open a public issue for security vulnerabilities.

Instead, report it privately via
[GitHub Security Advisories](https://github.com/cleven12/django_snippe/security/advisories/new).

Include, where possible:

- A description of the vulnerability and its impact
- Steps to reproduce (a minimal repro is ideal)
- The version/commit affected

You should receive an initial response within a few days. Once a fix is
confirmed, we'll coordinate a disclosure timeline and credit the reporter
(unless you prefer to stay anonymous).

## Scope

In scope:

- `django_snippe/` package code — webhook signature verification, model/field
  validation, admin, signals
- GitHub Actions workflows in `.github/workflows/`

Out of scope:

- The upstream [Snippe API](https://docs.snippe.sh) itself and the
  [snippe-python-sdk](https://github.com/Neurotech-HQ/snippe-python-sdk) —
  report those upstream.
- Vulnerabilities requiring a misconfigured deployment (e.g. `SNIPPE_WEBHOOK_SECRET`
  intentionally left unset) — see the [webhook security notes](docs/USAGE.md)
  for the recommended configuration.

## Dependency & Code Scanning

This repo runs [Dependabot](.github/dependabot.yml) for dependency updates and
[CodeQL](.github/workflows/codeql.yml) for static analysis on every push and
pull request to `main`.
