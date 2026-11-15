"""Unit tests for PaymentHelper, PayoutHelper, and SessionHelper."""

from unittest.mock import MagicMock, patch

import pytest

from django_snippe.exceptions import PaymentCreationError, PayoutCreationError, SessionCreationError
from django_snippe.helpers import PaymentHelper, PayoutHelper, SessionHelper
from django_snippe.models import SnippePayment, SnippePayout, SnippeSession

pytestmark = pytest.mark.django_db


def _mock_api_payment(reference="API-REF-1", payment_url=None, qr_code=None, token=None):
    api_payment = MagicMock()
    api_payment.reference = reference
    api_payment.status = "pending"
    api_payment.payment_url = payment_url
    api_payment.payment_qr_code = qr_code
    api_payment.payment_token = token
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
            idempotency_key="idem-mob-1",
        )

        assert isinstance(payment, SnippePayment)
        assert payment.reference == "MOB-1"
        assert payment.payment_type == SnippePayment.PaymentType.MOBILE
        assert payment.idempotency_key == "idem-mob-1"
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
    def test_create_qr_payment_saves_record(self, mock_get_client):
        client = MagicMock()
        client.create_qr_payment.return_value = _mock_api_payment(
            "QR-1", qr_code="BASE64QR", token="TOK-1"
        )
        mock_get_client.return_value = client

        payment = PaymentHelper.create_qr_payment(
            amount=10000,
            currency="TZS",
            phone_number="0712345678",
            customer_firstname="Baraka",
            customer_lastname="Mushi",
        )

        assert payment.payment_type == SnippePayment.PaymentType.QR
        assert payment.payment_qr_code == "BASE64QR"
        assert payment.payment_token == "TOK-1"

    @patch("django_snippe.services.get_client")
    def test_trigger_push_and_search(self, mock_get_client):
        client = MagicMock()
        client._handle_response.return_value = {"status": "pushed", "reference": "MOB-1"}
        mock_get_client.return_value = client

        res = PaymentHelper.trigger_push("MOB-1", phone_number="255712345678")
        assert res["status"] == "pushed"

    def test_get_payment_by_reference(self):
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
            reference="P1",
            payment_type=SnippePayment.PaymentType.MOBILE,
            amount=1000,
            currency="TZS",
            phone_number="0712345678",
            status=SnippePayment.Status.PENDING,
        )
        SnippePayment.objects.create(
            reference="P2",
            payment_type=SnippePayment.PaymentType.MOBILE,
            amount=1000,
            currency="TZS",
            phone_number="0712345678",
            status=SnippePayment.Status.FAILED,
        )
        assert len(PaymentHelper.get_pending_payments()) == 1
        assert len(PaymentHelper.get_failed_payments()) == 1


class TestPayoutHelper:
    @patch("django_snippe.helpers.get_client")
    def test_create_mobile_payout_saves_record(self, mock_get_client):
        client = MagicMock()
