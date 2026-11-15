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

