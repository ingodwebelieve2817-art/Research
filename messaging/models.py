from django.db import models
from django.conf import settings


class MessageCampaign(models.Model):
    """A broadcast message sent to a provider's customer list."""
    CHANNEL_WHATSAPP = "whatsapp"
    CHANNEL_FACEBOOK = "facebook"
    CHANNEL_BOTH = "both"
    CHANNEL_CHOICES = [
        (CHANNEL_WHATSAPP, "WhatsApp"),
        (CHANNEL_FACEBOOK, "Facebook Marketplace"),
        (CHANNEL_BOTH, "WhatsApp + Facebook"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_QUEUED = "queued"
    STATUS_SENDING = "sending"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_QUEUED, "Queued"),
        (STATUS_SENDING, "Sending"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
    ]

    provider = models.ForeignKey(
        "services.ServiceProvider", on_delete=models.CASCADE, related_name="campaigns"
    )
    title = models.CharField(max_length=200)
    message_body = models.TextField()
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_WHATSAPP)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    total_recipients = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_channel_display()}] {self.title} – {self.provider.business_name}"


class MessageLog(models.Model):
    """Individual delivery record per customer per campaign."""
    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"
    STATUS_DELIVERED = "delivered"
    STATUS_READ = "read"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SENT, "Sent"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_READ, "Read"),
        (STATUS_FAILED, "Failed"),
    ]

    campaign = models.ForeignKey(MessageCampaign, on_delete=models.CASCADE, related_name="logs")
    customer = models.ForeignKey(
        "services.CustomerProfile", on_delete=models.CASCADE, related_name="message_logs"
    )
    channel = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    external_message_id = models.CharField(max_length=200, blank=True)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.campaign.title} → {self.customer.name} ({self.status})"


class WhatsAppTemplate(models.Model):
    """Pre-approved WhatsApp message templates."""
    provider = models.ForeignKey(
        "services.ServiceProvider", on_delete=models.CASCADE, related_name="wa_templates",
        null=True, blank=True,
    )
    name = models.CharField(max_length=100)
    template_id = models.CharField(max_length=200, blank=True, help_text="Meta template name/ID")
    body = models.TextField()
    language = models.CharField(max_length=10, default="en")
    is_global = models.BooleanField(default=False, help_text="Available to all providers")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
