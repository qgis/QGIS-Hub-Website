from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.contrib.auth.models import User


GROUP_NAME = "Style Managers"
MAP_PUBLISHER_GROUP_NAME = "Map Publishers"


def is_resources_manager(user: User) -> bool:
    """Check if user is the members of Resources Managers group."""

    return user.is_staff or user.groups.filter(name=GROUP_NAME).exists()

def is_map_publisher(user: User) -> bool:
    """Check if user is the members of Map Publisher group."""

    return user.is_staff or user.groups.filter(name=MAP_PUBLISHER_GROUP_NAME).exists()

class ResourceManagerRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to staff users only."""

    def test_func(self):
        return self.request.user.is_staff or is_resources_manager(self.request.user)  # Checks if user is a staff member

    def handle_no_permission(self):
        """Show a 404 to signed in users, and send everyone else to sign in."""
        if self.request.user.is_authenticated:
            return render(self.request, '404.html', status=404)
        # AccessMixin knows the login URL and keeps the page they asked for
        return super().handle_no_permission()

class MapPublisherRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to staff users only."""

    def test_func(self):
        return self.request.user.is_staff or is_map_publisher(self.request.user)  # Checks if user is a staff member

    def handle_no_permission(self):
        """Show a 404 to signed in users, and send everyone else to sign in."""
        if self.request.user.is_authenticated:
            return render(self.request, '404.html', status=404)
        # AccessMixin knows the login URL and keeps the page they asked for
        return super().handle_no_permission()