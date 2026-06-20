from django.contrib.auth import get_user_model
from rest_framework import serializers
from services.models import SERVICE_CATEGORIES

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone", "supabase_uid", "created_at"]
        read_only_fields = ["id", "supabase_uid", "created_at"]


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    phone = serializers.CharField(required=False, default="")
    business_name = serializers.CharField(max_length=200)
    category = serializers.ChoiceField(choices=SERVICE_CATEGORIES)
    city = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=300, required=False, default="")
    whatsapp_number = serializers.CharField(max_length=20)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
