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
        currency: str,
        phone_number: str,
        customer_firstname: str,
        customer_lastname: str,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        customer_email: Optional[str] = None,
        callback_url: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> SnippePayment:
        """
        Create a mobile money payment (USSD push) and persist SnippePayment.

        Raises:
            PaymentCreationError: If input validation or the Snippe API request fails.
        """
        valid, errors = PaymentValidator.validate_payment_data(
            amount,
            currency,
            phone_number,
            "mobile",
            idempotency_key=idempotency_key,
        )
        if not valid:
            raise PaymentCreationError(f"Invalid payment data: {', '.join(errors)}")

        try:
            client = get_client()
            from snippe import Customer

            customer = Customer(
                firstname=customer_firstname,
                lastname=customer_lastname,
                email=customer_email,
            )
            call_kwargs: Dict[str, Any] = {
                "amount": amount,
                "currency": currency,
                "phone_number": phone_number,
                "customer": customer,
                "webhook_url": webhook_url,
            }
