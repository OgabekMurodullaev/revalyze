from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, VerificationOtp, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "role", "is_verified", "is_active", "is_staff")
    list_filter = ("role", "is_verified", "is_staff", "is_superuser")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)
    readonly_fields = ("last_login", "date_joined")

    fieldsets = (
        ("Account Info", {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "role", "is_verified", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role", "is_verified"),
        }),
    )


@admin.register(VerificationOtp)
class VerificationOtpAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "is_active", "expires_in")
    list_filter = ("is_active",)
    search_fields = ("user__email", "code")
    ordering = ("-expires_in",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "location", "phone_number", "resume_count")
    search_fields = ("user__email", "location", "phone_number")
    list_filter = ("location",)
    readonly_fields = ("resume_count",)