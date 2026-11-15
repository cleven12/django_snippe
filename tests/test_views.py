"""Unit tests for SnippeWebhookView (Snippe API 2026-01-25)."""

import json
from unittest.mock import patch

import pytest
from django.test import Client

from django_snippe import signals
from django_snippe.models import SnippePayment, SnippePayout, SnippeSession, SnippeWebhookEvent

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
    response = client.post(WEBHOOK_URL, data="not-json", content_type="application/json")
    assert response.status_code == 400
    body = response.json()
    assert body["status"] == "error"
    assert body["error_code"] == "invalid_webhook_payload"


@patch("django_snippe.views.get_setting", return_value=None)
def test_webhook_requires_event_and_reference(mock_setting, client):
    response = _post(client, {"event": "payment.completed"})
    assert response.status_code == 400
    body = response.json()
    assert body["status"] == "error"
    assert body["error_code"] == "invalid_webhook_payload"


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
def test_webhook_handles_2026_01_25_nested_data_amount_object(mock_setting, client):
    payment = _make_payment(reference="WH-2026-NESTED")
    payload = {
        "id": "evt_2026_001",
        "event": "payment.completed",
        "data": {
            "reference": payment.reference,
            "status": "completed",
            "amount": {"value": 50000, "currency": "TZS"},
            "payment_channel": "M-PESA",
            "payment_fee": 250,
            "completed_at": "2026-01-25T12:00:00Z",
        },
    }
    response = _post(client, payload)
    assert response.status_code == 200
    payment.refresh_from_db()
    assert payment.status == SnippePayment.Status.COMPLETED
    assert payment.amount == 50000
    assert payment.currency == "TZS"
    assert payment.payment_channel == "M-PESA"
    assert payment.fee_amount == 250
    assert payment.completed_at is not None


@patch("django_snippe.views.get_setting", return_value=None)
def test_webhook_idempotency_skips_duplicate_delivery(mock_setting, client):
    payment = _make_payment(reference="WH-IDEMP-1")
    payload = {"id": "evt_dup_123", "event": "payment.completed", "reference": payment.reference}
    first = _post(client, payload)
    second = _post(client, payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json().get("idempotent") is True
    assert SnippeWebhookEvent.objects.filter(delivery_id="evt_dup_123").count() == 1


@patch("django_snippe.views.get_setting", return_value=None)
def test_webhook_marks_payment_failed_with_reason(mock_setting, client):
    payment = _make_payment(reference="WH-FAIL")
    response = _post(
        client,
        {
            "event": "payment.failed",
            "reference": payment.reference,
            "failure_reason": "Insufficient balance",
        },
    )
    assert response.status_code == 200
    payment.refresh_from_db()
    assert payment.status == SnippePayment.Status.FAILED
    assert payment.failure_reason == "Insufficient balance"


@patch("django_snippe.views.get_setting", return_value=None)
def test_webhook_marks_payment_expired_and_voided(mock_setting, client):
    exp_payment = _make_payment(reference="WH-EXP")
    void_payment = _make_payment(reference="WH-VOID")

    r1 = _post(client, {"event": "payment.expired", "reference": exp_payment.reference})
    r2 = _post(client, {"event": "payment.voided", "reference": void_payment.reference})

    assert r1.status_code == 200
    assert r2.status_code == 200
    exp_payment.refresh_from_db()
    void_payment.refresh_from_db()
    assert exp_payment.status == SnippePayment.Status.EXPIRED
    assert void_payment.status == SnippePayment.Status.VOIDED


@patch("django_snippe.views.get_setting", return_value=None)
def test_webhook_marks_payout_completed_failed_and_reversed(mock_setting, client):
    payout_ok = SnippePayout.objects.create(
        reference="PO-WH-1",
        channel=SnippePayout.Channel.MOBILE,
        amount=5000,
        currency="TZS",
        recipient_name="Jane Doe",
        recipient_phone="0712345678",
    )
    payout_fail = SnippePayout.objects.create(
        reference="PO-WH-2",
        channel=SnippePayout.Channel.MOBILE,
        amount=5000,
        currency="TZS",
        recipient_name="Jane Doe",
        recipient_phone="0712345678",
    )
    payout_rev = SnippePayout.objects.create(
        reference="PO-WH-3",
        channel=SnippePayout.Channel.BANK,
        amount=10000,
        currency="TZS",
        recipient_name="Vendor Ltd",
        recipient_bank="CRDB",
        recipient_account="0150000000000",
    )

    assert (
        _post(client, {"event": "payout.completed", "reference": payout_ok.reference}).status_code
        == 200
    )
    assert (
        _post(
            client,
            {
                "event": "payout.failed",
                "reference": payout_fail.reference,
                "failure_reason": "Account frozen",
            },
        ).status_code
        == 200
    )
    assert (
        _post(client, {"event": "payout.reversed", "reference": payout_rev.reference}).status_code
        == 200
    )

    payout_ok.refresh_from_db()
    payout_fail.refresh_from_db()
    payout_rev.refresh_from_db()
    assert payout_ok.status == SnippePayout.Status.COMPLETED
    assert payout_fail.status == SnippePayout.Status.FAILED
    assert payout_fail.failure_reason == "Account frozen"
    assert payout_rev.status == SnippePayout.Status.REVERSED


@patch("django_snippe.views.get_setting", return_value=None)
def test_webhook_handles_session_events(mock_setting, client):
    s_comp = SnippeSession.objects.create(reference="SES-1", amount=5000, currency="TZS")
    s_exp = SnippeSession.objects.create(reference="SES-2", amount=5000, currency="TZS")
    s_canc = SnippeSession.objects.create(reference="SES-3", amount=5000, currency="TZS")

    assert (
        _post(client, {"event": "session.completed", "reference": s_comp.reference}).status_code
        == 200
    )
    assert (
        _post(client, {"event": "session.expired", "reference": s_exp.reference}).status_code == 200
    )
    assert (
        _post(client, {"event": "session.cancelled", "reference": s_canc.reference}).status_code
        == 200
    )

    s_comp.refresh_from_db()
    s_exp.refresh_from_db()
    s_canc.refresh_from_db()
    assert s_comp.status == SnippeSession.Status.COMPLETED
    assert s_exp.status == SnippeSession.Status.EXPIRED
    assert s_canc.status == SnippeSession.Status.CANCELLED


@patch("django_snippe.views.get_setting", return_value=None)
def test_webhook_unknown_event_is_ignored_gracefully(mock_setting, client):
    payment = _make_payment(reference="WH-UNKNOWN")
    response = _post(client, {"event": "payment.something_new", "reference": payment.reference})
    assert response.status_code == 200
    payment.refresh_from_db()
    assert payment.status == SnippePayment.Status.PENDING


@patch(
    "django_snippe.views.get_setting",
    side_effect=lambda name, default=None, required=False: (
        "whsec_test" if name == "WEBHOOK_SECRET" else default
    ),
)
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
