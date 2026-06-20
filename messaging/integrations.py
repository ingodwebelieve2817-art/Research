"""
Thin wrappers around the Meta (WhatsApp Business API + Facebook Graph API).

WhatsApp Cloud API docs:
  https://developers.facebook.com/docs/whatsapp/cloud-api

Facebook Marketplace / Pages Messaging docs:
  https://developers.facebook.com/docs/messenger-platform
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

WHATSAPP_API_BASE = "https://graph.facebook.com/v19.0"


# ──────────────────────────────────────────────
# WhatsApp Business Cloud API
# ──────────────────────────────────────────────

def send_whatsapp_text(to: str, body: str, phone_number_id: str = None, token: str = None) -> dict:
    """
    Send a free-form text message via WhatsApp Cloud API.
    `to` must be in E.164 format, e.g. +2348012345678
    """
    phone_number_id = phone_number_id or settings.WHATSAPP_PHONE_NUMBER_ID
    token = token or settings.WHATSAPP_API_TOKEN

    url = f"{WHATSAPP_API_BASE}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": body},
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        logger.info("WhatsApp sent to %s: %s", to, data)
        return {"success": True, "message_id": data.get("messages", [{}])[0].get("id")}
    except requests.RequestException as exc:
        logger.error("WhatsApp send failed to %s: %s", to, exc)
        return {"success": False, "error": str(exc)}


def send_whatsapp_template(
    to: str, template_name: str, language_code: str = "en",
    components: list = None, phone_number_id: str = None, token: str = None
) -> dict:
    """Send a pre-approved WhatsApp template message."""
    phone_number_id = phone_number_id or settings.WHATSAPP_PHONE_NUMBER_ID
    token = token or settings.WHATSAPP_API_TOKEN

    url = f"{WHATSAPP_API_BASE}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    template_payload = {
        "name": template_name,
        "language": {"code": language_code},
    }
    if components:
        template_payload["components"] = components

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": template_payload,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {"success": True, "message_id": data.get("messages", [{}])[0].get("id")}
    except requests.RequestException as exc:
        logger.error("WhatsApp template send failed: %s", exc)
        return {"success": False, "error": str(exc)}


# ──────────────────────────────────────────────
# Facebook Page / Marketplace Messaging
# ──────────────────────────────────────────────

def send_facebook_message(recipient_psid: str, message_text: str, page_access_token: str = None) -> dict:
    """
    Send a message to a user via Facebook Messenger (Page).
    recipient_psid is the user's Page-Scoped ID.
    """
    page_access_token = page_access_token or settings.FACEBOOK_PAGE_ACCESS_TOKEN
    url = f"{WHATSAPP_API_BASE}/me/messages"
    params = {"access_token": page_access_token}
    payload = {
        "recipient": {"id": recipient_psid},
        "message": {"text": message_text},
        "messaging_type": "MESSAGE_TAG",
        "tag": "CONFIRMED_EVENT_UPDATE",
    }

    try:
        resp = requests.post(url, json=payload, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        logger.info("Facebook message sent to PSID %s: %s", recipient_psid, data)
        return {"success": True, "message_id": data.get("message_id")}
    except requests.RequestException as exc:
        logger.error("Facebook send failed to PSID %s: %s", recipient_psid, exc)
        return {"success": False, "error": str(exc)}


def post_facebook_marketplace_listing(
    page_id: str,
    title: str,
    description: str,
    price: float,
    currency: str = "USD",
    page_access_token: str = None,
) -> dict:
    """
    Create a Facebook Marketplace listing on behalf of a provider's Page.
    Requires catalog/commerce permissions on the Page.
    """
    page_access_token = page_access_token or settings.FACEBOOK_PAGE_ACCESS_TOKEN
    url = f"{WHATSAPP_API_BASE}/{page_id}/commerce_listings"
    payload = {
        "title": title,
        "description": description,
        "price": int(price * 100),  # in cents
        "currency": currency,
        "access_token": page_access_token,
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {"success": True, "listing_id": data.get("id")}
    except requests.RequestException as exc:
        logger.error("Facebook Marketplace listing failed: %s", exc)
        return {"success": False, "error": str(exc)}
