from django.urls import path
from . import views

app_name = "services"

urlpatterns = [
    path("", views.provider_list, name="provider_list"),
    path("<int:pk>/", views.provider_detail, name="provider_detail"),
    path("setup/", views.setup, name="setup"),
    path("provider-setup/", views.provider_setup, name="provider_setup"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/add/", views.customer_add, name="customer_add"),
    path("customers/<int:pk>/edit/", views.customer_edit, name="customer_edit"),
    path("services/", views.service_manage, name="service_manage"),
    path("services/add/", views.service_add, name="service_add"),
]
