import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SnippePayment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reference", models.CharField(max_length=100, unique=True)),
                ("payment_type", models.CharField(
                    choices=[("mobile", "Mobile Money"), ("card", "Card"), ("dynamic-qr", "QR Code")],
                    max_length=20,
                )),
                ("amount", models.PositiveIntegerField()),
                ("currency", models.CharField(max_length=10)),
                ("phone_number", models.CharField(max_length=20)),
                ("status", models.CharField(
                    choices=[
                        ("pending", "Pending"),
                        ("completed", "Completed"),
                        ("failed", "Failed"),
                        ("expired", "Expired"),
                        ("voided", "Voided"),
                    ],
                    default="pending",
                    max_length=20,
                )),
                ("payment_url", models.URLField(blank=True, null=True)),
                ("payment_qr_code", models.TextField(blank=True, null=True)),
                ("payment_token", models.CharField(blank=True, max_length=100, null=True)),
                ("webhook_url", models.URLField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Payment",
                "verbose_name_plural": "Payments",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="SnippePayout",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reference", models.CharField(max_length=100, unique=True)),
                ("channel", models.CharField(
                    choices=[("mobile", "Mobile Money"), ("bank", "Bank Transfer")],
                    max_length=20,
                )),
                ("amount", models.PositiveIntegerField()),
                ("currency", models.CharField(default="TZS", max_length=10)),
                ("recipient_name", models.CharField(max_length=100)),
                ("recipient_phone", models.CharField(blank=True, max_length=20, null=True)),
                ("recipient_bank", models.CharField(blank=True, max_length=50, null=True)),
                ("recipient_account", models.CharField(blank=True, max_length=50, null=True)),
                ("status", models.CharField(
                    choices=[
                        ("pending", "Pending"),
                        ("completed", "Completed"),
                        ("failed", "Failed"),
                        ("reversed", "Reversed"),
                    ],
                    default="pending",
                    max_length=20,
                )),
                ("narration", models.CharField(blank=True, max_length=255, null=True)),
                ("failure_reason", models.TextField(blank=True, null=True)),
                ("webhook_url", models.URLField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Payout",
                "verbose_name_plural": "Payouts",
                "ordering": ["-created_at"],
            },
        ),
    ]
