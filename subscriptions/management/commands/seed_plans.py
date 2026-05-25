"""
python manage.py seed_plans

Creates / updates the three subscription tiers.
"""
from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionPlan

PLANS = [
    {
        "tier": "basic",
        "name": "Basic",
        "price_monthly": ₹100,
        "reach_limit": 1000,
        "whatsapp_enabled": False,
        "facebook_enabled": False,
        "description": (
            "Free plan. The platform will reach out to 5 potential customers "
            "in your city who need your type of service."
        ),
    },
    {
        "tier": "pro",
        "name": "Pro",
        "price_monthly": ₹500,
        "reach_limit": 5000,
        "whatsapp_enabled": True,
        "facebook_enabled": False,
        "description": (
            "The platform will reach out to 100 potential customers via WhatsApp "
            "in your city who need your type of service."
        ),
    },
    {
        "tier": "max",
        "name": "Max",
        "price_monthly":₹1500,
        "reach_limit": 10000,
        "whatsapp_enabled": True,
        "facebook_enabled": True,
        "description": (
            "The platform will reach out to 10,000 potential customers via "
            "WhatsApp AND Facebook in your city who need your type of service."
        ),
    },
]


class Command(BaseCommand):
    help = "Seed Basic / Pro / Max subscription plans"

    def handle(self, *args, **options):
        for data in PLANS:
            plan, created = SubscriptionPlan.objects.update_or_create(
                tier=data["tier"], defaults=data
            )
            verb = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{verb}: {plan}"))
