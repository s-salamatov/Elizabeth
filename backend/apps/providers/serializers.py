from __future__ import annotations

from typing import Any, cast

from rest_framework import serializers

from backend.apps.providers.models import ProviderAccount
from backend.apps.search.parsers import split_pin_and_brand


class ArmtekSearchInputSerializer(serializers.Serializer[dict[str, Any]]):
    query: serializers.CharField = serializers.CharField(
        required=False, allow_blank=True
    )
    pin: serializers.CharField = serializers.CharField(required=False, allow_blank=True)
    brand: serializers.CharField = serializers.CharField(
        required=False, allow_blank=True
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        pin = (attrs.get("pin") or "").strip()
        brand = (attrs.get("brand") or "").strip()
        query = (attrs.get("query") or "").strip()

        if query:
            try:
                pin, brand = split_pin_and_brand(query)
            except ValueError as exc:
                raise serializers.ValidationError(str(exc)) from exc
        else:
            if not pin or not brand:
                raise serializers.ValidationError("Укажите артикул и бренд")
            query = f"{pin}_{brand}"

        attrs["pin"] = pin
        attrs["brand"] = brand
        attrs["query"] = query
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

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        login = (attrs.get("login") or "").strip()
        password = (attrs.get("password") or "").strip()
        if not login or not password:
            raise serializers.ValidationError("Login and password are required")

        incoterms_raw: Any | None = attrs.get("incoterms")
        if incoterms_raw in ("", None):
            incoterms = None
        else:
            try:
                incoterms = int(cast(int | str, incoterms_raw))
            except (TypeError, ValueError) as exc:
                raise serializers.ValidationError(
                    "INCOTERMS must be an integer"
                ) from exc
        attrs["incoterms"] = incoterms
        for key in ("pin", "vkorg", "kunnr_rg", "program", "kunnr_za", "vbeln"):
            attrs[key] = (attrs.get(key) or "").strip() or None
        attrs["login"] = login
        attrs["password"] = password
        return attrs


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
