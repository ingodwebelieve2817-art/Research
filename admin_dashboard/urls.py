from django.urls import path
from . import views

app_name = "admin_dashboard"

urlpatterns = [
    path("", views.dashboard_overview, name="overview"),
    path("users/", views.user_list, name="user_list"),
    path("users/<int:pk>/", views.user_detail, name="user_detail"),
    path("users/<int:pk>/edit/", views.user_edit, name="user_edit"),
    path("users/<int:pk>/toggle-status/", views.user_toggle_status, name="user_toggle_status"),
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),
]
