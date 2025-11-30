from django.urls import path

from apps.providers.views import ArmtekSearchProxyView

urlpatterns = [
    path("armtek/search", ArmtekSearchProxyView.as_view(), name="armtek-search"),
]
