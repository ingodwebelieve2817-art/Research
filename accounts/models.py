from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Only service providers register on this platform.
    Customers never log in — they are in the separate Customer dataset.
    """
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    supabase_uid = models.UUIDField(unique=True, null=True, blank=True, db_index=True)
    is_phone_verified = models.BooleanField(default=False)
    referred_by = models.ForeignKey(
        "services.ServiceProvider",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referred_users"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
