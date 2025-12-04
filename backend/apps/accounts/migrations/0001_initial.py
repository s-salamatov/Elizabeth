# mypy: ignore-errors

import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations, models

import backend.apps.accounts.models

COUNTRY_CHOICES = [
    ("RU", "🇷🇺 Россия"),
    ("KZ", "🇰🇿 Казахстан"),
    ("BY", "🇧🇾 Беларусь"),
]


def create_superuser(apps, schema_editor):
    user_model = apps.get_model("accounts", "User")
    email = getattr(settings, "SUPERUSER_EMAIL", None)
    password = getattr(settings, "SUPERUSER_PASSWORD", None)
    phone = getattr(settings, "SUPERUSER_PHONE", None)
    first_name = getattr(settings, "SUPERUSER_FIRST_NAME", "")
    last_name = getattr(settings, "SUPERUSER_LAST_NAME", "")
    country = getattr(settings, "SUPERUSER_COUNTRY", "RU")

    if not (email and password and phone):
        return
    if user_model.objects.filter(email=email).exists():
        return

    user = user_model.objects.create(
        email=email,
        password=make_password(password),
        phone_number=phone,
        first_name=first_name,
        last_name=last_name,
        is_staff=True,
        is_superuser=True,
        is_active=True,
    )
    settings_model = apps.get_model("accounts", "UserSettings")
    settings_model.objects.create(user=user, country=country)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text=(
                            "Designates that this user has all permissions without "
                            "explicitly assigning them."
                        ),
                        verbose_name="superuser status",
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        help_text="Телефон в международном формате",
                        max_length=128,
                        region=None,
                        unique=True,
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=150)),
                ("last_name", models.CharField(blank=True, max_length=150)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "date_joined",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "User",
                "verbose_name_plural": "Users",
            },
            managers=[
                ("objects", backend.apps.accounts.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="UserSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "default_search_source",
                    models.CharField(
                        choices=[("armtek", "Армтек")],
                        default="armtek",
                        max_length=64,
                    ),
                ),
                (
                    "country",
                    models.CharField(
                        blank=True,
                        choices=COUNTRY_CHOICES,
                        default="RU",
                        max_length=2,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="settings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "User settings",
                "verbose_name_plural": "User settings",
            },
        ),
        migrations.RunPython(create_superuser, migrations.RunPython.noop),
    ]
