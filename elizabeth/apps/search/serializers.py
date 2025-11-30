from __future__ import annotations

from rest_framework import serializers

from apps.search.models import SearchRequest


class SearchInputSerializer(serializers.Serializer):
    query = serializers.CharField()
    source = serializers.CharField(default="armtek")


class BulkSearchSerializer(serializers.Serializer):
    queries = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )
    bulk_text = serializers.CharField(required=False, allow_blank=True)
    source = serializers.CharField(default="armtek")

    def validate(self, attrs):
        queries = attrs.get("queries") or []
        bulk_text = attrs.get("bulk_text") or ""
        if not queries and not bulk_text:
            raise serializers.ValidationError("Provide either queries array or bulk_text")
        attrs["queries"] = queries
        attrs["bulk_text"] = bulk_text
        return attrs


class SearchRequestSerializer(serializers.ModelSerializer):
    class Meta:
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
