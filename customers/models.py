from django.db import models


# ─────────────────────────────────────────────────────────────────────────────
# PLATFORM CUSTOMER DATASET
#
# These are NOT people who log in. These are real people (potential customers)
# whose contact details the platform owns.
#
# When a service provider subscribes to a plan, the platform automatically
# picks matching customers from this table (same city + matching service need)
# and sends them a WhatsApp / Facebook message about that provider.
#
# HOW TO ADD YOUR DATASET LATER:
#   Option 1 — Django Admin:
#       Go to /admin/ → Customers → Add Customer (one by one)
#
#   Option 2 — Bulk import from CSV (recommended):
#       Run:  python manage.py import_customers your_file.csv
#       (The import command is in customers/management/commands/import_customers.py)
#       CSV columns expected: name, phone, whatsapp_number, city, service_interest
#
#   Option 3 — Django shell (for developers):
#       python manage.py shell
#       >>> from customers.models import Customer
#       >>> Customer.objects.create(name="Ali", phone="+2348012345678", city="Lagos", service_interest="barber")
#
# ─────────────────────────────────────────────────────────────────────────────

SERVICE_INTEREST_CHOICES = [
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


class Customer(models.Model):
    """
    A person in the platform's contact database.
    They will receive messages about nearby service providers.
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
        help_text="City where this person lives / looks for services"
    )
    service_interest = models.CharField(
        max_length=50,
        choices=SERVICE_INTEREST_CHOICES,
        help_text="What type of service this person is likely to need"
    )
    opted_in_whatsapp = models.BooleanField(
        default=True,
        help_text="Can the platform send them WhatsApp messages?"
    )
    opted_in_facebook = models.BooleanField(
        default=False,
        help_text="Can the platform send them Facebook messages?"
    )
    is_active = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["city", "service_interest"]

    def effective_whatsapp(self):
        """Returns whatsapp_number if set, otherwise falls back to phone."""
        return self.whatsapp_number if self.whatsapp_number else self.phone

    def __str__(self):
        return f"{self.name} | {self.city} | {self.get_service_interest_display()}"
