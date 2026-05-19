from django.contrib import admin
from .models import MessageCampaign, MessageLog, WhatsAppTemplate


class MessageLogInline(admin.TabularInline):
    model = MessageLog
    extra = 0
    readonly_fields = ("sent_at", "delivered_at", "read_at")


@admin.register(MessageCampaign)
class MessageCampaignAdmin(admin.ModelAdmin):
    list_display = ("title", "provider", "channel", "status", "total_recipients",
                    "sent_count", "failed_count", "created_at")
    list_filter = ("channel", "status")
    inlines = [MessageLogInline]


@admin.register(WhatsAppTemplate)
class WhatsAppTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "template_id", "language", "is_global", "provider")
    list_filter = ("is_global", "language")
