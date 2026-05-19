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
    customer_limit = models.PositiveIntegerField()
    whatsapp_enabled = models.BooleanField(default=False)
    facebook_enabled = models.BooleanField(default=False)
    bulk_messaging = models.BooleanField(default=False)
    analytics_enabled = models.BooleanField(default=False)
    priority_listing = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["price_monthly"]

    def __str__(self):
        return f"{self.name} – {self.customer_limit} customers / ${self.price_monthly}/mo"


class Subscription(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_EXPIRED = "expired"
    STATUS_CANCELLED = "cancelled"
    STATUS_TRIAL = "trial"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_EXPIRED, "Expired"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_TRIAL, "Trial"),
    ]

    provider = models.ForeignKey(
        "services.ServiceProvider", on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_TRIAL)
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    payment_reference = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.provider.business_name} – {self.plan.name} ({self.status})"

    def is_expired(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False

    def days_remaining(self):
        if self.expires_at:
            delta = self.expires_at - timezone.now()
            return max(0, delta.days)
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
    gateway = models.CharField(max_length=50, blank=True, help_text="e.g. Stripe, Paystack, Flutterwave")
    transaction_id = models.CharField(max_length=200, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} – {self.status} – {self.amount} {self.currency}"
