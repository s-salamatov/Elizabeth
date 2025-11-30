from django.urls import path

from elizabeth.apps.providers.views import (
    ArmtekCredentialsView,
    ArmtekSearchProxyView,
    ProviderAccountListView,
)

urlpatterns = [
    path("", ProviderAccountListView.as_view(), name="provider-account-list"),
    path("armtek/search", ArmtekSearchProxyView.as_view(), name="armtek-search"),
    path(
        "armtek/credentials", ArmtekCredentialsView.as_view(), name="armtek-credentials"
    ),
]
