from django.urls import include, path

urlpatterns = [
    path("payments/", include("django_snippe.urls")),
]
