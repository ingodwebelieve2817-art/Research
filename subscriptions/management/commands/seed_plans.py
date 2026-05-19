"""
python manage.py seed_plans

Creates the three subscription tiers if they don't already exist.
"""
from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionPlan


PLANS = [
    {
        "tier": "basic",
        "name": "Basic",
        "price_monthly": 0,
        "customer_limit": 5,
        "whatsapp_enabled": False,
        "facebook_enabled": False,
        "bulk_messaging": False,
        "analytics_enabled": False,
        "priority_listing": False,
        "description": "Perfect for getting started. List your business and manage up to 5 customers for free.",
    },
    {
        "tier": "pro",
        "name": "Pro",
        "price_monthly": 19,
        "customer_limit": 100,
        "whatsapp_enabled": True,
        "facebook_enabled": False,
        "bulk_messaging": True,
        "analytics_enabled": True,
        "priority_listing": False,
        "description": "For growing businesses. Reach up to 100 customers with WhatsApp bulk messaging and campaign analytics.",
    },
    {
        "tier": "max",
        "name": "Max",
        "price_monthly": 99,
        "customer_limit": 10000,
        "whatsapp_enabled": True,
        "facebook_enabled": True,
        "bulk_messaging": True,
        "analytics_enabled": True,
        "priority_listing": True,
        "description": "For established businesses. Reach up to 10,000 customers on WhatsApp AND Facebook Marketplace with priority listing.",
    },
]


class Command(BaseCommand):
    help = "Seed the three subscription plans (Basic / Pro / Max)"

    def handle(self, *args, **options):
        for data in PLANS:
            plan, created = SubscriptionPlan.objects.update_or_create(
                tier=data["tier"], defaults=data
            )
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action}: {plan}"))
