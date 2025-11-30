from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.accounts.urls")),
    path("search/", include("apps.search.urls")),
    path("products/", include("apps.products.urls")),
    path("providers/", include("apps.providers.urls")),
]
