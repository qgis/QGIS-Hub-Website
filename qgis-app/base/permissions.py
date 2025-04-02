from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect

class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to staff users only."""
    
    def test_func(self):
        return self.request.user.is_staff  # Checks if user is a staff member
    
    def handle_no_permission(self):
        """Redirects unauthorized users to a login page or a custom error page."""
        if self.request.user.is_authenticated:
            return render(self.request, '404.html', status=404)
        return redirect('login') 