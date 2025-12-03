from __future__ import annotations

from typing import Any, cast

from rest_framework import serializers

from backend.apps.search.models import SearchRequest
from backend.apps.search.parsers import split_bulk_input, split_pin_and_brand


class SearchInputSerializer(serializers.Serializer[dict[str, Any]]):
    """Single search payload."""

    query = cast(Any, serializers.CharField())
    source = cast(Any, serializers.CharField(default="armtek"))

    def validate_query(self, value: str) -> str:
        try:
            split_pin_and_brand(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return value


class BulkSearchSerializer(serializers.Serializer[dict[str, Any]]):
    """Bulk search payload."""

    queries = cast(
        Any,
        serializers.ListField(
            child=serializers.CharField(), required=False, allow_empty=True
        ),
    )
    bulk_text = cast(Any, serializers.CharField(required=False, allow_blank=True))
    source = cast(Any, serializers.CharField(default="armtek"))

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        list_queries = attrs.get("queries") or []
        bulk_text = attrs.get("bulk_text") or ""
        combined = list(list_queries)
        if bulk_text:
            combined.extend(split_bulk_input(bulk_text))
        combined = [item.strip() for item in combined if item and item.strip()]
        if not combined:
            raise serializers.ValidationError(
                "Provide either queries array or bulk_text"
            )
        for query in combined:
            try:
                split_pin_and_brand(query)
            except ValueError as exc:
                raise serializers.ValidationError(str(exc)) from exc
        attrs["queries"] = combined
        attrs["bulk_text"] = bulk_text
        return attrs


class SearchRequestSerializer(serializers.ModelSerializer[SearchRequest]):
    """Search history serialization."""

    class Meta:
        """Search request serialization config."""

        model = SearchRequest
        fields = [
            "id",
            "source",
            "query_string",
            "status",
            "total_items",
            "created_at",
            "updated_at",
        ]
