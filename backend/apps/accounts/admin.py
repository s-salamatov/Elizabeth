from typing import TYPE_CHECKING, Any, TypeAlias

from django import forms
from django.contrib import admin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User, UserSettings

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin as DjangoModelAdmin
    from django.contrib.auth.admin import UserAdmin as DjangoUserAdminType
    from django.forms import ModelForm as DjangoModelForm

    UserModelForm: TypeAlias = DjangoModelForm[User]
    # django-stubs bounds UserAdmin to AbstractUser; our User extends AbstractBaseUser,
    # so annotate with Any to bypass the bound safely.
    UserAdminTyped: TypeAlias = DjangoUserAdminType[Any]
    UserSettingsAdminTyped: TypeAlias = DjangoModelAdmin[UserSettings]
else:  # pragma: no cover - runtime fallback (generics unsupported at runtime)
    from django.contrib.admin import ModelAdmin as UserSettingsAdminTyped
    from django.contrib.auth.admin import UserAdmin as UserAdminTyped
    from django.forms import ModelForm as UserModelForm


class UserCreationForm(UserModelForm):
    """Creation form that works with email-as-username users."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        """Model binding and fields exposed in the admin."""

        model = User
        fields = ("email", "phone_number", "first_name", "last_name")

    def clean_password2(self) -> str | None:
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(UserModelForm):
    """Update form that keeps password hashing intact."""

    password = ReadOnlyPasswordHashField(
        label="Password",
        help_text=(
            "Raw passwords are not stored, so there is no way to see "
            "this user's password, but you can change the password "
            'using <a href="../password/">this form</a>.'
        ),
    )

    class Meta:
        """Model binding and fields exposed in the admin."""

        model = User
        fields = (
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "password",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
            "last_login",
            "date_joined",
        )

    def clean_password(self) -> str | None:
        # Regardless of what the user provides, keep the hashed password.
        return self.initial.get("password")


@admin.register(User)
class UserAdmin(UserAdminTyped):
    """Admin UI for custom email-based users."""

    add_form = UserCreationForm
    form = UserChangeForm
    ordering = ("email",)
    list_display = (
        "email",
        "phone_number",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = (
        "email",
        "phone_number",
        "first_name",
        "last_name",
    )
    readonly_fields = ("date_joined", "last_login")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "phone_number")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "phone_number",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                ),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")


@admin.register(UserSettings)
class UserSettingsAdmin(UserSettingsAdminTyped):
    """Admin UI for per-user preferences."""

    list_display = (
        "user",
        "default_search_source",
        "country",
        "created_at",
        "updated_at",
    )
    list_filter = ("default_search_source", "country")
    search_fields = ("user__email", "user__phone_number")
    readonly_fields = ("created_at", "updated_at")
