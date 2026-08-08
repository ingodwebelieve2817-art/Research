from django.db import models
from django.conf import settings
from django.utils import timezone


class SubscriptionPlan(models.Model):
    TIER_BASIC = "basic"
    TIER_PRO = "pro"
    TIER_MAX = "max"
    TIER_CHOICES = [
        (TIER_BASIC, "Basic"),
        (TIER_PRO, "Pro"),
        (TIER_MAX, "Max"),
    ]

    tier = models.CharField(max_length=10, choices=TIER_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2)

    # How many people from the platform's customer dataset
    # will be contacted on behalf of this provider per campaign
    reach_limit = models.PositiveIntegerField(
        help_text="Number of customers the platform will reach out to for this provider"
    )

    whatsapp_enabled = models.BooleanField(default=False)
    facebook_enabled = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["price_monthly"]

    def __str__(self):
        return f"{self.name} — reach {self.reach_limit} customers / ${self.price_monthly}/mo"


class Subscription(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_EXPIRED = "expired"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_EXPIRED, "Expired"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    provider = models.ForeignKey(
        "services.ServiceProvider",
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    payment_reference = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "status"]),
        ]

    def __str__(self):
        return f"{self.provider.business_name} — {self.plan.name} ({self.status})"

    def days_remaining(self):
        if self.expires_at:
            return max(0, (self.expires_at - timezone.now()).days)
        return None


class Payment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    gateway = models.CharField(max_length=50, blank=True, help_text="e.g. Stripe, Paystack")
    transaction_id = models.CharField(max_length=200, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} — {self.status} — {self.amount} {self.currency}"
