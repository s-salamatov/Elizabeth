from __future__ import annotations

from django.views.generic import TemplateView


class FrontendAppView(TemplateView):
    template_name = "frontend/app.html"
