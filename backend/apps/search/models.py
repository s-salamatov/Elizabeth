from __future__ import annotations

from django.conf import settings
from django.db import models


class SearchStatus(models.TextChoices):
    """Lifecycle of a search request."""

    PENDING = "pending", "Pending"
    IN_PROGRESS = "in_progress", "In progress"
    DONE = "done", "Done"
    FAILED = "failed", "Failed"


class SearchRequest(models.Model):
    """History entry for bulk/single searches."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_requests",
    )
    source = models.CharField(max_length=64, default="armtek")
    query_string = models.TextField()
    status = models.CharField(
        max_length=32, choices=SearchStatus.choices, default=SearchStatus.PENDING
    )
    total_items = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Sort newest first for UX."""

        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Search {self.id} ({self.source})"
