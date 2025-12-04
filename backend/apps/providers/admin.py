from typing import TYPE_CHECKING, TypeAlias

from django.contrib import admin

from .models import ProviderAccount

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin as DjangoModelAdmin

    ProviderAccountAdminBase: TypeAlias = DjangoModelAdmin[ProviderAccount]
else:  # pragma: no cover - runtime fallback
    from django.contrib.admin import ModelAdmin as ProviderAccountAdminBase


@admin.register(ProviderAccount)
class ProviderAccountAdmin(ProviderAccountAdminBase):
    list_display = (
        "user",
        "provider_name",
        "login",
        "pin",
        "vkorg",
        "updated_at",
    )
    list_filter = ("provider_name", "created_at")
    search_fields = (
        "user__email",
        "user__phone_number",
        "login",
        "pin",
        "vkorg",
        "kunnr_rg",
    )
    readonly_fields = (
        "encrypted_password",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (None, {"fields": ("user", "provider_name", "login")}),
        (
            "Cached context (read only)",
            {
                "fields": (
                    "pin",
                    "vkorg",
                    "kunnr_rg",
                    "program",
                    "kunnr_za",
                    "incoterms",
                    "vbeln",
                ),
            },
        ),
        (
            "Service",
            {"fields": ("encrypted_password", "created_at", "updated_at")},
        ),
    )
