"""Webhook endpoint view for Snippe 2026-01-25 events with HMAC verification and idempotency."""

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from . import signals
from .conf import get_setting, get_webhook_tolerance
from .exceptions import WebhookPayloadError, WebhookVerificationError
from .logging import PaymentLogger
from .models import SnippePayment, SnippePayout, SnippeSession, SnippeWebhookEvent
from .services import _parse_dt

logger = logging.getLogger(__name__)


def _extract_event_and_reference(
    data: Dict[str, Any],
) -> tuple[Optional[str], Optional[str], Dict[str, Any]]:
    """Extract event name, reference, and inner data dict from 2026-01-25 or flat webhook payloads."""
    inner = data.get("data") if isinstance(data.get("data"), dict) else data
    event = data.get("event") or data.get("type") or inner.get("event")
    reference = data.get("reference") or inner.get("reference")
    return event, reference, inner


def _compute_delivery_id(event: str, reference: str, timestamp: str, body: str) -> str:
    """Compute a deterministic delivery identifier for idempotent webhook deduplication."""
    digest = hashlib.sha256(f"{event}:{reference}:{timestamp}:{body}".encode("utf-8")).hexdigest()
    return digest[:64]


@method_decorator(csrf_exempt, name="dispatch")
class SnippeWebhookView(View):
    """
    Handles incoming webhook POST requests from Snippe (API version 2026-01-25).

    Usage in urls.py:
        path("payments/", include("django_snippe.urls"))

    This registers: POST /payments/webhook/
    """

    def post(self, request, *args, **kwargs):
        raise_exceptions = bool(get_setting("WEBHOOK_RAISE_EXCEPTIONS", default=False))

        try:
            body = request.body.decode("utf-8")
            data = json.loads(body)
            if not isinstance(data, dict):
                raise ValueError("Webhook payload must be a JSON object")
        except (ValueError, UnicodeDecodeError) as exc:
            logger.warning("Snippe webhook: invalid JSON body - %s", exc)
            err = WebhookPayloadError(f"Invalid JSON body: {exc}")
            if raise_exceptions:
                raise err from exc
            return JsonResponse(err.to_dict(), status=400)

        signing_key = get_setting("WEBHOOK_SECRET")
        signature = request.headers.get("X-Webhook-Signature", "")
        timestamp = request.headers.get("X-Webhook-Timestamp", "")

        if signing_key:
            try:
                from snippe import verify_webhook

                verify_webhook(
                    body=body,
                    signature=signature,
                    timestamp=timestamp,
                    signing_key=signing_key,
                    tolerance=get_webhook_tolerance(),
