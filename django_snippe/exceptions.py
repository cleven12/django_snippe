"""Structured exceptions for django-snippe aligned with Snippe API 2026-01-25."""

from typing import Optional


class SnippeException(Exception):
    """Base exception for all django-snippe errors."""

    default_code: int = 400
    default_error_code: str = "snippe_error"

    def __init__(
        self,
        message: str = "An error occurred with Snippe.",
        *,
        code: Optional[int] = None,
        error_code: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code if code is not None else self.default_code
        self.error_code = error_code if error_code is not None else self.default_error_code

    def to_dict(self) -> dict:
        """Serialize error into the standard Snippe 2026-01-25 error envelope."""
        return {
            "status": "error",
            "code": self.code,
            "error_code": self.error_code,
            "message": self.message,
        }


class SnippeConfigError(SnippeException):
    """Raised when required django-snippe settings are missing or invalid."""

    default_code = 500
    default_error_code = "configuration_error"


class SnippeValidationError(SnippeException):
    """Raised on HTTP 400 validation errors or malformed input."""

    default_code = 400
    default_error_code = "validation_error"


class SnippeAuthenticationError(SnippeException):
    """Raised on HTTP 401 when the API key is missing or invalid."""

    default_code = 401
    default_error_code = "unauthorized"


class SnippePermissionError(SnippeException):
    """Raised on HTTP 403 when the API key lacks the required scope."""

    default_code = 403
    default_error_code = "forbidden_scope"


class SnippeNotFoundError(SnippeException):
    """Raised on HTTP 404 when a requested payment, payout, or session does not exist."""

    default_code = 404
    default_error_code = "not_found"


class SnippeConflictError(SnippeException):
    """Raised on HTTP 409 when a duplicate reference or conflicting state occurs."""

    default_code = 409
    default_error_code = "conflict"


class SnippeIdempotencyError(SnippeException):
    """Raised on HTTP 422 when an idempotency key is reused with different parameters."""

    default_code = 422
    default_error_code = "idempotency_key_mismatch"


class SnippeRateLimitError(SnippeException):
    """Raised on HTTP 429 when the Snippe API rate limit is exceeded."""

    default_code = 429
    default_error_code = "rate_limit_exceeded"


class SnippeServerError(SnippeException):
    """Raised on HTTP 500 or 503 upstream Snippe server errors."""

    default_code = 500
    default_error_code = "internal_server_error"


class WebhookVerificationError(SnippeException):
    """Raised when X-Webhook-Signature HMAC verification fails."""

    default_code = 401
    default_error_code = "invalid_webhook_signature"


class WebhookPayloadError(SnippeException):
    """Raised when a webhook payload is malformed or missing required fields."""

    default_code = 400
    default_error_code = "invalid_webhook_payload"


class PaymentCreationError(SnippeException):
    """Raised when payment creation or push trigger fails."""

    default_code = 400
    default_error_code = "payment_creation_failed"


class PayoutCreationError(SnippeException):
    """Raised when payout disbursement creation fails."""

    default_code = 400
    default_error_code = "payout_creation_failed"


class SessionCreationError(SnippeException):
    """Raised when checkout session creation or cancellation fails."""
