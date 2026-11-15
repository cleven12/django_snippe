from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SnippePayment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("reference", models.CharField(max_length=100, unique=True)),
                (
                    "payment_type",
                    models.CharField(
                        choices=[
                            ("mobile", "Mobile Money"),
                            ("card", "Card"),
                            ("dynamic-qr", "QR Code"),
                        ],
                        max_length=20,
                    ),
                ),
                ("amount", models.PositiveIntegerField()),
                ("currency", models.CharField(max_length=10)),
                ("phone_number", models.CharField(max_length=20)),
                (
                    "status",
                    models.CharField(
