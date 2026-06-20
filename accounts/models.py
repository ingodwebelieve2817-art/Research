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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
