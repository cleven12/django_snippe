"""Unit tests for django_snippe.services and admin_actions."""

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory

from django_snippe import admin_actions, services
from django_snippe.admin import SnippePaymentAdmin, SnippePayoutAdmin, SnippeSessionAdmin
from django_snippe.models import SnippePayment, SnippePayout, SnippeSession
