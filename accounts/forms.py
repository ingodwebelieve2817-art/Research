from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class BusinessRegistrationForm(forms.ModelForm):
    # User Account fields
    email = forms.EmailField(required=True, label="Email Address")
    phone = forms.CharField(max_length=20, required=True, label="Phone Number")
    password = forms.CharField(widget=forms.PasswordInput(), required=True, label="Password")
    
    # Business Details fields
    business_name = forms.CharField(max_length=150, required=True, label="Business Name")
    category = forms.ChoiceField(choices=[], required=True, label="Business Category") # Loaded dynamically in __init__
    city = forms.CharField(max_length=100, required=True, label="City")
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), required=False, label="Street Address")
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False, label="Business Description")
    website = forms.URLField(required=False, label="Website URL")
    whatsapp_number = forms.CharField(max_length=20, required=False, label="WhatsApp Number")
    
    # Referral Promo Code
    promo_code = forms.CharField(max_length=50, required=False, label="Promo / Referral Code")

    class Meta:
        model = User
        fields = ("username", "email", "phone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from services.models import SERVICE_CATEGORIES
        self.fields["category"].choices = SERVICE_CATEGORIES

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]
        user.set_password(self.cleaned_data["password"])
        
        # Handle referral promo code validation
        promo_code = self.cleaned_data.get("promo_code")
        referrer = None
        if promo_code:
            from services.models import ServiceProvider
            try:
                referrer = ServiceProvider.objects.get(promo_code=promo_code)
                user.referred_by = referrer
            except ServiceProvider.DoesNotExist:
                pass
        
        if commit:
            user.save()
            if referrer:
                from services.models import Referral
                Referral.objects.get_or_create(referrer=referrer, referred_user=user)
                
            # Create corresponding ServiceProvider profile upfront
            from services.models import ServiceProvider
            ServiceProvider.objects.create(
                user=user,
                business_name=self.cleaned_data["business_name"],
                category=self.cleaned_data["category"],
                city=self.cleaned_data["city"],
                address=self.cleaned_data.get("address") or "",
                description=self.cleaned_data.get("description") or "",
                website=self.cleaned_data.get("website") or "",
                whatsapp_number=self.cleaned_data.get("whatsapp_number") or "",
                is_active=True
            )
            
        return user


class CustomerRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=False, label="Email Address (Optional)")
    phone = forms.CharField(max_length=20, required=False, label="Phone Number (Optional)")

    class Meta:
        model = User
        fields = ("username", "email", "phone")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email") or ""
        user.phone = self.cleaned_data.get("phone") or ""
        
        # Default password for customer logins
        user.set_password("DefaultPassword123!")
        
        if commit:
            user.save()
        return user

