from django.db import models


class Outreach(models.Model):
    """
    Represents one outreach campaign the platform runs for a provider.
    Created automatically when a provider subscribes or renews their plan.
    The platform picks matching customers and messages them on WhatsApp/Facebook.
    """
    CHANNEL_WHATSAPP = "whatsapp"
    CHANNEL_FACEBOOK = "facebook"
    CHANNEL_BOTH = "both"
    CHANNEL_CHOICES = [
        (CHANNEL_WHATSAPP, "WhatsApp"),
        (CHANNEL_FACEBOOK, "Facebook"),
        (CHANNEL_BOTH, "WhatsApp + Facebook"),
    ]

    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_DONE = "done"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RUNNING, "Running"),
        (STATUS_DONE, "Done"),
        (STATUS_FAILED, "Failed"),
    ]

    provider = models.ForeignKey(
        "services.ServiceProvider",
        on_delete=models.CASCADE,
        related_name="outreaches",
    )
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_WHATSAPP)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # Auto-filled from provider city + category at the time of outreach
    target_city = models.CharField(max_length=100)
    target_category = models.CharField(max_length=50)
    reach_limit = models.PositiveIntegerField()

    total_matched = models.PositiveIntegerField(default=0)   # customers found in dataset
    total_sent = models.PositiveIntegerField(default=0)      # messages successfully sent
    total_failed = models.PositiveIntegerField(default=0)    # messages that failed

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Outreach for {self.provider.business_name} — {self.status} ({self.total_sent} sent)"


class OutreachLog(models.Model):
    """One row per customer per outreach — tracks delivery status."""
    STATUS_SENT = "sent"
    STATUS_DELIVERED = "delivered"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_SENT, "Sent"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_FAILED, "Failed"),
    ]

    outreach = models.ForeignKey(Outreach, on_delete=models.CASCADE, related_name="logs")
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="outreach_logs",
    )
    channel = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SENT)
    external_message_id = models.CharField(max_length=200, blank=True)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.outreach} → {self.customer.name} ({self.status})"
