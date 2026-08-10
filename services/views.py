from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import models
from django.db.models import Avg, Count, Value
from django.db.models.functions import Coalesce
import os
import logging
from supercompress.client import SuperCompress
from .models import ServiceProvider, SERVICE_CATEGORIES
from .forms import ServiceProviderForm

logger = logging.getLogger(__name__)


def provider_list(request):
    category = request.GET.get("category", "")
    city = request.GET.get("city", "").strip()
    min_rating = request.GET.get("min_rating", "")
    sort_by = request.GET.get("sort_by", "newest")

    # Annotate with average rating (coalesced to 0.0) and review count
    providers = ServiceProvider.objects.filter(is_active=True).annotate(
        avg_rating=Coalesce(Avg("reviews__rating"), Value(0.0), output_field=models.FloatField()),
        num_reviews=Count("reviews")
    )

    if category:
        providers = providers.filter(category=category)
    if city:
        providers = providers.filter(city__icontains=city)
    if min_rating:
        try:
            providers = providers.filter(avg_rating__gte=float(min_rating))
        except ValueError:
            pass

    if sort_by == "highest_rated":
        providers = providers.order_by("-avg_rating", "-num_reviews", "-created_at")
    elif sort_by == "most_reviewed":
        providers = providers.order_by("-num_reviews", "-avg_rating", "-created_at")
    else:  # newest
        providers = providers.order_by("-created_at")

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "services/partials/provider_cards.html", {"providers": providers})

    return render(request, "services/provider_list.html", {
        "providers": providers,
        "categories": SERVICE_CATEGORIES,
        "category": category,
        "city": city,
        "min_rating": min_rating,
        "sort_by": sort_by,
    })


@login_required
def provider_detail(request, pk):
    from django.urls import reverse
    provider = get_object_or_404(ServiceProvider, pk=pk, is_active=True)
    reviews = provider.reviews.all().select_related("customer")
    avg_rating_data = reviews.aggregate(avg=Avg("rating"))
    avg_rating = avg_rating_data["avg"]
    
    breadcrumbs = [
        ("Providers", reverse("services:provider_list")),
        (provider.business_name, ""),
    ]
    
    return render(request, "services/provider_detail.html", {
        "provider": provider,
        "services": [],
        "reviews": reviews,
        "avg_rating": avg_rating,
        "breadcrumbs": breadcrumbs,
    })


def submit_review(request, project_id):
    from projects.models import Project
    from customers.models import Customer
    from .models import Review

    project = get_object_or_404(Project, pk=project_id)

    # 1. Verify project is completed
    if project.status != "completed":
        messages.error(request, "You can only review a service after the project is completed.")
        return redirect("services:provider_detail", pk=project.provider.pk)

    # 2. Check if a review already exists for this project
    if hasattr(project, "review"):
        messages.error(request, "A review has already been submitted for this project.")
        return redirect("services:provider_detail", pk=project.provider.pk)

    if request.method == "POST":
        rating_str = request.POST.get("rating")
        comment = request.POST.get("comment", "").strip()

        try:
            rating = int(rating_str)
            if rating < 1 or rating > 5:
                raise ValueError()
        except (TypeError, ValueError):
            messages.error(request, "Please provide a valid rating between 1 and 5.")
            return render(request, "services/review_form.html", {"project": project})

        if not comment:
            messages.error(request, "Please provide a review comment.")
            return render(request, "services/review_form.html", {"project": project})

        customer = project.customer
        if not customer:
            messages.error(request, "This project has no associated customer.")
            return redirect("services:provider_detail", pk=project.provider.pk)

        Review.objects.create(
            provider=project.provider,
            customer=customer,
            project=project,
            rating=rating,
            comment=comment
        )

        messages.success(request, f"Thank you! Your review for {project.provider.business_name} has been submitted.")
        return redirect("services:thank_you")

    return render(request, "services/review_form.html", {"project": project})



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
    if request.user.is_superuser or request.user.is_staff:
        return redirect("admin_dashboard:overview")
    try:
        provider = ServiceProvider.objects.select_related("user").prefetch_related("subscriptions__plan").get(user=request.user)
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


@login_required
def ai_writer(request):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    
    if request.method == "POST":
        prompt = request.POST.get("prompt", "").strip()
        if not prompt:
            return JsonResponse({"success": False, "error": "Prompt cannot be empty."})
            
        # 1. Gather context
        context_parts = [
            f"Business Name: {provider.business_name}",
            f"Category: {provider.get_category_display()}",
            f"City: {provider.city}",
            f"Address: {provider.address or 'N/A'}",
            f"WhatsApp Contact: {provider.whatsapp_number}",
            f"Website: {provider.website or 'N/A'}",
            f"Description: {provider.description or 'N/A'}",
        ]
        context_str = "\n".join(context_parts)
        
        # 2. Compress context using SuperCompress
        sc_api_key = os.getenv("SUPERCOMPRESS_API_KEY", "")
        compressed_text = context_str
        original_tokens = len(context_str.split()) # basic token approximation
        kept_tokens = original_tokens
        savings_pct = 0.0
        compression_risk = "N/A (No API Key)"
        using_compression = False
        
        if sc_api_key:
            try:
                sc = SuperCompress(api_key=sc_api_key)
                result = sc.compress(context=context_str, query=prompt)
                compressed_text = result.compressed_text
                original_tokens = result.original_tokens
                kept_tokens = result.kept_tokens
                savings_pct = result.kv_savings_pct
                compression_risk = getattr(result, "compression_risk", "low")
                using_compression = True
            except Exception as e:
                # Log error and fallback gracefully
                logger.error("SuperCompress failed: %s", e)
                
        # 3. Call LLM (Gemini or Mock fallback)
        gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        generated_copy = ""
        
        if gemini_api_key:
            try:
                import requests
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": (
                                f"You are an expert AI copywriter for a service matching platform.\n"
                                f"Here is the compressed context about the service provider:\n"
                                f"--- BEGIN CONTEXT ---\n{compressed_text}\n--- END CONTEXT ---\n\n"
                                f"Task: {prompt}\n"
                                f"Generate a short, high-converting promotional message (maximum 300 characters) "
                                f"for WhatsApp/Facebook outreach. Do not include quotes, intro, or explanations. "
                                f"Include the business name and contact information."
                            )
                        }]
                    }]
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                generated_copy = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception as e:
                logger.error("Gemini copy generation failed: %s", e)
                generated_copy = f"Error generating text via Gemini API: {str(e)}"
        else:
            # Fallback mock copywriting
            generated_copy = (
                f"🌟 Need professional {provider.get_category_display()} services in {provider.city}? "
                f"Choose {provider.business_name}! We are prompt, local, and reliable. "
                f"Contact us on WhatsApp: {provider.whatsapp_number}! {prompt}"
            )
            
        return JsonResponse({
            "success": True,
            "original_text": context_str,
            "compressed_text": compressed_text,
            "original_tokens": original_tokens,
            "kept_tokens": kept_tokens,
            "savings_pct": f"{savings_pct:.1f}%",
            "compression_risk": compression_risk,
            "using_compression": using_compression,
            "generated_copy": generated_copy,
        })
        
    return render(request, "services/ai_writer.html", {
        "provider": provider,
        "supercompress_api_configured": bool(os.getenv("SUPERCOMPRESS_API_KEY")),
        "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY")),
    })


def case_studies(request):
    return render(request, "case_studies.html")


def privacy(request):
    return render(request, "privacy.html")


def thank_you(request):
    return render(request, "thank_you.html")
