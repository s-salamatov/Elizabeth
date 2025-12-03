from django.urls import include, path

urlpatterns = [
    path("auth/", include("backend.apps.accounts.urls")),
    path("search/", include("backend.apps.search.urls")),
    path("products/", include("backend.apps.products.urls")),
    path("providers/", include("backend.apps.providers.urls")),
]
