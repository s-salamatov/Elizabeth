from __future__ import annotations

from rest_framework import serializers

from apps.products.models import Product, ProductDetails


class ProductDetailsSerializer(serializers.ModelSerializer):
    class Meta:
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


class ProductDetailsInputSerializer(serializers.Serializer):
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


class ProductSerializer(serializers.ModelSerializer):
    details = ProductDetailsSerializer(read_only=True)

    class Meta:
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
        ]
