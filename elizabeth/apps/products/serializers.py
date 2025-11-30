from __future__ import annotations

from typing import Any

from rest_framework import serializers

from elizabeth.apps.products.models import (
    DetailsRequestStatus,
    Product,
    ProductDetails,
    ProductDetailsRequest,
)


class ProductDetailsSerializer(serializers.ModelSerializer[ProductDetails]):
    """Read-only representation of product details."""

    class Meta:
        """Product details read serializer config."""

        model = ProductDetails
        fields = [
            "image_url",
            "weight",
            "length",
            "width",
            "height",
            "analog_code",
            "fetched_at",
        ]


class ProductDetailsInputSerializer(serializers.Serializer[dict[str, Any]]):
    """Payload accepted from browser extension."""

    image_url = serializers.URLField(required=False, allow_blank=True)
    weight = serializers.DecimalField(
        max_digits=10, decimal_places=3, required=False, allow_null=True
    )
    length = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    width = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    height = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    analog_code = serializers.CharField(required=False, allow_blank=True)


class ProductSerializer(serializers.ModelSerializer[Product]):
    """Serialized product with optional details and request id."""

    details = ProductDetailsSerializer(read_only=True)
    details_status = serializers.SerializerMethodField()
    request_id = serializers.SerializerMethodField()

    class Meta:
        """Product read serializer with relations."""

        model = Product
        fields = [
            "id",
            "artid",
            "brand",
            "pin",
            "oem",
            "name",
            "source",
            "fetched_at",
            "details",
            "details_status",
            "request_id",
        ]

    def get_details_status(self, obj: Product) -> str:
        try:
            return obj.details_request.status
        except ProductDetailsRequest.DoesNotExist:
            return DetailsRequestStatus.PENDING

    def get_request_id(self, obj: Product) -> str | None:
        try:
            return str(obj.details_request.request_id)
        except ProductDetailsRequest.DoesNotExist:
            return None
