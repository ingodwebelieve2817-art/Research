from django.urls import path
from . import views

app_name = "subscriptions"

urlpatterns = [
    path("plans/", views.plans_page, name="plans"),
    path("subscribe/<int:plan_id>/", views.subscribe, name="subscribe"),
    path("my-plan/", views.my_subscription, name="my_subscription"),
]
