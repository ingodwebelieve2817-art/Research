from django.contrib import admin
from .models import ServiceProvider, ProviderService, CustomerProfile, ProviderReview


class ProviderServiceInline(admin.TabularInline):
    model = ProviderService
    extra = 0


class CustomerProfileInline(admin.TabularInline):
    model = CustomerProfile
    extra = 0
    fields = ("name", "phone", "whatsapp_number", "opted_in_whatsapp", "opted_in_facebook")


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ("business_name", "category", "city", "is_verified", "is_active", "customer_count", "created_at")
    list_filter = ("category", "is_verified", "is_active", "country")
    search_fields = ("business_name", "city", "user__email")
    inlines = [ProviderServiceInline, CustomerProfileInline]

    def customer_count(self, obj):
        return obj.customers.count()
    customer_count.short_description = "Customers"


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "provider", "opted_in_whatsapp", "opted_in_facebook", "created_at")
    list_filter = ("opted_in_whatsapp", "opted_in_facebook")
    search_fields = ("name", "phone", "provider__business_name")


@admin.register(ProviderReview)
class ProviderReviewAdmin(admin.ModelAdmin):
    list_display = ("provider", "customer", "rating", "created_at")
    list_filter = ("rating",)
