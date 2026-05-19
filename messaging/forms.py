from django import forms
from .models import MessageCampaign


class CampaignForm(forms.ModelForm):
    class Meta:
        model = MessageCampaign
        fields = ["title", "message_body", "channel", "scheduled_at"]
        widgets = {
            "message_body": forms.Textarea(attrs={"rows": 5, "maxlength": 1024}),
            "scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
