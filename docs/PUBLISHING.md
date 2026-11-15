# Publishing Guide (Maintainers)

## Trusted Publishing via GitHub OIDC (Recommended)

PyPI and TestPyPI support Trusted Publishing via GitHub Actions OIDC without long-lived API tokens.

### Setup Steps (TestPyPI First)

1. On TestPyPI, navigate to **Publishing** and add a new pending publisher:
   - **Project Name**: `django-snippe`
   - **Owner**: `cleven12`
   - **Repository name**: `django_snippe`
