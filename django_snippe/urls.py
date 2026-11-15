"""URL configuration for django_snippe webhook endpoints."""

from django.urls import path

from .views import SnippeWebhookView

app_name = "django_snippe"

urlpatterns = [
    path("webhook/", SnippeWebhookView.as_view(), name="webhook"),
]
