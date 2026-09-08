"""Minimal Django settings for running the django_snippe test suite."""

SECRET_KEY = "test-secret-key"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django_snippe",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

USE_TZ = True

ROOT_URLCONF = "tests.urls"

SNIPPE_API_KEY = "snp_test_dummy_key"
SNIPPE_WEBHOOK_SECRET = "test_webhook_secret"
