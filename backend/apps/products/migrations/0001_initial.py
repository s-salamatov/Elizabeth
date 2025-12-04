import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("artid", models.CharField(max_length=64)),
                ("brand", models.CharField(max_length=128)),
                ("pin", models.CharField(max_length=128)),
                ("oem", models.CharField(blank=True, max_length=128)),
                ("name", models.CharField(max_length=255)),
                ("source", models.CharField(default="armtek", max_length=64)),
                ("fetched_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "unique_together": {("artid", "source")},
            },
        ),
        migrations.CreateModel(
            name="ProductDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image_url", models.URLField(blank=True)),
                (
                    "weight",
                    models.DecimalField(
                        blank=True, decimal_places=3, max_digits=10, null=True
                    ),
                ),
                (
                    "length",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "width",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "height",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("analog_code", models.CharField(blank=True, max_length=128)),
                ("fetched_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="details",
                        to="products.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductDetailsRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("request_id", models.UUIDField(unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("ready", "Ready"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("last_error", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="details_request",
                        to="products.product",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["pin"], name="products_p_pin_ab1b65_idx"),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["brand"], name="products_p_brand_d1b85b_idx"),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(
                fields=["source", "fetched_at"], name="products_p_source__9006b7_idx"
            ),
        ),
    ]
