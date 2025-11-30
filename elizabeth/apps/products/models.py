from __future__ import annotations

from django.db import models


class Product(models.Model):
    artid = models.CharField(max_length=64)
    brand = models.CharField(max_length=128)
    pin = models.CharField(max_length=128)
    oem = models.CharField(max_length=128, blank=True)
    name = models.CharField(max_length=255)
    source = models.CharField(max_length=64, default="armtek")
    fetched_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("artid", "source")
        indexes = [
            models.Index(fields=["pin"]),
            models.Index(fields=["brand"]),
            models.Index(fields=["source", "fetched_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.pin} ({self.brand})"


class ProductDetails(models.Model):
    product = models.OneToOneField(
        Product, related_name="details", on_delete=models.CASCADE
    )
    image_url = models.URLField(blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    analog_code = models.CharField(max_length=128, blank=True)
    fetched_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Details for {self.product_id}" if self.product_id else "Detached details"
