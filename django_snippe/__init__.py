"""Django integration for the Snippe payment gateway (API version 2026-01-25)."""

from .__version__ import API_VERSION, __version__
from .exceptions import (
    PaymentCreationError,
    PayoutCreationError,
    SessionCreationError,
    SnippeAuthenticationError,
    SnippeConfigError,
    SnippeConflictError,
    SnippeException,
    SnippeIdempotencyError,
    SnippeNotFoundError,
    SnippePermissionError,
    SnippeRateLimitError,
    SnippeServerError,
    SnippeValidationError,
    WebhookPayloadError,
    WebhookVerificationError,
)

__all__ = [
    "__version__",
    "API_VERSION",
