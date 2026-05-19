from django.urls import path
from . import views

app_name = "services"

urlpatterns = [
    path("", views.provider_list, name="provider_list"),
    path("<int:pk>/", views.provider_detail, name="provider_detail"),
    path("setup/", views.setup, name="setup"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
