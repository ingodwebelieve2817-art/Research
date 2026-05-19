from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from services.models import ServiceProvider
from .models import MessageCampaign, MessageLog
from .forms import CampaignForm


@login_required
def campaign_list(request):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    campaigns = provider.campaigns.all()
    return render(request, "messaging/campaign_list.html", {
        "provider": provider,
        "campaigns": campaigns,
    })


@login_required
def campaign_create(request):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    subscription = provider.current_subscription

    # Enforce plan gating for bulk messaging
    if not subscription or not subscription.plan.bulk_messaging:
        messages.error(request, "Bulk messaging is available on Pro and Max plans. Please upgrade.")
        return redirect("subscriptions:plans")

    if request.method == "POST":
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.provider = provider
            campaign.total_recipients = provider.customer_count
            campaign.save()
            messages.success(request, "Campaign saved as draft.")
            return redirect("messaging:campaign_list")
    else:
        form = CampaignForm()
    return render(request, "messaging/campaign_form.html", {
        "form": form,
        "provider": provider,
        "customer_count": provider.customer_count,
    })


@login_required
def campaign_send(request, pk):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    campaign = get_object_or_404(MessageCampaign, pk=pk, provider=provider)

    if campaign.status not in (MessageCampaign.STATUS_DRAFT, MessageCampaign.STATUS_FAILED):
        messages.warning(request, "This campaign has already been sent or is currently sending.")
        return redirect("messaging:campaign_list")

    if request.method == "POST":
        # Queue async Celery task
        try:
            from .tasks import dispatch_campaign
            dispatch_campaign.delay(campaign.pk)
            campaign.status = MessageCampaign.STATUS_QUEUED
            campaign.save(update_fields=["status"])
            messages.success(request, "Campaign queued! Messages will be sent shortly.")
        except Exception as exc:
            messages.error(request, f"Failed to queue campaign: {exc}")
        return redirect("messaging:campaign_list")

    return render(request, "messaging/campaign_confirm_send.html", {
        "campaign": campaign,
        "provider": provider,
    })


@login_required
def campaign_detail(request, pk):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    campaign = get_object_or_404(MessageCampaign, pk=pk, provider=provider)
    logs = campaign.logs.select_related("customer").order_by("-sent_at")
    return render(request, "messaging/campaign_detail.html", {
        "campaign": campaign,
        "logs": logs,
        "provider": provider,
    })
