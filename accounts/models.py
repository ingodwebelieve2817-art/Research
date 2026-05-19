from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_PROVIDER = "provider"
    ROLE_CUSTOMER = "customer"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = [
        (ROLE_PROVIDER, "Service Provider"),
        (ROLE_CUSTOMER, "Customer"),
        (ROLE_ADMIN, "Admin"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_provider(self):
        return self.role == self.ROLE_PROVIDER

    def is_customer(self):
        return self.role == self.ROLE_CUSTOMER

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
