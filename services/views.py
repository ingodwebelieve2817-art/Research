from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ServiceProvider, SERVICE_CATEGORIES
from .forms import ServiceProviderForm


def provider_list(request):
    category = request.GET.get("category", "")
    city = request.GET.get("city", "").strip()

    providers = ServiceProvider.objects.filter(is_active=True)
    if category:
        providers = providers.filter(category=category)
    if city:
        providers = providers.filter(city__icontains=city)

    return render(request, "services/provider_list.html", {
        "providers": providers,
        "categories": SERVICE_CATEGORIES,
        "category": category,
        "city": city,
    })


def provider_detail(request, pk):
    provider = get_object_or_404(ServiceProvider, pk=pk, is_active=True)
    return render(request, "services/provider_detail.html", {
        "provider": provider,
        "services": [],
        "reviews": [],
        "avg_rating": None,
    })


@login_required
def setup(request):
    """Provider fills in their business profile after registering."""
    try:
        profile = request.user.provider_profile
    except ServiceProvider.DoesNotExist:
        profile = None

    if request.method == "POST":
        form = ServiceProviderForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            provider = form.save(commit=False)
            provider.user = request.user
            provider.save()
            messages.success(request, "Business profile saved!")
            return redirect("services:dashboard")
    else:
        form = ServiceProviderForm(instance=profile)
    return render(request, "services/setup.html", {"form": form})


@login_required
def provider_setup(request):
    return redirect("services:setup")


@login_required
def customer_list(request):
    return render(request, "services/customer_list.html", {
        "customers": [],
        "customer_count": 0,
        "customer_limit": 0,
    })


@login_required
def customer_add(request):
    return render(request, "services/customer_form.html", {"form": None, "customer": None})


@login_required
def customer_edit(request, pk):
    return render(request, "services/customer_form.html", {"form": None, "customer": None})


@login_required
def service_manage(request):
    return render(request, "services/service_manage.html", {"services": []})


@login_required
def service_add(request):
    return render(request, "services/service_form.html", {"form": None})


@login_required
def dashboard(request):
    try:
        provider = request.user.provider_profile
    except ServiceProvider.DoesNotExist:
        messages.info(request, "Please complete your business profile first.")
        return redirect("services:setup")

    subscription = provider.active_subscription
    recent_outreaches = provider.outreaches.order_by("-created_at")[:5]

    # Count how many customers from the platform dataset match this provider
    from customers.models import Customer
    matched_customers = Customer.objects.filter(
        city__iexact=provider.city,
        is_active=True,
    ).count()

    return render(request, "services/dashboard.html", {
        "provider": provider,
        "subscription": subscription,
        "recent_outreaches": recent_outreaches,
        "matched_customers": matched_customers,
    })
