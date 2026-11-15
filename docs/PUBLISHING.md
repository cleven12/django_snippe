# Publishing Guide (Maintainers)

## Trusted Publishing via GitHub OIDC (Recommended)

PyPI and TestPyPI support Trusted Publishing via GitHub Actions OIDC without long-lived API tokens.

### Setup Steps (TestPyPI First)

1. On TestPyPI, navigate to **Publishing** and add a new pending publisher:
   - **Project Name**: `django-snippe`
   - **Owner**: `cleven12`
   - **Repository name**: `django_snippe`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `testpypi`
2. In the GitHub repository settings under **Settings -> Environments**, create an environment named `testpypi`.
3. Push `.github/workflows/publish.yml` to `main`.
4. Trigger the workflow from the **Actions** tab (`Publish to PyPI` -> `Run workflow` -> `testpypi`).
5. Verify installation from TestPyPI:
