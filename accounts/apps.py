from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        from django import forms
        plain_widgets = [
            forms.TextInput, forms.EmailInput, forms.PasswordInput,
            forms.NumberInput, forms.URLInput, forms.Textarea,
            forms.Select, forms.DateInput, forms.DateTimeInput,
        ]
        for w in plain_widgets:
            w.attrs = {"class": "form-control"}
        forms.CheckboxInput.attrs = {"class": "form-check-input"}
        forms.FileInput.attrs = {"class": "form-control"}
        forms.SelectMultiple.attrs = {"class": "form-select"}
