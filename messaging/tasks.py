"""
Celery tasks for automatic outreach.

trigger_outreach is called automatically when a provider subscribes.
It finds matching customers from the platform's dataset and
sends them a WhatsApp / Facebook message about the provider.
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def build_message(provider) -> str:
    """Build the outreach message text sent to customers."""
    lines = [
        f"Hi! We found a {provider.get_category_display()} near you in {provider.city}.",
        f"",
        f"Business: {provider.business_name}",
    ]
    if provider.address:
        lines.append(f"Address: {provider.address}")
    if provider.whatsapp_number:
        lines.append(f"WhatsApp: {provider.whatsapp_number}")
    if provider.facebook_page_url:
        lines.append(f"Facebook: {provider.facebook_page_url}")
    if provider.website:
        lines.append(f"Website: {provider.website}")
    if provider.description:
        lines.append(f"")
        lines.append(provider.description[:200])
    return "\n".join(lines)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def trigger_outreach(self, provider_id: int):
    """
    Main outreach task.
    1. Find matching customers (same city + same service interest)
    2. Pick up to reach_limit of them
    3. Send WhatsApp / Facebook message to each
    4. Log every delivery attempt
    """
    from services.models import ServiceProvider
    from customers.models import Customer
    from messaging.models import Outreach, OutreachLog
    from messaging.integrations import send_whatsapp_text, send_facebook_message

    try:
        provider = ServiceProvider.objects.get(pk=provider_id)
    except ServiceProvider.DoesNotExist:
        logger.error("Provider %s not found", provider_id)
        return

    subscription = provider.active_subscription
    if not subscription:
        logger.warning("Provider %s has no active subscription — skipping outreach", provider_id)
        return

    plan = subscription.plan
    reach_limit = plan.reach_limit

    # Determine which channels to use based on plan
    if plan.whatsapp_enabled and plan.facebook_enabled:
        channel = Outreach.CHANNEL_BOTH
    elif plan.facebook_enabled:
        channel = Outreach.CHANNEL_FACEBOOK
    else:
        channel = Outreach.CHANNEL_WHATSAPP

    # Find customers from the platform dataset that match this provider
    matched_customers = Customer.objects.filter(
        city__iexact=provider.city,
        service_interest=provider.category,
        is_active=True,
        opted_in_whatsapp=True,
    )[:reach_limit]

    outreach = Outreach.objects.create(
        provider=provider,
        channel=channel,
        status=Outreach.STATUS_RUNNING,
        target_city=provider.city,
        target_category=provider.category,
        reach_limit=reach_limit,
        total_matched=matched_customers.count(),
    )

    message_text = build_message(provider)
    sent = 0
    failed = 0

    for customer in matched_customers:
        # WhatsApp
        if plan.whatsapp_enabled and customer.opted_in_whatsapp:
            result = send_whatsapp_text(
                to=customer.effective_whatsapp(),
                body=message_text,
            )
            OutreachLog.objects.create(
                outreach=outreach,
                customer=customer,
                channel="whatsapp",
                status=OutreachLog.STATUS_SENT if result["success"] else OutreachLog.STATUS_FAILED,
                external_message_id=result.get("message_id", ""),
                error_message=result.get("error", ""),
                sent_at=timezone.now() if result["success"] else None,
            )
            if result["success"]:
                sent += 1
            else:
                failed += 1

        # Facebook
        if plan.facebook_enabled and customer.opted_in_facebook:
            result = send_facebook_message(
                recipient_psid=customer.phone,
                message_text=message_text,
            )
            OutreachLog.objects.create(
                outreach=outreach,
                customer=customer,
                channel="facebook",
                status=OutreachLog.STATUS_SENT if result["success"] else OutreachLog.STATUS_FAILED,
                external_message_id=result.get("message_id", ""),
                error_message=result.get("error", ""),
                sent_at=timezone.now() if result["success"] else None,
            )
            if result["success"]:
                sent += 1
            else:
                failed += 1

    outreach.total_sent = sent
    outreach.total_failed = failed
    outreach.status = Outreach.STATUS_DONE
    outreach.completed_at = timezone.now()
    outreach.save(update_fields=["total_sent", "total_failed", "status", "completed_at"])

    logger.info(
        "Outreach complete for %s: %s sent, %s failed in %s",
        provider.business_name, sent, failed, provider.city
    )
