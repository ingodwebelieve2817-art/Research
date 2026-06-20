from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q
from .decorators import superuser_required

from services.models import ServiceProvider, SERVICE_CATEGORIES
from customers.models import Customer
from projects.models import Project
from subscriptions.models import Subscription
from activities.models import ActivityLog

User = get_user_model()


@superuser_required
def dashboard_overview(request):
    """
    Overview page showing system analytics and statistics.
    """
    total_users = User.objects.count()
    total_providers = ServiceProvider.objects.count()
    total_customers = Customer.objects.count()
    total_projects = Project.objects.count()
    active_subscriptions = Subscription.objects.filter(is_active=True).count()

    # Project distribution by status
    project_status_counts = {
        "pending": Project.objects.filter(status="pending").count(),
        "in_progress": Project.objects.filter(status="in_progress").count(),
        "completed": Project.objects.filter(status="completed").count(),
        "cancelled": Project.objects.filter(status="cancelled").count(),
    }
    
    project_status_data = []
    for skey, scount in project_status_counts.items():
        percentage = (scount / total_projects * 100) if total_projects > 0 else 0
        project_status_data.append({
            "status": skey,
            "status_display": skey.replace("_", " ").capitalize(),
            "count": scount,
            "percentage": percentage
        })

    # Latest activities
    recent_activities = ActivityLog.objects.order_by("-created_at")[:10]

    context = {
        "total_users": total_users,
        "total_providers": total_providers,
        "total_customers": total_customers,
        "total_projects": total_projects,
        "active_subscriptions": active_subscriptions,
        "project_status_data": project_status_data,
        "recent_activities": recent_activities,
    }
    return render(request, "admin_dashboard/overview.html", context)


@superuser_required
def user_list(request):
    """
    Lists all users (service providers + super admins) in the system with search.
    """
    query = request.GET.get("q", "").strip()
    users = User.objects.all().order_by("-created_at")

    if query:
        users = users.filter(
            Q(username__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query)
        )

    context = {
        "users": users,
        "query": query,
    }
    return render(request, "admin_dashboard/user_list.html", context)


@superuser_required
def user_detail(request, pk):
    """
    Displays detailed information about a user, including their ServiceProvider profile,
    projects, and activity logs.
    """
    user = get_object_or_404(User, pk=pk)

    # Fetch provider profile if it exists
    provider = getattr(user, "provider_profile", None)

    # Fetch user's projects and activity logs
    projects = []
    if provider:
        projects = Project.objects.filter(provider=provider).order_by("-created_at")

    activities = ActivityLog.objects.filter(user=user).order_by("-created_at")

    context = {
        "admin_user": user,
        "provider": provider,
        "projects": projects,
        "activities": activities,
    }
    return render(request, "admin_dashboard/user_detail.html", context)


@superuser_required
def user_edit(request, pk):
    """
    Allows the Super Admin to edit a user's details and their associated ServiceProvider profile.
    """
    user = get_object_or_404(User, pk=pk)
    provider = getattr(user, "provider_profile", None)

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()

        # Update User
        user.email = email
        user.phone = phone
        user.save()

        # Update Service Provider Profile if exists
        if provider:
            provider.business_name = request.POST.get("business_name", "").strip()
            provider.category = request.POST.get("category", "").strip()
            provider.city = request.POST.get("city", "").strip()
            provider.address = request.POST.get("address", "").strip()
            provider.whatsapp_number = request.POST.get("whatsapp_number", "").strip()
            provider.facebook_page_url = request.POST.get("facebook_page_url", "").strip()
            provider.website = request.POST.get("website", "").strip()
            provider.save()

        # Log change activity
        ActivityLog.objects.create(
            user=request.user,
            action="Admin Modified User Details",
            details=f"Super Admin updated information for user: {user.username} (ID: {user.id})",
        )

        messages.success(request, f"User details for '{user.username}' successfully updated.")
        return redirect("admin_dashboard:user_detail", pk=user.pk)

    context = {
        "admin_user": user,
        "provider": provider,
        "categories": SERVICE_CATEGORIES,
    }
    return render(request, "admin_dashboard/user_edit.html", context)


@superuser_required
def user_toggle_status(request, pk):
    """
    POST view to suspend (deactivate) or reactivate a user.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("admin_dashboard:user_list")

    user = get_object_or_404(User, pk=pk)

    # Protect other superusers from suspension
    if user.is_superuser:
        messages.error(request, "Super Admin accounts cannot be suspended.")
        return redirect("admin_dashboard:user_detail", pk=user.pk)

    user.is_active = not user.is_active
    user.save()

    status_str = "Reactivated" if user.is_active else "Suspended"

    # Log suspend/reactivate activity
    ActivityLog.objects.create(
        user=request.user,
        action=f"User {status_str}",
        details=f"Super Admin {status_str.lower()} user: {user.username} (ID: {user.id})",
    )

    messages.success(request, f"User '{user.username}' has been successfully {status_str.lower()}.")
    return redirect("admin_dashboard:user_detail", pk=user.pk)


@superuser_required
def user_delete(request, pk):
    """
    POST view to permanently delete a user from the system.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("admin_dashboard:user_list")

    user = get_object_or_404(User, pk=pk)

    # Protect superusers from deletion
    if user.is_superuser:
        messages.error(request, "Super Admin accounts cannot be deleted.")
        return redirect("admin_dashboard:user_detail", pk=user.pk)

    username = user.username
    user.delete()

    # Log delete activity
    ActivityLog.objects.create(
        user=request.user,
        action="User Deleted By Admin",
        details=f"Super Admin permanently deleted user: {username} (ID: {pk})",
    )

    messages.success(request, f"User '{username}' was permanently deleted.")
    return redirect("admin_dashboard:user_list")
