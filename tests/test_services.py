"""Unit tests for django_snippe.services and admin_actions."""

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory

from django_snippe import admin_actions, services
from django_snippe.admin import SnippePaymentAdmin, SnippePayoutAdmin, SnippeSessionAdmin
from django_snippe.models import SnippePayment, SnippePayout, SnippeSession

pytestmark = pytest.mark.django_db


def _make_request():
    rf = RequestFactory()
    request = rf.post("/admin/")
    setattr(request, "session", "session")
    messages = FallbackStorage(request)
    setattr(request, "_messages", messages)
    return request


@patch("django_snippe.services.get_client")
def test_services_create_mobile_card_qr_and_sync(mock_get_client):
    client = MagicMock()
    pay_res = MagicMock()
    pay_res.reference = "SRV-PAY-1"
    pay_res.amount = 2500
    pay_res.currency = "TZS"
    pay_res.status = "pending"
    pay_res.payment_type = "mobile"
    pay_res.payment_url = None
    pay_res.payment_qr_code = None
    pay_res.payment_token = None
    pay_res.expires_at = "2026-01-25T16:00:00Z"
    pay_res.fee_amount = 50
    pay_res.net_amount = 2450
    pay_res.psp_reference = "PSP-1"
    pay_res.failure_reason = None
    pay_res.metadata = {"order": 1}

    client.create_mobile_payment.return_value = pay_res
    pay_res_completed = MagicMock()
    pay_res_completed.reference = "SRV-PAY-1"
    pay_res_completed.amount = 2500
    pay_res_completed.currency = "TZS"
    pay_res_completed.status = "completed"
    pay_res_completed.payment_type = "mobile"
    pay_res_completed.expires_at = "2026-01-25T16:00:00Z"
    client.get_payment.return_value = pay_res_completed
    mock_get_client.return_value = client

    p = services.create_mobile_payment(
        amount=2500,
        currency="TZS",
        phone_number="0712345678",
        customer={"firstname": "John", "lastname": "Doe"},
    )
    assert p.reference == "SRV-PAY-1"
    assert p.status == "pending"

    synced = services.sync_payment_status("SRV-PAY-1")
    assert synced.status == "completed"


def test_admin_bulk_actions():
    p1 = SnippePayment.objects.create(
        reference="ADM-P1",
        payment_type="mobile",
        amount=1000,
        currency="TZS",
        phone_number="0712345678",
        status="pending",
    )
    p2 = SnippePayment.objects.create(
        reference="ADM-P2",
        payment_type="mobile",
        amount=1000,
        currency="TZS",
        phone_number="0712345678",
        status="failed",
    )
    po1 = SnippePayout.objects.create(
        reference="ADM-PO1",
        channel="mobile",
        amount=5000,
        currency="TZS",
        recipient_name="Jane Doe",
        recipient_phone="0712345678",
        status="pending",
    )
    s1 = SnippeSession.objects.create(
        reference="ADM-S1",
        amount=5000,
        currency="TZS",
        status="active",
    )

    site = AdminSite()
    pay_admin = SnippePaymentAdmin(SnippePayment, site)
    po_admin = SnippePayoutAdmin(SnippePayout, site)
    ses_admin = SnippeSessionAdmin(SnippeSession, site)

    admin_actions.mark_payment_completed(
        pay_admin, _make_request(), SnippePayment.objects.filter(pk=p1.pk)
    )
    p1.refresh_from_db()
    assert p1.status == "completed"

    admin_actions.retry_payment(pay_admin, _make_request(), SnippePayment.objects.filter(pk=p2.pk))
    p2.refresh_from_db()
    assert p2.status == "pending"

    admin_actions.void_payment(pay_admin, _make_request(), SnippePayment.objects.filter(pk=p2.pk))
    p2.refresh_from_db()
    assert p2.status == "voided"

    admin_actions.mark_payout_failed(
        po_admin, _make_request(), SnippePayout.objects.filter(pk=po1.pk)
    )
    po1.refresh_from_db()
    assert po1.status == "failed"

    admin_actions.retry_payout(po_admin, _make_request(), SnippePayout.objects.filter(pk=po1.pk))
    po1.refresh_from_db()
    assert po1.status == "pending"

    admin_actions.mark_payout_completed(
        po_admin, _make_request(), SnippePayout.objects.filter(pk=po1.pk)
