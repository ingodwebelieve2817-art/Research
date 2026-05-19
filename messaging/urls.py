from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path("", views.outreach_list, name="outreach_list"),
    path("<int:pk>/", views.outreach_detail, name="outreach_detail"),
    path("campaigns/", views.campaign_list, name="campaign_list"),
    path("campaigns/new/", views.campaign_create, name="campaign_create"),
    path("campaigns/<int:pk>/", views.campaign_detail, name="campaign_detail"),
    path("campaigns/<int:pk>/send/", views.campaign_send, name="campaign_send"),
]
