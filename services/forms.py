from django import forms
from .models import ServiceProvider, ProviderService, CustomerProfile


class ServiceProviderForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = [
            "business_name", "category", "description",
            "logo", "cover_image",
            "address", "city", "state", "country",
            "whatsapp_number", "website",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class ProviderServiceForm(forms.ModelForm):
    class Meta:
        model = ProviderService
        fields = ["title", "description", "price", "price_unit", "image", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ["name", "phone", "email", "whatsapp_number", "notes",
                  "opted_in_whatsapp", "opted_in_facebook"]
