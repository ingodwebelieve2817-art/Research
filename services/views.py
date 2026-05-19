from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ServiceProvider
from .forms import ServiceProviderForm


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
        service_interest=provider.category,
        is_active=True,
    ).count()

    return render(request, "services/dashboard.html", {
        "provider": provider,
        "subscription": subscription,
        "recent_outreaches": recent_outreaches,
        "matched_customers": matched_customers,
    })
