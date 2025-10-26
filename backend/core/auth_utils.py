from django.core.exceptions import PermissionDenied
from .models import Admin, User

def get_current_admin(request):
    """Get currently logged-in admin from session."""
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return None
    try:
        return Admin.objects.get(pk=admin_id, is_active=True)
    except Admin.DoesNotExist:
        request.session.flush()
        return None

def get_current_user(request):
    """Get currently logged-in user from session."""
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        request.session.flush()
        return None

def require_admin(view_func):
    """Decorator to require admin authentication."""
    def wrapped(request, *args, **kwargs):
        if not get_current_admin(request):
            raise PermissionDenied("Admin authentication required")
        return view_func(request, *args, **kwargs)
    return wrapped

def require_user(view_func):
    """Decorator to require user authentication."""
    def wrapped(request, *args, **kwargs):
        if not get_current_user(request):
            raise PermissionDenied("User authentication required")
        return view_func(request, *args, **kwargs)
    return wrapped