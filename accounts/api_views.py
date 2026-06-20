from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from supabase import create_client

from activities.models import ActivityLog
from services.models import ServiceProvider
from .serializers import SignupSerializer, LoginSerializer, UserSerializer

User = get_user_model()


def get_supabase_client():
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("Supabase URL and Key must be set in your configuration / environment.")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
    """
    Sign up a new service provider.
    Registers the user in Supabase Auth, creates the custom User in Django,
    and sets up their ServiceProvider business profile.
    """
    serializer = SignupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    try:
        supabase = get_supabase_client()
        # 1. Sign up user in Supabase Auth
        supabase_resp = supabase.auth.sign_up(
            {
                "email": data["email"],
                "password": data["password"],
                "options": {
                    "data": {
                        "phone": data.get("phone", ""),
                    }
                },
            }
        )
    except Exception as e:
        return Response(
            {"error": f"Supabase auth registration failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Note: If email confirmation is enabled in Supabase, supabase_resp.user might be created
    # but not fully active, or session might be null. Regardless, the user object is returned.
    supabase_user = supabase_resp.user
    if not supabase_user:
        return Response(
            {"error": "Failed to create user on Supabase auth server."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # 2. Create Django user mapping
    django_user = User.objects.create_user(
        username=data["email"],
        email=data["email"],
        phone=data.get("phone", ""),
        supabase_uid=supabase_user.id,
    )

    # 3. Create ServiceProvider business profile
    provider = ServiceProvider.objects.create(
        user=django_user,
        business_name=data["business_name"],
        category=data["category"],
        city=data["city"],
        address=data.get("address", ""),
        whatsapp_number=data["whatsapp_number"],
    )

    # 4. Log the registration activity
    ActivityLog.objects.create(
        user=django_user,
        action="Provider Signup",
        details=f"Provider created business profile '{provider.business_name}' in {provider.city}.",
    )

    return Response(
        {
            "message": "User registered successfully.",
            "user": UserSerializer(django_user).data,
            "provider_id": provider.id,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
    Log in a service provider.
    Verifies credentials with Supabase Auth and returns the access JWT token.
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    try:
        supabase = get_supabase_client()
        # Sign in via Supabase Auth
        supabase_resp = supabase.auth.sign_in_with_password(
            {
                "email": data["email"],
                "password": data["password"],
            }
        )
    except Exception as e:
        return Response(
            {"error": f"Invalid email or password: {str(e)}"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    session = supabase_resp.session
    if not session:
        return Response(
            {"error": "Login succeeded but session could not be established."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Fetch/create user in Django matching this Supabase ID
    supabase_user = supabase_resp.user
    django_user, created = User.objects.get_or_create(
        supabase_uid=supabase_user.id,
        defaults={
            "username": supabase_user.email,
            "email": supabase_user.email,
            "phone": supabase_user.user_metadata.get("phone", "") if supabase_user.user_metadata else "",
        },
    )

    # Log the login activity
    ActivityLog.objects.create(
        user=django_user,
        action="User Login",
        details="User authenticated via Supabase JWT.",
    )

    return Response(
        {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "expires_in": session.expires_in,
            "user": UserSerializer(django_user).data,
        },
        status=status.HTTP_200_OK,
    )
