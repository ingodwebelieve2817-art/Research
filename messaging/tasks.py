"""
Celery tasks for asynchronous bulk message dispatch.
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def dispatch_campaign(self, campaign_id: int):
    from .models import MessageCampaign, MessageLog
    from .integrations import send_whatsapp_text, send_facebook_message

    try:
        campaign = MessageCampaign.objects.get(pk=campaign_id)
    except MessageCampaign.DoesNotExist:
        logger.error("Campaign %s not found", campaign_id)
        return

    campaign.status = MessageCampaign.STATUS_SENDING
    campaign.save(update_fields=["status"])

    customers = campaign.provider.customers.all()
    channel = campaign.channel
    provider = campaign.provider

    sent = 0
    failed = 0

    for customer in customers:
        # WhatsApp dispatch
        if channel in (MessageCampaign.CHANNEL_WHATSAPP, MessageCampaign.CHANNEL_BOTH):
            if customer.opted_in_whatsapp and customer.whatsapp_number:
                wa_token = provider.facebook_page_token or None
                wa_phone_id = None
                result = send_whatsapp_text(
                    to=customer.whatsapp_number,
                    body=campaign.message_body,
                )
                log = MessageLog.objects.create(
                    campaign=campaign,
                    customer=customer,
                    channel="whatsapp",
                    status=MessageLog.STATUS_SENT if result["success"] else MessageLog.STATUS_FAILED,
                    external_message_id=result.get("message_id", ""),
                    error_message=result.get("error", ""),
                    sent_at=timezone.now() if result["success"] else None,
                )
                if result["success"]:
                    sent += 1
                else:
                    failed += 1

        # Facebook dispatch
        if channel in (MessageCampaign.CHANNEL_FACEBOOK, MessageCampaign.CHANNEL_BOTH):
            if customer.opted_in_facebook and customer.email:
                # In practice you'd use the customer's PSID; email is a fallback identifier
                result = send_facebook_message(
                    recipient_psid=customer.email,
                    message_text=campaign.message_body,
                    page_access_token=provider.facebook_page_token or None,
                )
                MessageLog.objects.create(
                    campaign=campaign,
                    customer=customer,
                    channel="facebook",
                    status=MessageLog.STATUS_SENT if result["success"] else MessageLog.STATUS_FAILED,
                    external_message_id=result.get("message_id", ""),
                    error_message=result.get("error", ""),
                    sent_at=timezone.now() if result["success"] else None,
                )
                if result["success"]:
                    sent += 1
                else:
                    failed += 1

    campaign.sent_count = sent
    campaign.failed_count = failed
    campaign.status = MessageCampaign.STATUS_SENT
    campaign.sent_at = timezone.now()
    campaign.save(update_fields=["sent_count", "failed_count", "status", "sent_at"])
    logger.info("Campaign %s complete: %s sent, %s failed", campaign_id, sent, failed)
