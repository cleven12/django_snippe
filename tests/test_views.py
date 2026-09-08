import json
from unittest.mock import patch

import pytest
from django.test import Client

from django_snippe.models import SnippePayment, SnippePayout
from django_snippe import signals

pytestmark = pytest.mark.django_db

WEBHOOK_URL = "/payments/webhook/"


def _post(client, payload, headers=None):
    return client.post(
        WEBHOOK_URL,
        data=json.dumps(payload),
        content_type="application/json",
        **(headers or {}),
    )


@pytest.fixture
def client():
    return Client()


def _make_payment(reference="WH-REF", status=SnippePayment.Status.PENDING):
    return SnippePayment.objects.create(
        reference=reference,
        payment_type=SnippePayment.PaymentType.MOBILE,
        amount=1000,
        currency="TZS",
        phone_number="0712345678",
        status=status,
    )


@patch("django_snippe.views.get_setting", return_value=None)
def test_webhook_rejects_invalid_json(mock_setting, client):
    with pytest.raises(Exception):
        client.post(WEBHOOK_URL, data="not-json", content_type="application/json")


@patch("django_snippe.views.get_setting", return_value=None)
def test_webhook_requires_event_and_reference(mock_setting, client):
    with pytest.raises(Exception):
        _post(client, {"event": "payment.completed"})  # missing reference


@patch("django_snippe.views.get_setting", return_value=None)
def test_webhook_marks_payment_completed(mock_setting, client):
    payment = _make_payment()
    received = {}

    def _receiver(sender, payment, **kwargs):
        received["payment"] = payment

    signals.payment_completed.connect(_receiver)
    try:
        response = _post(client, {"event": "payment.completed", "reference": payment.reference})
    finally:
        signals.payment_completed.disconnect(_receiver)

    assert response.status_code == 200
    payment.refresh_from_db()
    assert payment.status == SnippePayment.Status.COMPLETED
    assert received["payment"].reference == payment.reference


@patch("django_snippe.views.get_setting", return_value=None)
def test_webhook_marks_payment_failed(mock_setting, client):
    payment = _make_payment(reference="WH-FAIL")
    response = _post(client, {"event": "payment.failed", "reference": payment.reference})
    assert response.status_code == 200
    payment.refresh_from_db()
    assert payment.status == SnippePayment.Status.FAILED


@patch("django_snippe.views.get_setting", return_value=None)
def test_webhook_marks_payout_completed(mock_setting, client):
    payout = SnippePayout.objects.create(
        reference="PO-WH-1",
        channel=SnippePayout.Channel.MOBILE,
        amount=1000,
        currency="TZS",
        recipient_name="Jane Doe",
        recipient_phone="0712345678",
        status=SnippePayout.Status.PENDING,
    )
    response = _post(client, {"event": "payout.completed", "reference": payout.reference})
    assert response.status_code == 200
    payout.refresh_from_db()
    assert payout.status == SnippePayout.Status.COMPLETED


@patch("django_snippe.views.get_setting", return_value=None)
def test_webhook_unknown_event_is_ignored_gracefully(mock_setting, client):
    payment = _make_payment(reference="WH-UNKNOWN")
    response = _post(client, {"event": "payment.something_new", "reference": payment.reference})
    assert response.status_code == 200
    payment.refresh_from_db()
    assert payment.status == SnippePayment.Status.PENDING


@patch("django_snippe.views.get_setting", return_value="whsec_test")
@patch("snippe.verify_webhook")
def test_webhook_verifies_signature_when_secret_configured(mock_verify, mock_setting, client):
    payment = _make_payment(reference="WH-SIGNED")
    response = _post(
        client,
        {"event": "payment.completed", "reference": payment.reference},
        headers={
            "HTTP_X_WEBHOOK_SIGNATURE": "sig",
            "HTTP_X_WEBHOOK_TIMESTAMP": "12345",
        },
    )
    assert response.status_code == 200
    mock_verify.assert_called_once()


@patch("django_snippe.views.get_setting", return_value="whsec_test")
@patch("snippe.verify_webhook", side_effect=Exception("bad signature"))
def test_webhook_rejects_bad_signature(mock_verify, mock_setting, client):
    payment = _make_payment(reference="WH-BADSIG")
    with pytest.raises(Exception):
        _post(
            client,
            {"event": "payment.completed", "reference": payment.reference},
            headers={
                "HTTP_X_WEBHOOK_SIGNATURE": "bad",
                "HTTP_X_WEBHOOK_TIMESTAMP": "12345",
            },
        )
