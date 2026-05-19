from django.contrib import admin
from .models import SubscriptionPlan, Subscription, Payment


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "tier", "price_monthly", "customer_limit",
                    "whatsapp_enabled", "facebook_enabled", "bulk_messaging")


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("provider", "plan", "status", "started_at", "expires_at", "is_active")
    list_filter = ("status", "is_active", "plan")
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("subscription", "amount", "currency", "status", "gateway", "paid_at")
    list_filter = ("status", "gateway")
