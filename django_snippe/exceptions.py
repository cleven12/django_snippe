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
