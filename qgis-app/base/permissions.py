from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect
from django.contrib.auth.models import User


GROUP_NAME = "Style Managers"


def is_resources_manager(user: User) -> bool:
    """Check if user is the members of Resources Managers group."""

    return user.groups.filter(name=GROUP_NAME).exists()

class ResourceManagerRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to staff users only."""

    def test_func(self):
        return self.request.user.is_staff or is_resources_manager(self.request.user)  # Checks if user is a staff member

    def handle_no_permission(self):
        """Redirects unauthorized users to a login page or a custom error page."""
        if self.request.user.is_authenticated:
            return render(self.request, '404.html', status=404)
        return redirect('login') 