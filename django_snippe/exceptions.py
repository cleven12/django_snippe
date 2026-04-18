"""Custom exceptions for django-snippe."""


class SnippeException(Exception):
    """Base exception for all django-snippe errors."""

    pass


class SnippeConfigError(SnippeException):
    """Raised when django-snippe is misconfigured."""

    pass


class SnippeWebhookError(SnippeException):
    """Base exception for webhook-related errors."""

    pass


class WebhookVerificationError(SnippeWebhookError):
    """Raised when webhook signature verification fails."""

    pass


class WebhookPayloadError(SnippeWebhookError):
    """Raised when webhook payload is invalid or malformed."""

    pass


class SnippePaymentError(SnippeException):
    """Base exception for payment-related errors."""

    pass


class PaymentNotFoundError(SnippePaymentError):
    """Raised when a payment record cannot be found."""

    pass


class PaymentCreationError(SnippePaymentError):
    """Raised when payment creation fails in the SDK."""

    pass


class SnippePayoutError(SnippeException):
    """Base exception for payout-related errors."""

    pass


class PayoutNotFoundError(SnippePayoutError):
    """Raised when a payout record cannot be found."""

    pass


class PayoutCreationError(SnippePayoutError):
    """Raised when payout creation fails in the SDK."""

    pass
