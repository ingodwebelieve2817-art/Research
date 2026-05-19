from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "city", "service_interest", "opted_in_whatsapp", "opted_in_facebook", "is_active", "added_at")
    list_filter = ("service_interest", "city", "opted_in_whatsapp", "opted_in_facebook", "is_active")
    search_fields = ("name", "phone", "city")
    list_editable = ("is_active", "opted_in_whatsapp", "opted_in_facebook")

    # ── ADD YOUR DATASET HERE ──────────────────────────────────────────────
    # You can add customers one by one from this admin panel,
    # or bulk import via: python manage.py import_customers your_file.csv
    # ──────────────────────────────────────────────────────────────────────
