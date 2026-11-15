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
                )
            except TypeError:
                from snippe import verify_webhook

                verify_webhook(
                    body=body,
                    signature=signature,
                    timestamp=timestamp,
                    signing_key=signing_key,
                )
            except Exception as exc:
                logger.warning("Snippe webhook: verification failed - %s", exc)
                err = WebhookVerificationError(f"Webhook verification failed: {exc}")
                if raise_exceptions:
                    raise err from exc
                return JsonResponse(err.to_dict(), status=401)

        event, reference, inner = _extract_event_and_reference(data)

        if not event or not reference:
            logger.error("Snippe webhook: missing event or reference in payload")
            err = WebhookPayloadError("Missing 'event' or 'reference' in webhook payload")
            if raise_exceptions:
                raise err
            return JsonResponse(err.to_dict(), status=400)

        PaymentLogger.log_webhook_received(event, reference)

        delivery_id = (
            request.headers.get("X-Webhook-Id")
            or data.get("id")
            or _compute_delivery_id(event, reference, timestamp, body)
        )
        existing_event = SnippeWebhookEvent.objects.filter(
            delivery_id=delivery_id, processed=True
        ).first()
        if existing_event:
            return JsonResponse(
                {"status": "ok", "idempotent": True, "reference": reference},
                status=200,
            )

        webhook_record, _ = SnippeWebhookEvent.objects.update_or_create(
            delivery_id=delivery_id,
            defaults={
                "event_type": event,
                "reference": reference,
                "payload": data,
                "signature": signature,
                "timestamp": timestamp,
                "processed": False,
                "error_message": None,
            },
        )

        try:
            handler = getattr(self, f"handle_{event.replace('.', '_')}", None)
            if handler:
                handler(reference, data, inner)
            else:
                logger.debug("Snippe webhook: no handler for event %s", event)
            webhook_record.processed = True
            webhook_record.save(update_fields=["processed"])
            PaymentLogger.log_webhook_processing(event, reference, True)
        except Exception as exc:
            webhook_record.error_message = str(exc)
            webhook_record.save(update_fields=["error_message"])
            PaymentLogger.log_webhook_processing(event, reference, False, error=str(exc))
            logger.error("Snippe webhook handler error for %s: %s", event, exc, exc_info=True)
            raise

        return JsonResponse({"status": "ok", "reference": reference}, status=200)

    def _apply_payment_metadata(
        self, payment: SnippePayment, data: Dict[str, Any], inner: Dict[str, Any]
    ) -> List[str]:
        """Extract 2026-01-25 nested amount, fee, channel, and failure fields onto SnippePayment."""
        updated = ["status", "updated_at"]

        amount_obj = inner.get("amount") if "amount" in inner else data.get("amount")
        if isinstance(amount_obj, dict):
            if "value" in amount_obj and isinstance(amount_obj["value"], int):
                payment.amount = amount_obj["value"]
                updated.append("amount")
            if "currency" in amount_obj and amount_obj["currency"]:
                payment.currency = str(amount_obj["currency"])
                updated.append("currency")

        channel = inner.get("payment_channel") or data.get("payment_channel")
        if channel:
            payment.payment_channel = str(channel)
            updated.append("payment_channel")

        fee = inner.get("payment_fee") if "payment_fee" in inner else data.get("payment_fee")
        if isinstance(fee, int):
            payment.fee_amount = fee
            updated.append("fee_amount")

        reason = inner.get("failure_reason") or data.get("failure_reason")
        if reason:
            payment.failure_reason = str(reason)
            updated.append("failure_reason")

        completed_at = inner.get("completed_at") or data.get("completed_at")
        if completed_at:
            payment.completed_at = _parse_dt(completed_at)
            updated.append("completed_at")

        return updated

    def handle_payment_completed(
        self, reference: str, data: Dict[str, Any], inner: Optional[Dict[str, Any]] = None
    ) -> None:
        inner = inner or data
        try:
            payment = SnippePayment.objects.get(reference=reference)
            payment.status = SnippePayment.Status.COMPLETED
            fields = self._apply_payment_metadata(payment, data, inner)
            payment.save(update_fields=fields)
            signals.payment_completed.send(sender=SnippePayment, payment=payment)
            logger.info("Payment %s marked as completed", reference)
        except SnippePayment.DoesNotExist:
            logger.error("Payment %s not found when handling completion", reference)

    def handle_payment_failed(
        self, reference: str, data: Dict[str, Any], inner: Optional[Dict[str, Any]] = None
    ) -> None:
        inner = inner or data
        try:
            payment = SnippePayment.objects.get(reference=reference)
            payment.status = SnippePayment.Status.FAILED
            fields = self._apply_payment_metadata(payment, data, inner)
            payment.save(update_fields=fields)
            signals.payment_failed.send(sender=SnippePayment, payment=payment)
            logger.info("Payment %s marked as failed", reference)
        except SnippePayment.DoesNotExist:
            logger.error("Payment %s not found when handling failure", reference)

    def handle_payment_expired(
        self, reference: str, data: Dict[str, Any], inner: Optional[Dict[str, Any]] = None
    ) -> None:
        inner = inner or data
        try:
            payment = SnippePayment.objects.get(reference=reference)
            payment.status = SnippePayment.Status.EXPIRED
            fields = self._apply_payment_metadata(payment, data, inner)
            payment.save(update_fields=fields)
            signals.payment_expired.send(sender=SnippePayment, payment=payment)
            logger.info("Payment %s marked as expired", reference)
        except SnippePayment.DoesNotExist:
            logger.error("Payment %s not found when handling expiration", reference)

    def handle_payment_voided(
        self, reference: str, data: Dict[str, Any], inner: Optional[Dict[str, Any]] = None
    ) -> None:
        inner = inner or data
        try:
            payment = SnippePayment.objects.get(reference=reference)
            payment.status = SnippePayment.Status.VOIDED
            fields = self._apply_payment_metadata(payment, data, inner)
            payment.save(update_fields=fields)
            signals.payment_voided.send(sender=SnippePayment, payment=payment)
            logger.info("Payment %s marked as voided", reference)
        except SnippePayment.DoesNotExist:
            logger.error("Payment %s not found when handling void", reference)

    def handle_payout_completed(
        self, reference: str, data: Dict[str, Any], inner: Optional[Dict[str, Any]] = None
    ) -> None:
        inner = inner or data
        try:
            payout = SnippePayout.objects.get(reference=reference)
            payout.status = SnippePayout.Status.COMPLETED
            updated = ["status", "updated_at"]
            completed_at = inner.get("completed_at") or data.get("completed_at")
            if completed_at:
                payout.completed_at = _parse_dt(completed_at)
                updated.append("completed_at")
            payout.save(update_fields=updated)
            signals.payout_completed.send(sender=SnippePayout, payout=payout)
            logger.info("Payout %s marked as completed", reference)
        except SnippePayout.DoesNotExist:
            logger.error("Payout %s not found when handling completion", reference)

    def handle_payout_failed(
        self, reference: str, data: Dict[str, Any], inner: Optional[Dict[str, Any]] = None
