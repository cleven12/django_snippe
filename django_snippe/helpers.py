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
            PaymentLogger.log_payment_failed(reference, str(exc))
            raise PaymentCreationError(
                f"Failed to trigger USSD push for {reference}: {exc}"
            ) from exc

    @staticmethod
    def sync_payment(reference: str) -> SnippePayment:
        """Synchronize local SnippePayment status with the upstream Snippe API."""
        return services.sync_payment_status(reference)

    @staticmethod
    def search_payments(query: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search payments via the Snippe API search endpoint."""
        return services.search_payments(query=query, limit=limit, offset=offset)

    @staticmethod
    def get_balance() -> Any:
        """Fetch current Snippe merchant balance."""
        return services.get_account_balance()

    @staticmethod
    def get_payment_by_reference(reference: str) -> Optional[SnippePayment]:
        """Look up a local SnippePayment by its reference."""
        return SnippePayment.objects.filter(reference=reference).first()

    @staticmethod
    def get_pending_payments(limit: int = 100) -> List[SnippePayment]:
        """Return up to limit pending payments."""
        return list(SnippePayment.objects.filter(status=SnippePayment.Status.PENDING)[:limit])

    @staticmethod
    def get_failed_payments(limit: int = 100) -> List[SnippePayment]:
        """Return up to limit failed payments."""
        return list(SnippePayment.objects.filter(status=SnippePayment.Status.FAILED)[:limit])


class PayoutHelper:
    """High-level helper methods for Snippe payout disbursement operations."""

    @staticmethod
    def create_mobile_payout(
        amount: int,
        currency: str,
        recipient_name: str,
        recipient_phone: str,
        narration: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> SnippePayout:
        """
        Create a mobile money payout and persist SnippePayout.

        Raises:
            PayoutCreationError: If input validation or the Snippe API request fails.
        """
        valid, errors = PayoutValidator.validate_payout_data(
            amount,
            currency,
            "mobile",
            recipient_name,
            recipient_phone,
            idempotency_key=idempotency_key,
        )
        if not valid:
            raise PayoutCreationError(f"Invalid payout data: {', '.join(errors)}")

        try:
            client = get_client()
            call_kwargs: Dict[str, Any] = {
                "amount": amount,
                "currency": currency,
                "recipient_name": recipient_name,
                "recipient_phone": recipient_phone,
                "narration": narration,
                "webhook_url": webhook_url,
            }
            if metadata is not None:
                call_kwargs["metadata"] = metadata
            if idempotency_key is not None:
                call_kwargs["idempotency_key"] = idempotency_key

            try:
                api_payout = client.create_mobile_payout(**call_kwargs)
            except TypeError:
                call_kwargs.pop("currency", None)
                api_payout = client.create_mobile_payout(**call_kwargs)

            payout = SnippePayout.objects.create(
                reference=api_payout.reference,
                channel=SnippePayout.Channel.MOBILE,
                amount=amount,
                currency=currency,
                recipient_name=recipient_name,
                recipient_phone=recipient_phone,
                narration=narration,
                idempotency_key=idempotency_key,
                webhook_url=webhook_url,
                metadata=metadata or {},
            )

            PayoutLogger.log_payout_created(
                payout.reference, "mobile", amount, currency, recipient_name
            )
            return payout

        except Exception as exc:
            PayoutLogger.log_payout_failed(recipient_phone, str(exc))
            raise PayoutCreationError(f"Failed to create mobile payout: {exc}") from exc

    @staticmethod
    def create_bank_payout(
        amount: int,
        currency: str,
        recipient_name: str,
        recipient_bank: str,
        recipient_account: str,
        narration: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> SnippePayout:
        """
        Create a bank transfer payout and persist SnippePayout.

        Raises:
            PayoutCreationError: If input validation or the Snippe API request fails.
        """
        valid, errors = PayoutValidator.validate_payout_data(
            amount,
            currency,
            "bank",
            recipient_name,
            recipient_bank=recipient_bank,
            recipient_account=recipient_account,
            idempotency_key=idempotency_key,
        )
        if not valid:
            raise PayoutCreationError(f"Invalid payout data: {', '.join(errors)}")

        try:
            client = get_client()
            call_kwargs: Dict[str, Any] = {
                "amount": amount,
                "recipient_name": recipient_name,
                "recipient_bank": recipient_bank.upper(),
                "recipient_account": recipient_account,
                "narration": narration,
                "webhook_url": webhook_url,
            }
            if metadata is not None:
                call_kwargs["metadata"] = metadata
            if idempotency_key is not None:
                call_kwargs["idempotency_key"] = idempotency_key

            api_payout = client.create_bank_payout(**call_kwargs)

            payout = SnippePayout.objects.create(
                reference=api_payout.reference,
                channel=SnippePayout.Channel.BANK,
                amount=amount,
                currency=currency,
                recipient_name=recipient_name,
                recipient_bank=recipient_bank.upper(),
                recipient_account=recipient_account,
                narration=narration,
                idempotency_key=idempotency_key,
                webhook_url=webhook_url,
                metadata=metadata or {},
            )

            PayoutLogger.log_payout_created(
                payout.reference, "bank", amount, currency, recipient_name
            )
            return payout

        except Exception as exc:
            PayoutLogger.log_payout_failed(recipient_account, str(exc))
            raise PayoutCreationError(f"Failed to create bank payout: {exc}") from exc

    @staticmethod
    def sync_payout(reference: str) -> SnippePayout:
        """Synchronize local SnippePayout status with the upstream Snippe API."""
        return services.sync_payout_status(reference)

    @staticmethod
    def get_payout_by_reference(reference: str) -> Optional[SnippePayout]:
        """Look up a local SnippePayout by its reference."""
        return SnippePayout.objects.filter(reference=reference).first()

    @staticmethod
    def get_pending_payouts(limit: int = 100) -> List[SnippePayout]:
        """Return up to limit pending payouts."""
        return list(SnippePayout.objects.filter(status=SnippePayout.Status.PENDING)[:limit])

    @staticmethod
    def get_failed_payouts(limit: int = 100) -> List[SnippePayout]:
        """Return up to limit failed payouts."""
        return list(SnippePayout.objects.filter(status=SnippePayout.Status.FAILED)[:limit])


class SessionHelper:
    """High-level helper methods for Snippe 2026-01-25 hosted checkout sessions."""

    @staticmethod
    def create_checkout_session(
        amount: Optional[int] = None,
        currency: str = "TZS",
        allow_custom_amount: bool = False,
        allowed_methods: Optional[Sequence[str]] = None,
        customer: Optional[Dict[str, Any]] = None,
        redirect_url: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> SnippeSession:
        """
        Create a hosted checkout session and persist SnippeSession.

        Raises:
            SessionCreationError: If validation or the Snippe API request fails.
        """
        valid, errors = SessionValidator.validate_session_data(
            amount=amount,
            currency=currency,
            allow_custom_amount=allow_custom_amount,
            allowed_methods=allowed_methods,
        )
        if not valid:
            raise SessionCreationError(f"Invalid session data: {', '.join(errors)}")

        try:
            session = services.create_session(
                amount=amount,
                currency=currency,
                allow_custom_amount=allow_custom_amount,
                allowed_methods=allowed_methods,
                customer=customer,
                redirect_url=redirect_url,
                webhook_url=webhook_url,
                metadata=metadata,
                idempotency_key=idempotency_key,
            )
            SessionLogger.log_session_created(session.reference, session.amount, session.currency)
            return session
        except Exception as exc:
            SessionLogger.log_session_failed("new-session", str(exc))
            raise SessionCreationError(f"Failed to create checkout session: {exc}") from exc

    @staticmethod
    def cancel_checkout_session(reference: str) -> SnippeSession:
        """Cancel an active checkout session by reference."""
        try:
            return services.cancel_session(reference)
        except Exception as exc:
            SessionLogger.log_session_failed(reference, str(exc))
            raise SessionCreationError(
                f"Failed to cancel checkout session {reference}: {exc}"
            ) from exc

    @staticmethod
    def get_session_by_reference(reference: str) -> Optional[SnippeSession]:
        """Look up a local SnippeSession by its reference."""
        return SnippeSession.objects.filter(reference=reference).first()
