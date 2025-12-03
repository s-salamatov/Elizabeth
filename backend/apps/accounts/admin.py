from typing import cast

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from backend.apps.accounts.models import User, UserSettings


class UserCreationForm(forms.ModelForm):  # type: ignore[type-arg]
    """Creation form that works with email-based auth."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        """Meta options for user creation form."""

        model = User
        fields = ("email", "phone_number", "first_name", "last_name")

    def clean_password2(self) -> str | None:
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit: bool = True) -> User:
        user = cast(User, super().save(commit=False))
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):  # type: ignore[type-arg]
    """Update form that shows hashed password."""

    password = ReadOnlyPasswordHashField(label=("Password"))

    class Meta:
        """Meta options for user change form."""

        model = User
        fields = (
            "email",
            "password",
            "phone_number",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )


@admin.register(User)
class UserAdmin(BaseUserAdmin):  # type: ignore[type-arg]
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ("email", "phone_number", "is_staff", "is_superuser")
    list_filter = ("is_staff", "is_superuser")
    search_fields = ("email", "phone_number", "first_name", "last_name")
    ordering = ("email",)
    readonly_fields = ("date_joined", "last_login")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone_number")}),
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
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        "user",
        "country",
        "default_search_source",
        "created_at",
        "updated_at",
    )
    list_select_related = ("user",)
    list_filter = ("country", "default_search_source")
