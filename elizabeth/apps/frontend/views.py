from __future__ import annotations

from typing import Any

from django.views.generic import TemplateView


class SearchPageView(TemplateView):
    template_name = "frontend/search.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:  # pragma: no cover - template context
        ctx = super().get_context_data(**kwargs)
        ctx["api_base"] = "/api/v1"
        return ctx
