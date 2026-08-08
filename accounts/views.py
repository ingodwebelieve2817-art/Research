from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import BusinessRegistrationForm, CustomerRegistrationForm


def register(request):
    if request.method == "POST":
        form = BusinessRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Business account and profile registered successfully!")
            return redirect("services:dashboard")
    else:
        form = BusinessRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


def register_provider(request):
    if request.method == "POST":
        form = BusinessRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Business account and profile registered successfully!")
            return redirect("services:dashboard")
    else:
        form = BusinessRegistrationForm()
    return render(request, "accounts/register_provider.html", {"form": form})


def register_customer(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your customer account has been created.")
            return redirect("/")
    else:
        form = CustomerRegistrationForm()
    return render(request, "accounts/register_customer.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser or user.is_staff:
                return redirect("admin_dashboard:overview")
            return redirect("services:dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("/")


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")
