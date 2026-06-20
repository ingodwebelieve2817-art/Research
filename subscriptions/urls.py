from django.urls import path
from . import views

app_name = "subscriptions"

urlpatterns = [
    path("plans/", views.plans_page, name="plans"),
    path("subscribe/<int:plan_id>/", views.subscribe, name="subscribe"),
    path("payment/verify/", views.payment_verify, name="payment_verify"),
    path("payment/success/<int:pk>/", views.payment_success, name="success"),
    path("my-plan/", views.my_subscription, name="my_subscription"),
]
