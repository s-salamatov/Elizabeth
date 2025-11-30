from __future__ import annotations

from typing import Any, cast

from rest_framework import serializers

from elizabeth.apps.search.models import SearchRequest


class SearchInputSerializer(serializers.Serializer[dict[str, Any]]):
    """Single search payload."""

    query = cast(Any, serializers.CharField())
    source = cast(Any, serializers.CharField(default="armtek"))


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
        queries = attrs.get("queries") or []
        bulk_text = attrs.get("bulk_text") or ""
        if not queries and not bulk_text:
            raise serializers.ValidationError(
                "Provide either queries array or bulk_text"
            )
        attrs["queries"] = queries
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
