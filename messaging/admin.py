from django.contrib import admin
from .models import Outreach, OutreachLog


class OutreachLogInline(admin.TabularInline):
    model = OutreachLog
    extra = 0
    readonly_fields = ("sent_at",)


@admin.register(Outreach)
class OutreachAdmin(admin.ModelAdmin):
    list_display = ("provider", "target_city", "target_category", "channel",
                    "status", "total_matched", "total_sent", "total_failed", "created_at")
    list_filter = ("status", "channel", "target_category")
    inlines = [OutreachLogInline]
