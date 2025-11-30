from django.urls import path

from elizabeth.apps.providers.views import ArmtekSearchProxyView

urlpatterns = [
    path("armtek/search", ArmtekSearchProxyView.as_view(), name="armtek-search"),
]
