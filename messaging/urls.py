from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path("", views.outreach_list, name="outreach_list"),
    path("<int:pk>/", views.outreach_detail, name="outreach_detail"),
]
