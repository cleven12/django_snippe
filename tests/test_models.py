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
            payment.full_clean()

    def test_full_clean_rejects_invalid_phone(self):
        payment = SnippePayment(
            reference="PAY-3",
            payment_type=SnippePayment.PaymentType.MOBILE,
            amount=5000,
            currency="TZS",
            phone_number="not-a-phone",
        )
        with pytest.raises(ValidationError):
            payment.full_clean()

    def test_status_change_is_logged(self, caplog):
        payment = make_payment()
        with caplog.at_level("INFO", logger="django_snippe.audit"):
            payment.status = SnippePayment.Status.COMPLETED
            payment.save()
        assert any("status changed" in record.message for record in caplog.records)


class TestSnippePayout:
    def test_create_and_str(self):
        payout = make_payout()
        assert payout.pk is not None
        assert payout.status == SnippePayout.Status.PENDING
        assert "PAYOUT-1" in str(payout)

    def test_full_clean_rejects_short_recipient_name(self):
        payout = SnippePayout(
            reference="PAYOUT-2",
            channel=SnippePayout.Channel.BANK,
            amount=5000,
            currency="TZS",
            recipient_name="J",
        )
        with pytest.raises(ValidationError):
            payout.full_clean()

    def test_full_clean_rejects_unsupported_currency(self):
        payout = SnippePayout(
            reference="PAYOUT-3",
            channel=SnippePayout.Channel.BANK,
            amount=5000,
            currency="USD",
            recipient_name="Jane Doe",
        )
        with pytest.raises(ValidationError):
            payout.full_clean()

    def test_status_change_is_logged(self, caplog):
        payout = make_payout()
        with caplog.at_level("INFO", logger="django_snippe.audit"):
            payout.status = SnippePayout.Status.COMPLETED
            payout.save()
        assert any("status changed" in record.message for record in caplog.records)
