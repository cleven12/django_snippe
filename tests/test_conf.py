from unittest.mock import patch

import pytest

from django_snippe.conf import get_client, get_setting
from django_snippe.exceptions import SnippeConfigError


def test_get_setting_returns_configured_value(settings):
    settings.SNIPPE_API_KEY = "snp_live_abc"
    assert get_setting("API_KEY") == "snp_live_abc"

