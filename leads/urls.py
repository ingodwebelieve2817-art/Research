from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_leads, name="leads-list"),
    path("create/", views.create_lead, name="leads-create"),
    path("<int:pk>/status/", views.update_lead_status, name="leads-update-status"),
]
