from django.urls import path
from . import views

app_name = "services"

urlpatterns = [
    path("setup/", views.setup, name="setup"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
