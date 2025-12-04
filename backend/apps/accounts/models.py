from typing import Any

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Country(models.TextChoices):
    RUSSIA = "RU", "🇷🇺 Россия"
    KAZAKHSTAN = "KZ", "🇰🇿 Казахстан"
    BELARUS = "BY", "🇧🇾 Беларусь"


class SearchSource(models.TextChoices):
    ARMTEK = "armtek", "Армтек"


class UserManager(BaseUserManager["User"]):
    """Manager for custom User model."""

    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "User":
        if not email:
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")
        if not extra_fields.get("phone_number"):
            raise ValueError("Phone number is required")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_active", True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user that uses email for authentication."""

    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(
        unique=True, help_text="Телефон в международном формате"
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number"]

    class Meta:
        """Meta options for custom user."""

        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.email


class UserSettings(models.Model):
    """Per-user application preferences."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="settings", on_delete=models.CASCADE
    )
    default_search_source = models.CharField(
        max_length=64, choices=SearchSource.choices, default=SearchSource.ARMTEK
    )
    country = models.CharField(
        max_length=2,
        choices=Country.choices,
        blank=True,
        default=Country.RUSSIA,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Django meta options."""

        verbose_name = "User settings"
        verbose_name_plural = "User settings"

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Settings for {self.user}" if self.user_id else "Orphan settings"
