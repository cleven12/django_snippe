from datetime import datetime

from .conf import get_client
from .models import SnippePayment, SnippePayout


def _parse_dt(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _save_payment(result, phone_number, payment_type, webhook_url, metadata):
    return SnippePayment.objects.create(
        reference=result.reference,
        payment_type=payment_type,
        amount=result.amount,
        currency=result.currency,
        phone_number=phone_number,
        status=result.status or SnippePayment.Status.PENDING,
        payment_url=result.payment_url,
        payment_qr_code=result.payment_qr_code,
        payment_token=result.payment_token,
        webhook_url=webhook_url,
        metadata=metadata or {},
        expires_at=_parse_dt(result.expires_at),
    )


def _save_payout(result, webhook_url, metadata):
    return SnippePayout.objects.create(
        reference=result.reference,
        channel=result.channel.type,
        amount=result.amount.value,
        currency=result.amount.currency,
        recipient_name=result.recipient.name,
        recipient_phone=result.recipient.phone,
        recipient_bank=result.recipient.bank,
        recipient_account=result.recipient.account,
        status=result.status or SnippePayout.Status.PENDING,
        narration=result.narration,
        failure_reason=result.failure_reason,
        webhook_url=webhook_url,
        metadata=metadata or {},
        completed_at=_parse_dt(result.completed_at),
    )


def create_mobile_payment(
    amount, currency, phone_number, customer,
    callback_url=None, webhook_url=None, metadata=None, idempotency_key=None,
) -> SnippePayment:
    client = get_client()
    result = client.create_mobile_payment(
        amount=amount,
        currency=currency,
        phone_number=phone_number,
        customer=customer,
        callback_url=callback_url,
        webhook_url=webhook_url,
        metadata=metadata,
        idempotency_key=idempotency_key,
    )
    return _save_payment(result, phone_number, SnippePayment.PaymentType.MOBILE, webhook_url, metadata)


def create_card_payment(
    amount, currency, phone_number, customer, callback_url,
    webhook_url=None, metadata=None, idempotency_key=None,
) -> SnippePayment:
    client = get_client()
    result = client.create_card_payment(
        amount=amount,
        currency=currency,
        phone_number=phone_number,
        customer=customer,
        callback_url=callback_url,
        webhook_url=webhook_url,
        metadata=metadata,
        idempotency_key=idempotency_key,
    )
    return _save_payment(result, phone_number, SnippePayment.PaymentType.CARD, webhook_url, metadata)


def create_qr_payment(
    amount, currency, phone_number, customer,
    callback_url=None, webhook_url=None, metadata=None, idempotency_key=None,
) -> SnippePayment:
    client = get_client()
    result = client.create_qr_payment(
        amount=amount,
        currency=currency,
        phone_number=phone_number,
        customer=customer,
        callback_url=callback_url,
        webhook_url=webhook_url,
        metadata=metadata,
        idempotency_key=idempotency_key,
    )
    return _save_payment(result, phone_number, SnippePayment.PaymentType.QR, webhook_url, metadata)


def create_mobile_payout(
    amount, recipient_name, recipient_phone,
    narration=None, webhook_url=None, metadata=None, idempotency_key=None,
) -> SnippePayout:
    client = get_client()
    result = client.create_mobile_payout(
        amount=amount,
        recipient_name=recipient_name,
        recipient_phone=recipient_phone,
        narration=narration,
        webhook_url=webhook_url,
        metadata=metadata,
        idempotency_key=idempotency_key,
    )
    return _save_payout(result, webhook_url, metadata)


def create_bank_payout(
    amount, recipient_name, recipient_bank, recipient_account,
    narration=None, webhook_url=None, metadata=None, idempotency_key=None,
) -> SnippePayout:
    client = get_client()
    result = client.create_bank_payout(
        amount=amount,
        recipient_name=recipient_name,
        recipient_bank=recipient_bank,
        recipient_account=recipient_account,
        narration=narration,
        webhook_url=webhook_url,
        metadata=metadata,
        idempotency_key=idempotency_key,
    )
    return _save_payout(result, webhook_url, metadata)
