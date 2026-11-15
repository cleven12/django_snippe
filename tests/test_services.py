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
