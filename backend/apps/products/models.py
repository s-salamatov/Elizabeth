from __future__ import annotations

from django.conf import settings
from django.db import models


class DetailsRequestStatus(models.TextChoices):
    """States of detail collection."""

    PENDING = "pending", "Pending"
    READY = "ready", "Ready"
    FAILED = "failed", "Failed"


class Product(models.Model):
    """Stored product search result."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
    )
    search_request = models.ForeignKey(
        "search.SearchRequest",
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
    )
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
        """Uniqueness and indexes for product table."""

        unique_together = ("search_request", "artid")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["search_request"]),
            models.Index(fields=["pin"]),
            models.Index(fields=["brand"]),
            models.Index(fields=["source", "fetched_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.pin} ({self.brand})"


class ProductDetailsRequest(models.Model):
    """Correlation record for extension callbacks."""

    product = models.OneToOneField(
        Product, related_name="details_request", on_delete=models.CASCADE
    )
    request_id = models.UUIDField(unique=True)
    status = models.CharField(
        max_length=16,
        choices=DetailsRequestStatus.choices,
        default=DetailsRequestStatus.PENDING,
    )
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover - display helper
        return (
            f"Details request for {self.product_id}"
            if self.product_id
            else "Orphan request"
        )


class ProductDetails(models.Model):
    """HTML-scraped characteristics for a product."""

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
        return (
            f"Details for {self.product_id}" if self.product_id else "Detached details"
        )
