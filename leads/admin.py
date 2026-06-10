from django.contrib import admin
from .models import LinkedInLead


@admin.register(LinkedInLead)
class LinkedInLeadAdmin(admin.ModelAdmin):
    list_display = ["full_name", "company", "city", "engagement_type", "status", "dm_sent", "created_at"]
    list_filter = ["status", "engagement_type", "dm_sent", "country"]
    search_fields = ["full_name", "email", "company", "city", "linkedin_url"]
    list_editable = ["status", "dm_sent"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Contact Info", {
            "fields": ("full_name", "email", "phone", "linkedin_url")
        }),
        ("Professional Info", {
            "fields": ("job_title", "company", "city", "country")
        }),
        ("Lead Source", {
            "fields": ("engagement_type", "post_url")
        }),
        ("Pipeline", {
            "fields": ("status", "notes", "dm_sent", "dm_sent_at")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
