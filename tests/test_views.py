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
