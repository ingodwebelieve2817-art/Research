from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.api_views import signup_view, login_view
from customers.views import CustomerViewSet

# Set up REST Framework Default Router for customer viewset
router = DefaultRouter()
router.register(r"customers", CustomerViewSet, basename="customer")

urlpatterns = [
    # Auth Endpoints
    path("auth/signup/", signup_view, name="api_signup"),
    path("auth/login/", login_view, name="api_login"),
    # Customer CRUD Endpoints
    path("", include(router.urls)),
]
