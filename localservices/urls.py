from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from services.models import SERVICE_CATEGORIES


def home(request):
    return render(request, "home.html", {"categories": SERVICE_CATEGORIES})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("providers/", include("services.urls", namespace="services")),
    path("subscriptions/", include("subscriptions.urls", namespace="subscriptions")),
    path("messaging/", include("messaging.urls", namespace="messaging")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
