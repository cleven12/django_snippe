import pytest
from django.core.exceptions import ValidationError

from django_snippe.models import SnippePayment, SnippePayout

pytestmark = pytest.mark.django_db
