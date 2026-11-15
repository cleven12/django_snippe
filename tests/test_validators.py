import pytest
from django.core.exceptions import ValidationError

from django_snippe.validators import (
    CurrencyValidator,
    PaymentValidator,
