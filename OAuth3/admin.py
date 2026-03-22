from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AppUser, MFAChallenge


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    model = AppUser
    ordering = ("id",)
    list_display = (
        "id",
        "email",
        "nombres",
        "apellidos",
        "is_active",
        "is_staff",
        "is_email_verified",
        "mfa_enabled",
    )

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Información personal", {"fields": ("nombres", "apellidos")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "is_email_verified", "mfa_enabled", "groups", "user_permissions")}),
        ("Fechas", {"fields": ("last_login", "last_login_at", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "nombres", "apellidos", "password1", "password2", "is_active", "is_staff"),
        }),
    )

    search_fields = ("email", "nombres", "apellidos")


@admin.register(MFAChallenge)
class MFAChallengeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "purpose", "channel", "expires_at", "consumed_at", "attempts")
    search_fields = ("user__email",)