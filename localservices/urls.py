from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from services.models import ServiceProvider, SERVICE_CATEGORIES
from customers.models import Customer
from subscriptions.models import Subscription


def home(request):
    from services.models import Review
    total_providers = ServiceProvider.objects.filter(is_active=True).count()
    total_customers = Customer.objects.filter(is_active=True).count()
    active_outreaches = Subscription.objects.filter(is_active=True).count() * 10
    reviews = Review.objects.all().select_related("customer", "provider")[:3]
    
    return render(request, "home.html", {
        "categories": SERVICE_CATEGORIES,
        "total_providers": total_providers,
        "total_customers": total_customers,
        "active_outreaches": active_outreaches or 42,
        "reviews": reviews,
    })


def custom_404_view(request, exception=None):
    return render(request, "404.html", status=404)


def robots_txt(request):
    return render(request, "robots.txt", {
        "scheme": request.scheme,
        "host": request.get_host()
    }, content_type="text/plain")


def sitemap_xml(request):
    return render(request, "sitemap.xml", {
        "scheme": request.scheme,
        "host": request.get_host()
    }, content_type="application/xml")


handler404 = "localservices.urls.custom_404_view"


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("dashboard/", include("services.urls", namespace="services")),
    path("subscriptions/", include("subscriptions.urls", namespace="subscriptions")),
    path("outreach/", include("messaging.urls", namespace="messaging")),
    path("api/v1/", include("localservices.api_urls")),
    path("admin-dashboard/", include("admin_dashboard.urls", namespace="admin_dashboard")),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap_xml, name="sitemap_xml"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
