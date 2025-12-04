from typing import TYPE_CHECKING, TypeAlias

from django.contrib import admin

from .models import SearchRequest

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin as DjangoModelAdmin

    SearchRequestAdminBase: TypeAlias = DjangoModelAdmin[SearchRequest]
else:  # pragma: no cover - runtime fallback
    from django.contrib.admin import ModelAdmin as SearchRequestAdminBase


@admin.register(SearchRequest)
class SearchRequestAdmin(SearchRequestAdminBase):
    list_display = (
        "id",
        "user",
        "source",
        "status",
        "total_items",
        "created_at",
    )
    list_filter = ("status", "source", "created_at")
    search_fields = ("id", "user__email", "query_string")
    readonly_fields = ("created_at", "updated_at")
