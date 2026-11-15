"""Structured exceptions for django-snippe aligned with Snippe API 2026-01-25."""

from typing import Optional


class SnippeException(Exception):
    """Base exception for all django-snippe errors."""

    default_code: int = 400
    default_error_code: str = "snippe_error"

    def __init__(
