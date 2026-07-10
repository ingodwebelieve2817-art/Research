from django.db import models


# ─────────────────────────────────────────────────────────────────────────────
# PLATFORM CUSTOMER DATASET
#
# These are people in various cities who will receive messages about
# local service providers operating in their city.
# Matching is done by city only — everyone in the same city as a provider
# gets the outreach message when that provider subscribes.
#
# HOW TO ADD YOUR DATASET LATER:
#   Option 1 — Bulk import from CSV (recommended):
#       python manage.py import_customers your_file.csv
#       CSV columns: name, phone, whatsapp_number, city
#       (whatsapp_number can be left blank — phone will be used instead)
#
#   Option 2 — Django Admin:
#       Go to /admin/ → Customers → Add Customer
#
#   Option 3 — Django shell:
#       python manage.py shell
#       >>> from customers.models import Customer
#       >>> Customer.objects.create(name="Ali", phone="+2348012345678", city="Lagos")
#
# ─────────────────────────────────────────────────────────────────────────────


class Customer(models.Model):
    """
    A person in the platform's contact database.
    Matched to providers purely by city.
    They never log in to this platform.
    """
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, unique=True)
    whatsapp_number = models.CharField(
        max_length=20, blank=True,
        help_text="Leave blank if same as phone. Must be in format +2348012345678"
    )
    city = models.CharField(
        max_length=100,
        help_text="City where this person lives"
    )
    opted_in_whatsapp = models.BooleanField(default=True)
    opted_in_facebook = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["city", "name"]
        indexes = [
            models.Index(fields=["city", "name"]),
        ]

    def effective_whatsapp(self):
        """Returns whatsapp_number if set, otherwise falls back to phone."""
        return self.whatsapp_number if self.whatsapp_number else self.phone

    def __str__(self):
        return f"{self.name} | {self.city} | {self.phone}"
