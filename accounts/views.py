from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProviderRegistrationForm, CustomerRegistrationForm
from .models import User


def register_provider(request):
    if request.method == "POST":
        form = ProviderRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Now complete your business profile.")
            return redirect("services:provider_setup")
    else:
        form = ProviderRegistrationForm()
    return render(request, "accounts/register_provider.html", {"form": form})


def register_customer(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created! Explore local service providers near you.")
            return redirect("services:provider_list")
    else:
        form = CustomerRegistrationForm()
    return render(request, "accounts/register_customer.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_provider():
                return redirect("services:dashboard")
            return redirect("services:provider_list")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("/")


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"user": request.user})
