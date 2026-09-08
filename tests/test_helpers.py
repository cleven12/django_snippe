from unittest.mock import MagicMock, patch

import pytest

from django_snippe.exceptions import PaymentCreationError, PayoutCreationError
from django_snippe.helpers import PaymentHelper, PayoutHelper
from django_snippe.models import SnippePayment, SnippePayout

pytestmark = pytest.mark.django_db


def _mock_api_payment(reference="API-REF-1", payment_url=None):
    api_payment = MagicMock()
    api_payment.reference = reference
    api_payment.payment_url = payment_url
    return api_payment


class TestPaymentHelper:
    @patch("django_snippe.helpers.get_client")
    def test_create_mobile_payment_saves_record(self, mock_get_client):
        client = MagicMock()
        client.create_mobile_payment.return_value = _mock_api_payment("MOB-1")
        mock_get_client.return_value = client

        payment = PaymentHelper.create_mobile_payment(
            amount=5000,
            currency="TZS",
            phone_number="0712345678",
            customer_firstname="John",
            customer_lastname="Doe",
        )

        assert isinstance(payment, SnippePayment)
        assert payment.reference == "MOB-1"
        assert payment.payment_type == SnippePayment.PaymentType.MOBILE
        assert SnippePayment.objects.filter(reference="MOB-1").exists()

    def test_create_mobile_payment_rejects_invalid_phone(self):
        with pytest.raises(PaymentCreationError):
            PaymentHelper.create_mobile_payment(
                amount=5000,
                currency="TZS",
                phone_number="invalid",
                customer_firstname="John",
                customer_lastname="Doe",
            )
        assert not SnippePayment.objects.exists()

    @patch("django_snippe.helpers.get_client")
    def test_create_mobile_payment_wraps_api_errors(self, mock_get_client):
        client = MagicMock()
        client.create_mobile_payment.side_effect = RuntimeError("api down")
        mock_get_client.return_value = client

        with pytest.raises(PaymentCreationError):
            PaymentHelper.create_mobile_payment(
                amount=5000,
                currency="TZS",
                phone_number="0712345678",
                customer_firstname="John",
                customer_lastname="Doe",
            )
        assert not SnippePayment.objects.exists()

    @patch("django_snippe.helpers.get_client")
    def test_create_card_payment_saves_record(self, mock_get_client):
        client = MagicMock()
        client.create_card_payment.return_value = _mock_api_payment(
            "CARD-1", payment_url="https://pay.snippe.sh/x"
        )
        mock_get_client.return_value = client

        payment = PaymentHelper.create_card_payment(
            amount=15000,
            currency="KES",
            customer_firstname="Amina",
            customer_lastname="Yusuf",
        )

        assert payment.payment_type == SnippePayment.PaymentType.CARD
        assert payment.payment_url == "https://pay.snippe.sh/x"

    @patch("django_snippe.helpers.get_client")
    def test_get_payment_by_reference(self, mock_get_client):
        SnippePayment.objects.create(
            reference="LOOKUP-1",
            payment_type=SnippePayment.PaymentType.MOBILE,
            amount=1000,
            currency="TZS",
            phone_number="0712345678",
        )
        found = PaymentHelper.get_payment_by_reference("LOOKUP-1")
        assert found is not None
        assert PaymentHelper.get_payment_by_reference("MISSING") is None

    def test_get_pending_and_failed_payments(self):
        SnippePayment.objects.create(
            reference="P1", payment_type=SnippePayment.PaymentType.MOBILE,
            amount=1000, currency="TZS", phone_number="0712345678",
            status=SnippePayment.Status.PENDING,
        )
        SnippePayment.objects.create(
            reference="P2", payment_type=SnippePayment.PaymentType.MOBILE,
            amount=1000, currency="TZS", phone_number="0712345678",
            status=SnippePayment.Status.FAILED,
        )
        assert len(PaymentHelper.get_pending_payments()) == 1
        assert len(PaymentHelper.get_failed_payments()) == 1


class TestPayoutHelper:
    @patch("django_snippe.helpers.get_client")
    def test_create_mobile_payout_saves_record(self, mock_get_client):
        client = MagicMock()
        api_payout = MagicMock()
        api_payout.reference = "PO-1"
        client.create_mobile_payout.return_value = api_payout
        mock_get_client.return_value = client

        payout = PayoutHelper.create_mobile_payout(
            amount=5000,
            currency="TZS",
            recipient_name="Jane Doe",
            recipient_phone="0712345678",
        )

        assert isinstance(payout, SnippePayout)
        assert payout.reference == "PO-1"
        assert payout.channel == SnippePayout.Channel.MOBILE

    def test_create_mobile_payout_rejects_short_name(self):
        with pytest.raises(PayoutCreationError):
            PayoutHelper.create_mobile_payout(
                amount=5000,
                currency="TZS",
                recipient_name="J",
                recipient_phone="0712345678",
            )
        assert not SnippePayout.objects.exists()

    @patch("django_snippe.helpers.get_client")
    def test_create_mobile_payout_wraps_api_errors(self, mock_get_client):
        client = MagicMock()
        client.create_mobile_payout.side_effect = RuntimeError("api down")
        mock_get_client.return_value = client

        with pytest.raises(PayoutCreationError):
            PayoutHelper.create_mobile_payout(
                amount=5000,
                currency="TZS",
                recipient_name="Jane Doe",
                recipient_phone="0712345678",
            )
