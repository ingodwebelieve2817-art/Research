"""
Auto-apply Bootstrap 5 form-control classes via a custom renderer.
Add to FORM_RENDERER in settings to activate globally.
"""
from django.forms.renderers import TemplatesSetting


class BootstrapRenderer(TemplatesSetting):
    pass
