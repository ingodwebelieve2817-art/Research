from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "phone", "is_phone_verified", "referred_by", "is_active", "created_at")
    fieldsets = UserAdmin.fieldsets + (
        ("Extra", {"fields": ("phone", "avatar", "is_phone_verified", "referred_by")}),
    )
