"""Low-level service functions interacting with the Snippe 2026-01-25 API and Django ORM."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from .conf import get_client, get_default_currency
from .models import SnippePayment, SnippePayout, SnippeSession


def _opt_str(obj: Any, attr: str) -> Optional[str]:
    """Return string attribute if present and a real str, otherwise None."""
    val = getattr(obj, attr, None)
    return val if isinstance(val, str) else None


def _opt_int(obj: Any, attr: str) -> Optional[int]:
    """Return integer attribute if present and a real int (not bool), otherwise None."""
    val = getattr(obj, attr, None)
    return val if isinstance(val, int) and not isinstance(val, bool) else None


def _parse_dt(value: Any) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp string into a timezone-aware datetime object."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _extract_amount_and_currency(
    raw_amount: Any, fallback_currency: str = "TZS"
) -> tuple[int, str]:
    """Extract integer amount and currency from either an int or 2026-01-25 {value, currency} dict."""
    if isinstance(raw_amount, dict):
        return int(raw_amount.get("value", 0)), str(raw_amount.get("currency", fallback_currency))
    val = getattr(raw_amount, "value", None)
    cur = getattr(raw_amount, "currency", None)
    if isinstance(val, int) and not isinstance(val, bool):
        return val, cur if isinstance(cur, str) else fallback_currency
    if isinstance(raw_amount, int) and not isinstance(raw_amount, bool):
        return raw_amount, fallback_currency
    return 0, fallback_currency


def _save_payment(
    result: Any,
    phone_number: str,
    payment_type: str,
    webhook_url: Optional[str],
    metadata: Optional[Dict[str, Any]],
    *,
    callback_url: Optional[str] = None,
    customer: Any = None,
    idempotency_key: Optional[str] = None,
) -> SnippePayment:
    """Persist or update a SnippePayment model from an SDK Payment response."""
    cust_first = _opt_str(customer, "firstname")
    cust_last = _opt_str(customer, "lastname")
    cust_email = _opt_str(customer, "email")
    if isinstance(customer, dict):
        cust_first = customer.get("firstname") or customer.get("first_name")
        cust_last = customer.get("lastname") or customer.get("last_name")
        cust_email = customer.get("email")

    res_metadata = getattr(result, "metadata", None)
    resolved_meta = (
        metadata
        if isinstance(metadata, dict)
        else (res_metadata if isinstance(res_metadata, dict) else {})
    )

    defaults = {
        "payment_type": _opt_str(result, "payment_type") or payment_type,
        "amount": _opt_int(result, "amount") or 0,
        "currency": _opt_str(result, "currency") or get_default_currency(),
        "phone_number": phone_number or "",
        "status": _opt_str(result, "status") or SnippePayment.Status.PENDING,
        "payment_url": _opt_str(result, "payment_url"),
        "payment_qr_code": _opt_str(result, "payment_qr_code"),
        "payment_token": _opt_str(result, "payment_token"),
        "callback_url": callback_url,
        "webhook_url": webhook_url,
        "customer_firstname": cust_first,
        "customer_lastname": cust_last,
        "customer_email": cust_email,
        "idempotency_key": idempotency_key,
        "fee_amount": _opt_int(result, "fee_amount"),
        "net_amount": _opt_int(result, "net_amount"),
        "psp_reference": _opt_str(result, "psp_reference"),
        "failure_reason": _opt_str(result, "failure_reason"),
        "metadata": resolved_meta,
        "expires_at": _parse_dt(_opt_str(result, "expires_at")),
    }
    payment, _ = SnippePayment.objects.update_or_create(
        reference=result.reference,
        defaults=defaults,
    )
    return payment


def _save_payout(
    result: Any,
    webhook_url: Optional[str],
    metadata: Optional[Dict[str, Any]],
    *,
    idempotency_key: Optional[str] = None,
) -> SnippePayout:
    """Persist or update a SnippePayout model from an SDK Payout response."""
    amount_val, currency_val = _extract_amount_and_currency(
        getattr(result, "amount", 0), get_default_currency()
    )
    fees_val, _ = _extract_amount_and_currency(getattr(result, "fees", 0), currency_val)
    total_val, _ = _extract_amount_and_currency(getattr(result, "total", 0), currency_val)

    channel_obj = getattr(result, "channel", None)
    channel_type = _opt_str(channel_obj, "type") if channel_obj else "mobile"
    provider = _opt_str(channel_obj, "provider") if channel_obj else None

    recipient_obj = getattr(result, "recipient", None)
    res_metadata = getattr(result, "metadata", None)
    resolved_meta = (
        metadata
        if isinstance(metadata, dict)
        else (res_metadata if isinstance(res_metadata, dict) else {})
    )

    defaults = {
        "channel": channel_type or SnippePayout.Channel.MOBILE,
        "provider": provider,
        "amount": amount_val,
        "fee_amount": fees_val,
        "total_amount": total_val,
        "currency": currency_val,
        "recipient_name": (_opt_str(recipient_obj, "name") if recipient_obj else None)
        or "Recipient",
        "recipient_phone": _opt_str(recipient_obj, "phone") if recipient_obj else None,
        "recipient_bank": _opt_str(recipient_obj, "bank") if recipient_obj else None,
        "recipient_account": _opt_str(recipient_obj, "account") if recipient_obj else None,
        "status": _opt_str(result, "status") or SnippePayout.Status.PENDING,
        "narration": _opt_str(result, "narration"),
        "external_reference": _opt_str(result, "external_reference"),
        "idempotency_key": idempotency_key,
        "failure_reason": _opt_str(result, "failure_reason"),
        "webhook_url": webhook_url,
        "metadata": resolved_meta,
        "completed_at": _parse_dt(_opt_str(result, "completed_at")),
    }
    payout, _ = SnippePayout.objects.update_or_create(
        reference=result.reference,
        defaults=defaults,
    )
    return payout


def create_mobile_payment(
    amount: int,
    currency: str,
    phone_number: str,
    customer: Any,
    callback_url: Optional[str] = None,
    webhook_url: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    idempotency_key: Optional[str] = None,
) -> SnippePayment:
    """Create a mobile money payment (USSD push) and store SnippePayment."""
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
    return _save_payment(
        result,
        phone_number,
        SnippePayment.PaymentType.MOBILE,
        webhook_url,
        metadata,
        callback_url=callback_url,
        customer=customer,
        idempotency_key=idempotency_key,
    )


def create_card_payment(
    amount: int,
    currency: str,
    phone_number: str,
    customer: Any,
    callback_url: str,
    webhook_url: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    idempotency_key: Optional[str] = None,
    redirect_url: Optional[str] = None,
    cancel_url: Optional[str] = None,
) -> SnippePayment:
    """Create a card payment and store SnippePayment."""
    client = get_client()
    kwargs: Dict[str, Any] = {
        "amount": amount,
        "currency": currency,
        "phone_number": phone_number,
        "customer": customer,
        "callback_url": callback_url,
        "webhook_url": webhook_url,
        "metadata": metadata,
        "idempotency_key": idempotency_key,
    }
    if redirect_url is not None:
        kwargs["redirect_url"] = redirect_url
    if cancel_url is not None:
        kwargs["cancel_url"] = cancel_url
    result = client.create_card_payment(**kwargs)
    return _save_payment(
        result,
        phone_number,
        SnippePayment.PaymentType.CARD,
        webhook_url,
        metadata,
        callback_url=redirect_url or callback_url,
        customer=customer,
        idempotency_key=idempotency_key,
    )


def create_qr_payment(
    amount: int,
    currency: str,
    phone_number: str,
    customer: Any,
    callback_url: Optional[str] = None,
    webhook_url: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    idempotency_key: Optional[str] = None,
) -> SnippePayment:
    """Create a dynamic QR code payment and store SnippePayment."""
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
    return _save_payment(
        result,
        phone_number,
        SnippePayment.PaymentType.QR,
        webhook_url,
        metadata,
        callback_url=callback_url,
        customer=customer,
        idempotency_key=idempotency_key,
    )


def trigger_payment_push(
    reference: str,
    phone_number: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Trigger or re-trigger a USSD push for an existing pending payment.
    Endpoint: POST /v1/payments/{reference}/push
    """
    client = get_client()
    payload = {"phone_number": phone_number} if phone_number else {}
    response = client._client.post(f"/payments/{reference}/push", json=payload)
    return client._handle_response(response)


def sync_payment_status(reference: str) -> SnippePayment:
    """Fetch latest payment status from GET /v1/payments/{reference} and update local record."""
