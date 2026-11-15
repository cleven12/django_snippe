import pytest
from django.core.exceptions import ValidationError

from django_snippe.validators import (
    CurrencyValidator,
    PaymentValidator,
    PayoutValidator,
    PhoneValidator,
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
