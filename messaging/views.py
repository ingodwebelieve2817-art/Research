from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from services.models import ServiceProvider
from .models import Outreach


@login_required
def campaign_list(request):
    return render(request, "messaging/campaign_list.html", {"campaigns": []})


@login_required
def campaign_create(request):
    return render(request, "messaging/campaign_form.html", {"form": None, "customer_count": 0})


@login_required
def campaign_detail(request, pk):
    return render(request, "messaging/campaign_detail.html", {"campaign": None, "logs": []})


@login_required
def campaign_send(request, pk):
    return render(request, "messaging/campaign_confirm_send.html", {"campaign": None})


@login_required
def outreach_list(request):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    outreaches = provider.outreaches.all()
    return render(request, "messaging/outreach_list.html", {
        "provider": provider,
        "outreaches": outreaches,
    })


@login_required
def outreach_detail(request, pk):
    provider = get_object_or_404(ServiceProvider, user=request.user)
    outreach = get_object_or_404(Outreach, pk=pk, provider=provider)
    logs = outreach.logs.select_related("customer").order_by("-sent_at")
    return render(request, "messaging/outreach_detail.html", {
        "provider": provider,
        "outreach": outreach,
        "logs": logs,
    })
