"""Django integration for the Snippe payment gateway."""

from .exceptions import (
    SnippeException,
    SnippeConfigError,
    SnippeWebhookError,
    WebhookVerificationError,
    WebhookPayloadError,
    SnippePaymentError,
    PaymentNotFoundError,
    PaymentCreationError,
    SnippePayoutError,
    PayoutNotFoundError,
    PayoutCreationError,
)

default_app_config = "django_snippe.apps.DjangoSnippeConfig"

__all__ = [
    "SnippeException",
    "SnippeConfigError",
    "SnippeWebhookError",
    "WebhookVerificationError",
    "WebhookPayloadError",
    "SnippePaymentError",
    "PaymentNotFoundError",
    "PaymentCreationError",
    "SnippePayoutError",
    "PayoutNotFoundError",
    "PayoutCreationError",
]
