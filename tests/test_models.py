import pytest
from django.core.exceptions import ValidationError

from django_snippe.models import SnippePayment, SnippePayout

pytestmark = pytest.mark.django_db


def make_payment(**overrides):
    defaults = dict(
        reference="PAY-1",
        payment_type=SnippePayment.PaymentType.MOBILE,
        amount=5000,
        currency="TZS",
        phone_number="0712345678",
    )
    defaults.update(overrides)
    return SnippePayment.objects.create(**defaults)


def make_payout(**overrides):
    defaults = dict(
        reference="PAYOUT-1",
        channel=SnippePayout.Channel.MOBILE,
        amount=5000,
        currency="TZS",
        recipient_name="Jane Doe",
        recipient_phone="0712345678",
    )
    defaults.update(overrides)
    return SnippePayout.objects.create(**defaults)


class TestSnippePayment:
    def test_create_and_str(self):
        payment = make_payment()
        assert payment.pk is not None
        assert payment.status == SnippePayment.Status.PENDING
        assert "PAY-1" in str(payment)

    def test_reference_must_be_unique(self):
        make_payment(reference="DUPLICATE")
        with pytest.raises(Exception):
            make_payment(reference="DUPLICATE")

    def test_full_clean_rejects_unsupported_currency(self):
        payment = SnippePayment(
            reference="PAY-2",
            payment_type=SnippePayment.PaymentType.MOBILE,
            amount=5000,
            currency="USD",
            phone_number="0712345678",
        )
        with pytest.raises(ValidationError):
