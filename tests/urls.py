from django.urls import path, include

urlpatterns = [
    path("payments/", include("django_snippe.urls")),
]
