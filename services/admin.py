from django.contrib import admin
from .models import ServiceProvider, Review


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ("business_name", "category", "city", "whatsapp_number", "is_active", "reach_limit", "created_at")
    list_filter = ("category", "city", "is_active")
    search_fields = ("business_name", "city", "user__email")
    readonly_fields = ("created_at", "updated_at")

    def reach_limit(self, obj):
        return obj.reach_limit
    reach_limit.short_description = "Plan Reach"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("provider", "customer", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("provider__business_name", "customer__name", "comment")

