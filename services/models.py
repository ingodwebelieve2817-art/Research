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
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="provider_profile"
    )
    business_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=SERVICE_CATEGORIES)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="provider_logos/", blank=True, null=True)
    cover_image = models.ImageField(upload_to="provider_covers/", blank=True, null=True)

    # Location
    address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Nigeria")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Contact & socials
    whatsapp_number = models.CharField(max_length=20, blank=True)
    facebook_page_id = models.CharField(max_length=100, blank=True)
    facebook_page_token = models.TextField(blank=True)
    website = models.URLField(blank=True)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.business_name} ({self.get_category_display()})"

    @property
    def current_subscription(self):
        return self.subscriptions.filter(is_active=True).first()

    @property
    def customer_limit(self):
        sub = self.current_subscription
        if sub:
            return sub.plan.customer_limit
        return settings.PLAN_CUSTOMER_LIMITS["basic"]

    @property
    def customer_count(self):
        return self.customers.count()

    def can_accept_customer(self):
        return self.customer_count < self.customer_limit


class ProviderService(models.Model):
    """Individual services offered by a provider."""
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="offered_services")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_unit = models.CharField(max_length=50, default="per job", help_text="e.g. per hour, per job, per month")
    image = models.ImageField(upload_to="service_images/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} – {self.provider.business_name}"


class ProviderReview(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="reviews")
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="given_reviews"
    )
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("provider", "customer")

    def __str__(self):
        return f"{self.customer.username} → {self.provider.business_name} ({self.rating}★)"


class CustomerProfile(models.Model):
    """Customers registered under a specific provider."""
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="customers")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_profiles",
        null=True, blank=True,
    )
    # Allow walk-in / non-registered customers
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    opted_in_whatsapp = models.BooleanField(default=False)
    opted_in_facebook = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("provider", "phone")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} @ {self.provider.business_name}"
