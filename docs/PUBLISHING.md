# Publishing (maintainers)

## Recommended: Trusted Publishers (no API token needed)

PyPI + TestPyPI support "Trusted Publishing" via GitHub OIDC. No tokens or passwords.

### Step-by-step setup (TestPyPI first)

1. On TestPyPI, go to **Publishing** → "Add a new pending publisher"
2. Fill exactly:
   - **Project Name**: `django-snippe`
   - **Owner**: your GitHub username or org (see your repo URL)
   - **Repository name**: `django_snippe`
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

Install it for testing:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ django-snippe
```

> `--extra-index-url` is required because dependencies (Django, snippe SDK, etc.) live on the real PyPI, not TestPyPI.

Once comfortable, repeat the process on the real PyPI (use environment `pypi` and the same workflow).

**Important gotchas (learned the hard way):**

- "Repository name" in the publisher form **must exactly match** your GitHub repo slug (e.g. `django_snippe`, not `django-snippe`).
- Run the workflow from a branch that contains the current `publish.yml` (use the branch selector in "Run workflow").
- The GitHub Environment (`testpypi` / `pypi`) must exist under repo Settings → Environments before the first run.

## Manual publish (token-based, fallback)

```bash
pip install build twine
python -m build
twine upload dist/*
```

Testing uploads against TestPyPI specifically:

```bash
python -m build
python -m twine upload --repository testpypi dist/*
```

## Status

Beta. TestPyPI publishing verified using Trusted Publishers. The package builds cleanly, installs from source or wheel, and provides complete functionality. Public PyPI release is on hold pending further review — install from Git or source in the meantime (see README).
