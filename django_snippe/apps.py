from django.apps import AppConfig


class DjangoSnippeConfig(AppConfig):
    name = "django_snippe"
    verbose_name = "Snippe Payments"

    def ready(self):
        from . import signals  # noqa: F401
