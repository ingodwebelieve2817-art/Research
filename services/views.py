from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .models import ServiceProvider, ProviderService, CustomerProfile, ProviderReview
from .forms import ServiceProviderForm, ProviderServiceForm, CustomerProfileForm


def provider_list(request):
    category = request.GET.get("category", "")
    city = request.GET.get("city", "")
    qs = ServiceProvider.objects.filter(is_active=True).annotate(avg_rating=Avg("reviews__rating"))
    if category:
        qs = qs.filter(category=category)
    if city:
        qs = qs.filter(city__icontains=city)
    return render(request, "services/provider_list.html", {
        "providers": qs,
        "category": category,
        "city": city,
        "categories": ServiceProvider._meta.get_field("category").choices,
    })


def provider_detail(request, pk):
    provider = get_object_or_404(ServiceProvider, pk=pk, is_active=True)
    services = provider.offered_services.filter(is_active=True)
    reviews = provider.reviews.select_related("customer").order_by("-created_at")
    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"]
    return render(request, "services/provider_detail.html", {
        "provider": provider,
        "services": services,
        "reviews": reviews,
        "avg_rating": avg_rating,
    })


@login_required
def provider_setup(request):
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
    return render(request, "services/provider_setup.html", {"form": form})


@login_required
def dashboard(request):
    if not request.user.is_provider():
        return redirect("services:provider_list")
    provider = get_object_or_404(ServiceProvider, user=request.user)
    subscription = provider.current_subscription
    customers = provider.customers.all()[:10]
    recent_campaigns = provider.campaigns.all()[:5]
    return render(request, "services/dashboard.html", {
        "provider": provider,
        "subscription": subscription,
        "customers": customers,
        "recent_campaigns": recent_campaigns,
        "customer_count": provider.customer_count,
        "customer_limit": provider.customer_limit,
    })


@login_required
def customer_list(request):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    customers = provider.customers.all()
    return render(request, "services/customer_list.html", {
        "provider": provider,
        "customers": customers,
        "customer_count": provider.customer_count,
        "customer_limit": provider.customer_limit,
    })


@login_required
def customer_add(request):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    if not provider.can_accept_customer():
        messages.error(
            request,
            f"You've reached your plan limit of {provider.customer_limit} customers. "
            "Upgrade your plan to add more."
        )
        return redirect("subscriptions:plans")

    if request.method == "POST":
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.provider = provider
            customer.save()
            messages.success(request, f"Customer {customer.name} added.")
            return redirect("services:customer_list")
    else:
        form = CustomerProfileForm()
    return render(request, "services/customer_form.html", {"form": form, "provider": provider})


@login_required
def customer_edit(request, pk):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    customer = get_object_or_404(CustomerProfile, pk=pk, provider=provider)
    if request.method == "POST":
        form = CustomerProfileForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer updated.")
            return redirect("services:customer_list")
    else:
        form = CustomerProfileForm(instance=customer)
    return render(request, "services/customer_form.html", {"form": form, "provider": provider, "customer": customer})


@login_required
def service_manage(request):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    services = provider.offered_services.all()
    return render(request, "services/service_manage.html", {"provider": provider, "services": services})


@login_required
def service_add(request):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    if request.method == "POST":
        form = ProviderServiceForm(request.POST, request.FILES)
        if form.is_valid():
            svc = form.save(commit=False)
            svc.provider = provider
            svc.save()
            messages.success(request, "Service added.")
            return redirect("services:service_manage")
    else:
        form = ProviderServiceForm()
    return render(request, "services/service_form.html", {"form": form})
