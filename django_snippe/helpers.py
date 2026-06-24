"""Helper utilities for working with payments and payouts."""

from typing import Dict, Optional, Any

from .conf import get_client
from .models import SnippePayment, SnippePayout
from .exceptions import PaymentCreationError, PayoutCreationError
from .validators import PaymentValidator, PayoutValidator
from .logging import PaymentLogger, PayoutLogger


class PaymentHelper:
    """Helper functions for payment operations."""

    @staticmethod
    def create_mobile_payment(
        amount: int,
        currency: str,
        phone_number: str,
        customer_firstname: str,
        customer_lastname: str,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> SnippePayment:
        """
        Create a mobile money payment record.

        Args:
            amount: Payment amount
            currency: Currency code (TZS, KES, UGX)
            phone_number: Customer phone number
            customer_firstname: Customer first name
            customer_lastname: Customer last name
            webhook_url: Webhook URL for payment events
            metadata: Additional metadata dict

        Returns:
            SnippePayment model instance

        Raises:
            PaymentCreationError: If payment creation fails
        """
        # Validate input
        valid, errors = PaymentValidator.validate_payment_data(
            amount, currency, phone_number, "mobile"
        )
        if not valid:
            raise PaymentCreationError(f"Invalid payment data: {', '.join(errors)}")

        try:
            # Create payment via API
            client = get_client()
            from snippe import Customer

            customer = Customer(firstname=customer_firstname, lastname=customer_lastname)
            api_payment = client.create_mobile_payment(
                amount=amount,
                currency=currency,
                phone_number=phone_number,
                customer=customer,
                webhook_url=webhook_url,
            )

            # Save to database
            payment = SnippePayment.objects.create(
                reference=api_payment.reference,
                payment_type=SnippePayment.PaymentType.MOBILE,
                amount=amount,
                currency=currency,
                phone_number=phone_number,
                webhook_url=webhook_url,
                metadata=metadata or {},
            )

            PaymentLogger.log_payment_created(
                payment.reference, "mobile", amount, currency, phone_number
            )
            return payment

        except Exception as e:
            PaymentLogger.log_payment_failed(phone_number, str(e))
            raise PaymentCreationError(f"Failed to create mobile payment: {e}") from e

    @staticmethod
    def create_card_payment(
        amount: int,
        currency: str,
        customer_firstname: str,
        customer_lastname: str,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> SnippePayment:
        """Create a card payment record."""
        valid, errors = PaymentValidator.validate_payment_data(
            amount, currency, "0712345678", "card"  # Dummy phone for validation
        )
        if not valid:
            raise PaymentCreationError(f"Invalid payment data: {', '.join(errors)}")

        try:
            client = get_client()
            from snippe import Customer

            customer = Customer(firstname=customer_firstname, lastname=customer_lastname)
            api_payment = client.create_card_payment(
                amount=amount,
                currency=currency,
                customer=customer,
                webhook_url=webhook_url,
            )

            payment = SnippePayment.objects.create(
                reference=api_payment.reference,
                payment_type=SnippePayment.PaymentType.CARD,
                amount=amount,
                currency=currency,
                phone_number="",
                payment_url=getattr(api_payment, "payment_url", None),
                webhook_url=webhook_url,
                metadata=metadata or {},
            )

            PaymentLogger.log_payment_created(
                payment.reference, "card", amount, currency, customer_firstname
            )
            return payment

        except Exception as e:
            PaymentLogger.log_payment_failed(customer_firstname, str(e))
            raise PaymentCreationError(f"Failed to create card payment: {e}") from e

    @staticmethod
    def get_payment_by_reference(reference: str) -> Optional[SnippePayment]:
        """Get payment by reference."""
        return SnippePayment.objects.filter(reference=reference).first()

    @staticmethod
    def get_pending_payments(limit: int = 100) -> list:
        """Get pending payments."""
        return list(SnippePayment.objects.filter(status="pending")[:limit])

    @staticmethod
    def get_failed_payments(limit: int = 100) -> list:
        """Get failed payments."""
        return list(SnippePayment.objects.filter(status="failed")[:limit])


class PayoutHelper:
    """Helper functions for payout operations."""

    @staticmethod
    def create_mobile_payout(
        amount: int,
        currency: str,
        recipient_name: str,
        recipient_phone: str,
        narration: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> SnippePayout:
        """
        Create a mobile money payout.

        Args:
            amount: Payout amount
            currency: Currency code
            recipient_name: Recipient name
            recipient_phone: Recipient phone
            narration: Payment description
            webhook_url: Webhook URL
            metadata: Additional metadata

        Returns:
            SnippePayout model instance

        Raises:
            PayoutCreationError: If payout creation fails
        """
        valid, errors = PayoutValidator.validate_payout_data(
            amount, currency, "mobile", recipient_name, recipient_phone
        )
        if not valid:
            raise PayoutCreationError(f"Invalid payout data: {', '.join(errors)}")

        try:
            client = get_client()
            api_payout = client.create_mobile_payout(
                amount=amount,
                currency=currency,
                recipient_name=recipient_name,
                recipient_phone=recipient_phone,
                narration=narration,
                webhook_url=webhook_url,
            )

            payout = SnippePayout.objects.create(
                reference=api_payout.reference,
                channel=SnippePayout.Channel.MOBILE,
                amount=amount,
                currency=currency,
                recipient_name=recipient_name,
                recipient_phone=recipient_phone,
                narration=narration,
                webhook_url=webhook_url,
                metadata=metadata or {},
            )

            PayoutLogger.log_payout_created(
                payout.reference, "mobile", amount, currency, recipient_name
            )
            return payout

        except Exception as e:
            PayoutLogger.log_payout_failed(recipient_phone, str(e))
            raise PayoutCreationError(f"Failed to create mobile payout: {e}") from e

    @staticmethod
    def get_payout_by_reference(reference: str) -> Optional[SnippePayout]:
        """Get payout by reference."""
        return SnippePayout.objects.filter(reference=reference).first()

    @staticmethod
    def get_pending_payouts(limit: int = 100) -> list:
        """Get pending payouts."""
        return list(SnippePayout.objects.filter(status="pending")[:limit])

    @staticmethod
    def get_failed_payouts(limit: int = 100) -> list:
        """Get failed payouts."""
        return list(SnippePayout.objects.filter(status="failed")[:limit])
