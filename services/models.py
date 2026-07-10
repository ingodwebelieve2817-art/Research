from django.db import models
from django.conf import settings


SERVICE_CATEGORIES = [
    ("barber", "Barber / Hair Stylist"),
    ("plumber", "Plumber"),
    ("electrician", "Electrician"),
    ("carpenter", "Carpenter"),
    ("painter", "Painter"),
    ("cleaner", "Cleaner"),
    ("mechanic", "Mechanic"),
    ("tailor", "Tailor"),
    ("tutor", "Tutor"),
    ("gardener", "Gardener"),
    ("photographer", "Photographer"),
    ("caterer", "Caterer"),
    ("other", "Other"),
]


class ServiceProvider(models.Model):
    """
    A local business that registers on the platform.
    They pay for a plan and the platform reaches out to
    matching customers in their city on their behalf.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="provider_profile",
    )
    business_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=SERVICE_CATEGORIES)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="provider_logos/", blank=True, null=True)

    # Location — used to match with customers in the same city
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=300, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Nigeria")

    # Contact details sent to customers when the platform reaches out
    whatsapp_number = models.CharField(
        max_length=20,
        help_text="Customers will be sent this number on WhatsApp"
    )
    facebook_page_url = models.URLField(
        blank=True,
        help_text="Your Facebook page link shared with customers"
    )
    website = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["city", "category"]),
        ]

    def __str__(self):
        return f"{self.business_name} ({self.get_category_display()}) — {self.city}"

    @property
    def active_subscription(self):
        return self.subscriptions.filter(is_active=True).first()

    @property
    def reach_limit(self):
        """How many customers the platform will contact for this provider."""
        sub = self.active_subscription
        if sub:
            return sub.plan.reach_limit
        return settings.PLAN_REACH_LIMITS["basic"]
