from django.conf import settings
from django.db import models


# todo: amend user model to extend fields
class UserSettings(models.Model):
    """Per-user application preferences."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="settings", on_delete=models.CASCADE
    )
    default_search_source = models.CharField(max_length=64, default="armtek")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Django meta options."""

        verbose_name = "User settings"
        verbose_name_plural = "User settings"

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Settings for {self.user}" if self.user_id else "Orphan settings"
