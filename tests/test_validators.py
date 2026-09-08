import pytest
from django.core.exceptions import ValidationError

from django_snippe.validators import (
    CurrencyValidator,
    PhoneValidator,
    PaymentValidator,
    PayoutValidator,
    validate_recipient_name,
)


@pytest.mark.parametrize("currency", ["TZS", "KES", "UGX"])
def test_currency_validator_accepts_supported_currencies(currency):
    CurrencyValidator.validate_currency(currency)


def test_currency_validator_rejects_unsupported_currency():
    with pytest.raises(ValidationError):
        CurrencyValidator.validate_currency("USD")


@pytest.mark.parametrize(
    "phone",
    ["0712345678", "255712345678", "+255712345678", "0742345678"],
)
def test_phone_validator_accepts_valid_tanzania_numbers(phone):
    PhoneValidator.validate_phone(phone)


@pytest.mark.parametrize("phone", ["", "123", "07123", "not-a-phone"])
def test_phone_validator_rejects_invalid_numbers(phone):
    with pytest.raises(ValidationError):
        PhoneValidator.validate_phone(phone)


@pytest.mark.parametrize("name", ["a", "", "   "])
def test_validate_recipient_name_rejects_too_short(name):
    with pytest.raises(ValidationError):
        validate_recipient_name(name)


def test_validate_recipient_name_accepts_valid_name():
    validate_recipient_name("Jane Doe")


class TestPaymentValidator:
    def test_valid_mobile_payment(self):
        valid, errors = PaymentValidator.validate_payment_data(
            amount=5000, currency="TZS", phone_number="0712345678", payment_type="mobile"
        )
        assert valid is True
        assert errors == []

    def test_rejects_non_positive_amount(self):
        valid, errors = PaymentValidator.validate_payment_data(
            amount=0, currency="TZS", phone_number="0712345678", payment_type="mobile"
        )
        assert valid is False
        assert any("amount" in e for e in errors)

    def test_rejects_unsupported_currency(self):
        valid, errors = PaymentValidator.validate_payment_data(
            amount=5000, currency="USD", phone_number="0712345678", payment_type="mobile"
        )
        assert valid is False
        assert any("currency" in e for e in errors)

    def test_rejects_invalid_phone_for_mobile(self):
        valid, errors = PaymentValidator.validate_payment_data(
            amount=5000, currency="TZS", phone_number="123", payment_type="mobile"
        )
        assert valid is False
        assert any("phone_number" in e for e in errors)

    def test_card_payment_does_not_require_phone(self):
        valid, errors = PaymentValidator.validate_payment_data(
            amount=5000, currency="TZS", phone_number="", payment_type="card"
        )
        assert valid is True

    def test_rejects_unsupported_payment_type(self):
        valid, errors = PaymentValidator.validate_payment_data(
            amount=5000, currency="TZS", phone_number="0712345678", payment_type="bitcoin"
        )
        assert valid is False


class TestPayoutValidator:
    def test_valid_mobile_payout(self):
        valid, errors = PayoutValidator.validate_payout_data(
            amount=5000,
            currency="TZS",
            channel="mobile",
            recipient_name="Jane Doe",
            recipient_phone="0712345678",
        )
        assert valid is True
        assert errors == []

    def test_requires_recipient_name(self):
        valid, errors = PayoutValidator.validate_payout_data(
            amount=5000, currency="TZS", channel="bank", recipient_name=" "
        )
        assert valid is False
        assert any("recipient_name" in e for e in errors)

    def test_bank_channel_does_not_require_phone(self):
        valid, errors = PayoutValidator.validate_payout_data(
            amount=5000, currency="TZS", channel="bank", recipient_name="Jane Doe"
        )
        assert valid is True

    def test_rejects_unsupported_channel(self):
        valid, errors = PayoutValidator.validate_payout_data(
            amount=5000, currency="TZS", channel="crypto", recipient_name="Jane Doe"
        )
        assert valid is False
