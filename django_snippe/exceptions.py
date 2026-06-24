"""Custom exceptions for django-snippe."""


class SnippeException(Exception):
    """Base exception for all django-snippe errors."""
    pass


class WebhookVerificationError(SnippeException):
    """Raised when webhook signature verification fails."""
    pass


class WebhookPayloadError(SnippeException):
    """Raised when webhook payload is invalid or malformed."""
    pass


class PaymentCreationError(SnippeException):
    """Raised when payment creation fails."""
    pass


class PayoutCreationError(SnippeException):
    """Raised when payout creation fails."""
    pass
