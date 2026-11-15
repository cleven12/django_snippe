from unittest.mock import patch

import pytest

from django_snippe.conf import get_client, get_setting
from django_snippe.exceptions import SnippeConfigError


def test_get_setting_returns_configured_value(settings):
    settings.SNIPPE_API_KEY = "snp_live_abc"
    assert get_setting("API_KEY") == "snp_live_abc"


def test_get_setting_returns_default_when_missing():
    assert get_setting("MISSING_SETTING", default="fallback") == "fallback"


def test_get_setting_raises_when_required_and_missing():
    with pytest.raises(SnippeConfigError):
        get_setting("MISSING_REQUIRED", required=True)


@patch("snippe.Snippe")
def test_get_client_builds_client_from_settings(mock_snippe_cls, settings):
    settings.SNIPPE_API_KEY = "snp_live_abc"
    settings.SNIPPE_TIMEOUT = 15.0
    get_client()
    assert mock_snippe_cls.called


def test_get_client_requires_api_key(settings):
    settings.SNIPPE_API_KEY = None
    with pytest.raises(SnippeConfigError):
        get_client()
