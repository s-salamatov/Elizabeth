from __future__ import annotations

from typing import Any

from rest_framework import serializers

from elizabeth.apps.providers.models import ProviderAccount
from elizabeth.apps.search.parsers import split_pin_and_brand


class ArmtekSearchInputSerializer(serializers.Serializer[dict[str, Any]]):
    query: serializers.CharField = serializers.CharField(
        required=False, allow_blank=True
    )
    pin: serializers.CharField = serializers.CharField(required=False, allow_blank=True)
    brand: serializers.CharField = serializers.CharField(
        required=False, allow_blank=True
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        pin = attrs.get("pin")
        brand = attrs.get("brand")
        query = attrs.get("query")
        if not pin:
            if not query:
                raise serializers.ValidationError("Either pin or query is required")
            pin, parsed_brand = split_pin_and_brand(query)
            if parsed_brand and not brand:
                brand = parsed_brand
        attrs["pin"] = pin
        attrs["brand"] = brand or None
        return attrs


class ArmtekCredentialsSerializer(serializers.Serializer[dict[str, Any]]):
    login: serializers.CharField = serializers.CharField()
    password: serializers.CharField = serializers.CharField(write_only=True)
    pin: serializers.CharField = serializers.CharField(required=False, allow_blank=True)
    vkorg: serializers.CharField = serializers.CharField(
        required=False, allow_blank=True
    )
    kunnr_rg: serializers.CharField = serializers.CharField(
        required=False, allow_blank=True
    )
    program: serializers.CharField = serializers.CharField(
        required=False, allow_blank=True
    )
    kunnr_za: serializers.CharField = serializers.CharField(
        required=False, allow_blank=True
    )
    incoterms: serializers.IntegerField = serializers.IntegerField(required=False)
    vbeln: serializers.CharField = serializers.CharField(
        required=False, allow_blank=True
    )


class ProviderAccountSerializer(serializers.ModelSerializer[ProviderAccount]):
    class Meta:
        """Expose provider account fields."""

        model = ProviderAccount
        fields = [
            "id",
            "provider_name",
            "login",
            "created_at",
            "updated_at",
        ]
