from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "is_author",
        "is_staff",
    ]
    list_filter = ["is_author", "is_staff", "is_superuser", "is_active"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Права для опросов", {"fields": ("is_author",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Права для опросов", {"fields": ("is_author",)}),
    )
