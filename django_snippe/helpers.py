"""High-level helper classes for Snippe payments, payouts, and hosted checkout sessions."""

from typing import Any, Dict, List, Optional, Sequence

from . import services
from .conf import get_client
from .exceptions import PaymentCreationError, PayoutCreationError, SessionCreationError
from .logging import PaymentLogger, PayoutLogger, SessionLogger
from .models import SnippePayment, SnippePayout, SnippeSession
from .validators import PaymentValidator, PayoutValidator, SessionValidator


class PaymentHelper:
    """High-level helper methods for Snippe payment collection operations."""

    @staticmethod
    def create_mobile_payment(
        amount: int,
