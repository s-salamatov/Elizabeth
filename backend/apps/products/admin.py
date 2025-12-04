from typing import TYPE_CHECKING, Any, TypeAlias

from django.contrib import admin

from .models import Product, ProductDetails, ProductDetailsRequest

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin as DjangoModelAdmin
    from django.contrib.admin.options import StackedInline as DjangoStackedInline

    ProductAdminBase: TypeAlias = DjangoModelAdmin[Product]
    ProductDetailsAdminBase: TypeAlias = DjangoModelAdmin[ProductDetails]
    ProductDetailsRequestAdminBase: TypeAlias = DjangoModelAdmin[ProductDetailsRequest]
    ProductDetailsInlineBase: TypeAlias = DjangoStackedInline[ProductDetails, Any]
    ProductDetailsRequestInlineBase: TypeAlias = DjangoStackedInline[
        ProductDetailsRequest, Any
    ]
else:  # pragma: no cover - runtime fallback
    from django.contrib.admin import ModelAdmin as ProductAdminBase
    from django.contrib.admin import ModelAdmin as ProductDetailsAdminBase
    from django.contrib.admin import ModelAdmin as ProductDetailsRequestAdminBase
    from django.contrib.admin.options import StackedInline as ProductDetailsInlineBase
    from django.contrib.admin.options import (
        StackedInline as ProductDetailsRequestInlineBase,
    )


class ProductDetailsInline(ProductDetailsInlineBase):
    model = ProductDetails
    extra = 0
    readonly_fields = (
        "image_url",
        "weight",
        "length",
        "width",
        "height",
        "analog_code",
        "fetched_at",
        "created_at",
        "updated_at",
    )


class ProductDetailsRequestInline(ProductDetailsRequestInlineBase):
    model = ProductDetailsRequest
    extra = 0
    readonly_fields = (
        "request_id",
        "status",
        "last_error",
        "created_at",
        "updated_at",
    )


@admin.register(Product)
class ProductAdmin(ProductAdminBase):
    list_display = (
        "id",
        "pin",
        "brand",
        "artid",
        "price",
        "currency",
        "available_quantity",
        "source",
        "fetched_at",
        "user",
    )
    list_filter = ("source", "brand", "fetched_at")
    search_fields = (
        "pin",
        "brand",
        "artid",
        "oem",
        "warehouse_code",
        "warehouse_partner",
        "user__email",
    )
    readonly_fields = ("created_at", "updated_at")
    inlines = [ProductDetailsInline, ProductDetailsRequestInline]


@admin.register(ProductDetailsRequest)
class ProductDetailsRequestAdmin(ProductDetailsRequestAdminBase):
    list_display = ("product", "request_id", "status", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("product__pin", "product__brand", "request_id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ProductDetails)
class ProductDetailsAdmin(ProductDetailsAdminBase):
    list_display = ("product", "fetched_at", "updated_at")
    search_fields = (
        "product__pin",
        "product__brand",
        "product__artid",
    )
    readonly_fields = ("created_at", "updated_at")
