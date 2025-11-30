from django.urls import include, path

urlpatterns = [
    path("auth/", include("elizabeth.apps.accounts.urls")),
    path("search/", include("elizabeth.apps.search.urls")),
    path("products/", include("elizabeth.apps.products.urls")),
    path("providers/", include("elizabeth.apps.providers.urls")),
]
