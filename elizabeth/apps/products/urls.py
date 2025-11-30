from django.urls import path

from apps.products.views import (
    ProductDetailView,
    ProductDetailsIngestView,
    ProductListView,
)

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path("<int:pk>", ProductDetailView.as_view(), name="product-detail"),
    path("<int:pk>/details", ProductDetailsIngestView.as_view(), name="product-details"),
]
