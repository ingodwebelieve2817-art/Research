from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps


def superuser_required(view_func):
    """
    Decorator for views that checks if the user is logged in and is a superuser.
    If the user is not logged in, they are redirected to the login page.
    If the user is logged in but is not a superuser, PermissionDenied (403 HTTP response) is raised.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this page.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
