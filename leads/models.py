from django.db import models


ENGAGEMENT_TYPES = [
    ("comment", "Comment"),
    ("like", "Like"),
    ("share", "Share"),
    ("poll_vote", "Poll Vote"),
    ("profile_view", "Profile View"),
    ("newsletter", "Newsletter Subscriber"),
    ("dm", "Direct Message"),
    ("other", "Other"),
]

LEAD_STATUSES = [
    ("new", "New"),
    ("contacted", "Contacted"),
    ("replied", "Replied"),
    ("qualified", "Qualified"),
    ("converted", "Converted"),
    ("dead", "Dead"),
]


class LinkedInLead(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    linkedin_url = models.URLField(blank=True)

    job_title = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default="Nigeria")

    engagement_type = models.CharField(
        max_length=30, choices=ENGAGEMENT_TYPES, default="other"
    )
    post_url = models.URLField(blank=True, help_text="LinkedIn post that triggered this lead")

    status = models.CharField(max_length=20, choices=LEAD_STATUSES, default="new")
    notes = models.TextField(blank=True)

    dm_sent = models.BooleanField(default=False)
    dm_sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "LinkedIn Lead"
        verbose_name_plural = "LinkedIn Leads"

    def __str__(self):
        return f"{self.full_name} | {self.engagement_type} | {self.status}"

    @property
    def first_name(self):
        return self.full_name.split()[0] if self.full_name else ""
