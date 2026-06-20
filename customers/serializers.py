from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "name",
            "phone",
            "whatsapp_number",
            "city",
            "opted_in_whatsapp",
            "opted_in_facebook",
            "is_active",
            "added_at",
        ]
        read_only_fields = ["id", "added_at"]
