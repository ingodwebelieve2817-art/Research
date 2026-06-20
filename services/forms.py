from django import forms
from .models import ServiceProvider


class ServiceProviderForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = [
            "business_name",
            "category",
            "description",
            "logo",
            "city",
            "address",
            "state",
            "country",
            "whatsapp_number",
            "facebook_page_url",
            "website",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
        help_texts = {
            "whatsapp_number": "Include country code e.g. +2348012345678",
            "city": "Must match the city names in the customer dataset for correct matching",
        }
