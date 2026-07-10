import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from services.models import ServiceProvider
from .models import SubscriptionPlan, Subscription, Payment


import json
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict


def plans_page(request):
    plans = SubscriptionPlan.objects.all().order_by("price_monthly")
    plans_list = []
    for p in plans:
        d = model_to_dict(p)
        d["price_monthly"] = float(p.price_monthly)
        plans_list.append(d)
    plans_json = json.dumps(plans_list, cls=DjangoJSONEncoder)
    
    return render(request, "subscriptions/plans.html", {
        "plans": plans,
        "plans_json": plans_json
    })


@login_required
def subscribe(request, plan_id):
    try:
        provider = ServiceProvider.objects.get(user=request.user)
    except ServiceProvider.DoesNotExist:
        messages.warning(request, "Please complete your business profile before subscribing.")
        return redirect("accounts:register_provider")
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id)

    if request.method == "POST":
        # Cancel existing active subscriptions
        provider.subscriptions.filter(is_active=True).update(
            is_active=False, status=Subscription.STATUS_CANCELLED
        )

        if plan.price_monthly == 0:
            subscription = _activate_subscription(provider, plan, payment_ref="free")
            _send_confirmation_email(request, subscription)
            messages.success(request, f"You're now on the {plan.name} plan!")
            return redirect("subscriptions:success", pk=subscription.pk)

        # Create Razorpay order
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        amount_units = int(plan.price_monthly * 100)
        order = client.order.create({
            "amount": amount_units,
            "currency": settings.RAZORPAY_CURRENCY,
            "receipt": f"plan{plan.pk}_prov{provider.pk}",
            "payment_capture": 1,
        })

        # Pending subscription — activated only after payment verified
        subscription = Subscription.objects.create(
            provider=provider,
            plan=plan,
            status=Subscription.STATUS_CANCELLED,
            started_at=timezone.now(),
            is_active=False,
            payment_reference=order["id"],
        )
        Payment.objects.create(
            subscription=subscription,
            amount=plan.price_monthly,
            currency=settings.RAZORPAY_CURRENCY,
            status=Payment.STATUS_PENDING,
            gateway="razorpay",
            transaction_id=order["id"],
        )

        return render(request, "subscriptions/checkout.html", {
            "plan": plan,
            "provider": provider,
            "razorpay_order_id": order["id"],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount_units": amount_units,
            "currency": settings.RAZORPAY_CURRENCY,
        })

    return render(request, "subscriptions/confirm.html", {"plan": plan, "provider": provider})


@login_required
def payment_verify(request):
    if request.method != "POST":
        return redirect("subscriptions:plans")

    order_id = request.POST.get("razorpay_order_id", "")
    payment_id = request.POST.get("razorpay_payment_id", "")
    signature = request.POST.get("razorpay_signature", "")

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        })
    except razorpay.errors.SignatureVerificationError:
        messages.error(request, "Payment verification failed. Please contact support.")
        return redirect("subscriptions:plans")

    payment = get_object_or_404(Payment, transaction_id=order_id)
    payment.status = Payment.STATUS_SUCCESS
    payment.transaction_id = payment_id
    payment.paid_at = timezone.now()
    payment.save()

    subscription = payment.subscription
    subscription.status = Subscription.STATUS_ACTIVE
    subscription.started_at = timezone.now()
    subscription.expires_at = timezone.now() + timedelta(days=30)
    subscription.is_active = True
    subscription.save()

    _send_confirmation_email(request, subscription)

    try:
        from messaging.tasks import trigger_outreach
        trigger_outreach.delay(subscription.provider.pk)
    except Exception:
        pass

    return redirect("subscriptions:success", pk=subscription.pk)


@login_required
def payment_success(request, pk):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    subscription = get_object_or_404(Subscription, pk=pk, provider=provider)
    return render(request, "subscriptions/success.html", {
        "subscription": subscription,
        "provider": provider,
    })


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


def _activate_subscription(provider, plan, payment_ref=""):
    return Subscription.objects.create(
        provider=provider,
        plan=plan,
        status=Subscription.STATUS_ACTIVE,
        started_at=timezone.now(),
        expires_at=timezone.now() + timedelta(days=30),
        is_active=True,
        payment_reference=payment_ref,
    )


def _send_confirmation_email(request, subscription):
    plan = subscription.plan
    provider = subscription.provider
    subject = f"Your {plan.name} subscription is active — LocalPro"
    body = (
        f"Hi {provider.user.username},\n\n"
        f"Your {plan.name} plan is now active!\n\n"
        f"Plan details:\n"
        f"  - Customers reached: up to {plan.reach_limit}\n"
        f"  - WhatsApp outreach: {'Yes' if plan.whatsapp_enabled else 'No'}\n"
        f"  - Facebook outreach: {'Yes' if plan.facebook_enabled else 'No'}\n"
        f"  - Price: ${plan.price_monthly}/month\n"
        f"  - Expires: {subscription.expires_at.strftime('%B %d, %Y') if subscription.expires_at else 'N/A'}\n\n"
        f"We are now reaching out to customers in {provider.city} who need "
        f"{provider.get_category_display()} services.\n\n"
        f"Manage your plan: {request.build_absolute_uri('/subscriptions/my-plan/')}\n\n"
        f"Thanks,\nThe LocalPro Team"
    )
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [provider.user.email], fail_silently=True)
