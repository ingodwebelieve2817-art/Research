from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path("", views.campaign_list, name="campaign_list"),
    path("new/", views.campaign_create, name="campaign_create"),
    path("<int:pk>/", views.campaign_detail, name="campaign_detail"),
    path("<int:pk>/send/", views.campaign_send, name="campaign_send"),
]
