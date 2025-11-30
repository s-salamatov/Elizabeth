from __future__ import annotations

from rest_framework import serializers

from apps.search.parsers import split_pin_and_brand


class ArmtekSearchInputSerializer(serializers.Serializer):
    query = serializers.CharField(required=False, allow_blank=True)
    pin = serializers.CharField(required=False, allow_blank=True)
    brand = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
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
