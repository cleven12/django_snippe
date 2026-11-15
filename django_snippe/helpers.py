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
            if callback_url is not None:
                call_kwargs["callback_url"] = callback_url
            if metadata is not None:
                call_kwargs["metadata"] = metadata
            if idempotency_key is not None:
                call_kwargs["idempotency_key"] = idempotency_key

            api_payment = client.create_mobile_payment(**call_kwargs)

            payment = SnippePayment.objects.create(
                reference=api_payment.reference,
                payment_type=SnippePayment.PaymentType.MOBILE,
                amount=amount,
                currency=currency,
                phone_number=phone_number,
                status=getattr(api_payment, "status", None)
                if isinstance(getattr(api_payment, "status", None), str)
                else SnippePayment.Status.PENDING,
                callback_url=callback_url,
                webhook_url=webhook_url,
                customer_firstname=customer_firstname,
                customer_lastname=customer_lastname,
                customer_email=customer_email,
                idempotency_key=idempotency_key,
                metadata=metadata or {},
            )

            PaymentLogger.log_payment_created(
                payment.reference, "mobile", amount, currency, phone_number
            )
            return payment

        except Exception as exc:
            PaymentLogger.log_payment_failed(phone_number, str(exc))
            raise PaymentCreationError(f"Failed to create mobile payment: {exc}") from exc

    @staticmethod
    def create_card_payment(
        amount: int,
        currency: str,
        customer_firstname: str,
        customer_lastname: str,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        phone_number: str = "",
        customer_email: Optional[str] = None,
        redirect_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        callback_url: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> SnippePayment:
        """
        Create a card payment record and return SnippePayment with payment_url.

        Raises:
            PaymentCreationError: If input validation or the Snippe API request fails.
        """
        valid, errors = PaymentValidator.validate_payment_data(
            amount,
            currency,
            phone_number or "0712345678",
            "card",
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
                "customer": customer,
                "webhook_url": webhook_url,
            }
            if phone_number:
                call_kwargs["phone_number"] = phone_number
            if redirect_url is not None:
                call_kwargs["redirect_url"] = redirect_url
            if cancel_url is not None:
                call_kwargs["cancel_url"] = cancel_url
            if callback_url is not None:
                call_kwargs["callback_url"] = callback_url
            if metadata is not None:
                call_kwargs["metadata"] = metadata
            if idempotency_key is not None:
                call_kwargs["idempotency_key"] = idempotency_key

            api_payment = client.create_card_payment(**call_kwargs)

            payment = SnippePayment.objects.create(
                reference=api_payment.reference,
                payment_type=SnippePayment.PaymentType.CARD,
                amount=amount,
                currency=currency,
                phone_number=phone_number,
                payment_url=getattr(api_payment, "payment_url", None),
                callback_url=redirect_url or callback_url,
                webhook_url=webhook_url,
                customer_firstname=customer_firstname,
                customer_lastname=customer_lastname,
                customer_email=customer_email,
                idempotency_key=idempotency_key,
                metadata=metadata or {},
            )

            PaymentLogger.log_payment_created(
                payment.reference, "card", amount, currency, customer_firstname
            )
            return payment

        except Exception as exc:
            PaymentLogger.log_payment_failed(customer_firstname, str(exc))
            raise PaymentCreationError(f"Failed to create card payment: {exc}") from exc

    @staticmethod
    def create_qr_payment(
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
        Create a dynamic QR code payment and persist SnippePayment.

        Raises:
            PaymentCreationError: If input validation or the Snippe API request fails.
        """
        valid, errors = PaymentValidator.validate_payment_data(
            amount,
            currency,
            phone_number or "0712345678",
            "dynamic-qr",
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
            if callback_url is not None:
                call_kwargs["callback_url"] = callback_url
            if metadata is not None:
                call_kwargs["metadata"] = metadata
            if idempotency_key is not None:
                call_kwargs["idempotency_key"] = idempotency_key

            api_payment = client.create_qr_payment(**call_kwargs)

            payment = SnippePayment.objects.create(
                reference=api_payment.reference,
                payment_type=SnippePayment.PaymentType.QR,
                amount=amount,
                currency=currency,
                phone_number=phone_number,
                payment_qr_code=getattr(api_payment, "payment_qr_code", None),
                payment_token=getattr(api_payment, "payment_token", None),
                callback_url=callback_url,
                webhook_url=webhook_url,
                customer_firstname=customer_firstname,
                customer_lastname=customer_lastname,
                customer_email=customer_email,
                idempotency_key=idempotency_key,
                metadata=metadata or {},
            )

            PaymentLogger.log_payment_created(
                payment.reference, "dynamic-qr", amount, currency, phone_number
            )
            return payment

        except Exception as exc:
            PaymentLogger.log_payment_failed(phone_number, str(exc))
            raise PaymentCreationError(f"Failed to create QR payment: {exc}") from exc

    @staticmethod
    def trigger_push(reference: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """Trigger a manual USSD push for an existing payment reference."""
        try:
            result = services.trigger_payment_push(reference, phone_number=phone_number)
            PaymentLogger.log_payment_push_triggered(reference, phone_number=phone_number)
            return result
        except Exception as exc:
