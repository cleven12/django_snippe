import json
import logging

from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .conf import get_setting
from .models import SnippePayment, SnippePayout
from . import signals

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class SnippeWebhookView(View):
    """
    Handles incoming webhook POST requests from Snippe.

    Add to your urls.py:
        path("webhooks/snippe/", SnippeWebhookView.as_view(), name="snippe-webhook"),

    Then set your webhook URL in Snippe dashboard to:
        https://yourdomain.com/webhooks/snippe/
    """

    def post(self, request, *args, **kwargs):
        # Parse raw body
        try:
            body = request.body.decode("utf-8")
            data = json.loads(body)
        except (ValueError, UnicodeDecodeError) as e:
            logger.warning("Snippe webhook: invalid JSON body — %s", e)
            return HttpResponse(status=400)

        # Verify signature if webhook secret is configured
        signing_key = get_setting("WEBHOOK_SECRET")
        if signing_key:
            signature = request.headers.get("X-Webhook-Signature", "")
            timestamp = request.headers.get("X-Webhook-Timestamp", "")
            try:
                from snippe import verify_webhook, WebhookVerificationError
                verify_webhook(
                    body=body,
                    signature=signature,
                    timestamp=timestamp,
                    signing_key=signing_key,
                )
            except Exception as e:
                logger.warning("Snippe webhook: verification failed — %s", e)
                return HttpResponse(status=400)

        event = data.get("event")
        reference = data.get("reference") or data.get("data", {}).get("reference")

        if not event or not reference:
            return HttpResponse(status=400)

        logger.info("Snippe webhook received: %s for %s", event, reference)

        # Route to handler
        handler = getattr(self, f"handle_{event.replace('.', '_')}", None)
        if handler:
            handler(reference, data)
        else:
            logger.debug("Snippe webhook: no handler for event %s", event)

        return HttpResponse(status=200)

    def handle_payment_completed(self, reference, data):
        payment = SnippePayment.objects.filter(reference=reference).first()
        if payment:
            payment.status = SnippePayment.Status.COMPLETED
            payment.save(update_fields=["status", "updated_at"])
            signals.payment_completed.send(sender=SnippePayment, payment=payment)

    def handle_payment_failed(self, reference, data):
        payment = SnippePayment.objects.filter(reference=reference).first()
        if payment:
            payment.status = SnippePayment.Status.FAILED
            payment.save(update_fields=["status", "updated_at"])
            signals.payment_failed.send(sender=SnippePayment, payment=payment)

    def handle_payment_expired(self, reference, data):
        payment = SnippePayment.objects.filter(reference=reference).first()
        if payment:
            payment.status = SnippePayment.Status.EXPIRED
            payment.save(update_fields=["status", "updated_at"])
            signals.payment_expired.send(sender=SnippePayment, payment=payment)

    def handle_payment_voided(self, reference, data):
        payment = SnippePayment.objects.filter(reference=reference).first()
        if payment:
            payment.status = SnippePayment.Status.VOIDED
            payment.save(update_fields=["status", "updated_at"])
            signals.payment_voided.send(sender=SnippePayment, payment=payment)

    def handle_payout_completed(self, reference, data):
        payout = SnippePayout.objects.filter(reference=reference).first()
        if payout:
            payout.status = SnippePayout.Status.COMPLETED
            payout.save(update_fields=["status", "updated_at"])
            signals.payout_completed.send(sender=SnippePayout, payout=payout)

    def handle_payout_failed(self, reference, data):
        payout = SnippePayout.objects.filter(reference=reference).first()
        if payout:
            payout.status = SnippePayout.Status.FAILED
            payout.save(update_fields=["status", "updated_at"])
            signals.payout_failed.send(sender=SnippePayout, payout=payout)
