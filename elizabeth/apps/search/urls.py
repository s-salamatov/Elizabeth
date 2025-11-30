from django.urls import path

from elizabeth.apps.search.views import BulkSearchView, SearchDetailView, SearchView

urlpatterns = [
    path("", SearchView.as_view(), name="search"),
    path("bulk", BulkSearchView.as_view(), name="search-bulk"),
    path("<int:pk>", SearchDetailView.as_view(), name="search-detail"),
]
