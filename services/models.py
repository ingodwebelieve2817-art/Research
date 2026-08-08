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
    promo_code = models.CharField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # 1. Auto-generate unique promo code if not set
        if not self.promo_code:
            import uuid
            business_prefix = "".join(filter(str.isalnum, self.business_name)).upper()[:4]
            random_suffix = str(uuid.uuid4())[:4].upper()
            self.promo_code = f"PROMO-{business_prefix}-{random_suffix}"

        # 2. Limit system to only ONE active provider at any time
        if self.is_active:
            ServiceProvider.objects.exclude(pk=self.pk).update(is_active=False)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["city", "category"]),
            models.Index(fields=["is_active"]),
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


class Review(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="reviews")
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, related_name="reviews")
    project = models.OneToOneField("projects.Project", on_delete=models.SET_NULL, null=True, blank=True, related_name="review")
    rating = models.PositiveSmallIntegerField(choices=[(i, f"{i} Stars") for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review ({self.rating}★) for {self.provider.business_name} by {self.customer.name}"


class Referral(models.Model):
    referrer = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="referral_records")
    referred_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="referral_info")
    created_at = models.DateTimeField(auto_now_add=True)
    rewarded = models.BooleanField(default=False)

    def __str__(self):
        return f"Referral: {self.referrer.business_name} -> {self.referred_user.username}"

