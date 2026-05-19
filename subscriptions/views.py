from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from services.models import ServiceProvider
from .models import SubscriptionPlan, Subscription, Payment


def plans_page(request):
    plans = SubscriptionPlan.objects.all().order_by("price_monthly")
    return render(request, "subscriptions/plans.html", {"plans": plans})


@login_required
def subscribe(request, plan_id):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id)

    if request.method == "POST":
        # Cancel any existing active subscriptions
        provider.subscriptions.filter(is_active=True).update(
            is_active=False, status=Subscription.STATUS_CANCELLED
        )

        subscription = Subscription.objects.create(
            provider=provider,
            plan=plan,
            status=Subscription.STATUS_ACTIVE,
            started_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=30),
            is_active=True,
        )

        if plan.price_monthly > 0:
            Payment.objects.create(
                subscription=subscription,
                amount=plan.price_monthly,
                currency="USD",
                status=Payment.STATUS_PENDING,
                gateway="stripe",
            )

        # Automatically trigger outreach to matching customers
        from messaging.tasks import trigger_outreach
        trigger_outreach.delay(provider.pk)

        messages.success(
            request,
            f"Subscribed to {plan.name}! We are now reaching out to up to "
            f"{plan.reach_limit} customers in {provider.city} who need {provider.get_category_display()} services."
        )
        return redirect("services:dashboard")

    return render(request, "subscriptions/confirm.html", {"plan": plan, "provider": provider})


@login_required
def my_subscription(request):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    subscription = provider.active_subscription
    payments = subscription.payments.order_by("-created_at") if subscription else []
    return render(request, "subscriptions/my_subscription.html", {
        "provider": provider,
        "subscription": subscription,
        "payments": payments,
    })
