import pytest
from django.core.exceptions import ValidationError

from django_snippe.models import SnippePayment, SnippePayout

pytestmark = pytest.mark.django_db


def make_payment(**overrides):
    defaults = dict(
        reference="PAY-1",
        payment_type=SnippePayment.PaymentType.MOBILE,
