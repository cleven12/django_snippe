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
