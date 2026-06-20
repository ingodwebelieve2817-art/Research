import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework import exceptions

User = get_user_model()


class SupabaseJWTAuthentication(authentication.BaseAuthentication):
    """
    Custom Django REST Framework authentication class for Supabase Auth.
    Verifies the JWT token from the Authorization header using Supabase's JWT secret.
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        token = parts[1]

        try:
            # Decode using Supabase JWT Secret
            # Supabase JWTs use the HS256 algorithm and have "authenticated" as the audience
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(f"Invalid token: {str(e)}")

        supabase_uid = payload.get("sub")
        if not supabase_uid:
            raise exceptions.AuthenticationFailed("Token is missing user identifier ('sub' claim)")

        email = payload.get("email")
        phone = payload.get("phone")

        # Auto-provision user in Django if they do not exist
        # This maps the Supabase user UUID to our custom Django User model
        user, created = User.objects.get_or_create(
            supabase_uid=supabase_uid,
            defaults={
                "username": email or phone or supabase_uid,
                "email": email or "",
                "phone": phone or "",
                "is_active": True,
            },
        )

        return (user, token)

    def authenticate_header(self, request):
        return "Bearer"
