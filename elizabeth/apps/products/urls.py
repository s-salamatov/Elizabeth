from django.urls import path

from elizabeth.apps.products.views import (
    ProductDetailsIngestView,
    ProductDetailsJobsView,
    ProductDetailsRequestView,
    ProductDetailsStatusView,
    ProductDetailView,
    ProductListView,
)

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path("<int:pk>", ProductDetailView.as_view(), name="product-detail"),
    path(
        "<int:pk>/details", ProductDetailsIngestView.as_view(), name="product-details"
    ),
    path(
        "details/request",
        ProductDetailsRequestView.as_view(),
        name="product-details-request",
    ),
    path(
        "details/status",
        ProductDetailsStatusView.as_view(),
        name="product-details-status",
    ),
    path("details/jobs", ProductDetailsJobsView.as_view(), name="product-details-jobs"),
]
