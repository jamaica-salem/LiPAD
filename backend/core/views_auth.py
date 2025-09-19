# core/views_auth.py - Secure authentication views
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.middleware.csrf import get_token
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from .models import Admin, User
from .serializers import AdminSerializer, UserSerializer

logger = logging.getLogger(__name__)

# --- CSRF Token Management ---
@require_GET
@ensure_csrf_cookie
def csrf_view(request):
    """Provide CSRF token for authentication requests"""
    token = get_token(request)
    return JsonResponse({"csrfToken": token})

# --- Admin Authentication ---
@require_POST
@csrf_protect
def admin_login(request):
    """Secure admin login with session management"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"detail": "Invalid JSON payload"}, status=400)
    
    email = payload.get("email", "").strip().lower()
    password = payload.get("password", "")
    
    # Input validation
    if not email or not password:
        return JsonResponse({"detail": "Email and password are required"}, status=400)
    
    # Rate limiting check (implement with django-ratelimit in production)
    # @ratelimit(key='ip', rate='5/m', method='POST', block=True)
    
    try:
        with transaction.atomic():
            admin = Admin.authenticate(email, password)
            
            if not admin:
                logger.warning(f"Failed admin login attempt for: {email} from IP: {request.META.get('REMOTE_ADDR')}")
                return JsonResponse({"detail": "Invalid credentials"}, status=401)
            
            # Clear any existing session
            if admin.session_key:
                admin.clear_session()
            
            # Create new session
            session_key = admin.create_session()
            
            # Mark for middleware to set cookie
            request._set_admin_session = admin
            
            logger.info(f"Admin login successful: {admin.email}")
            
            # Return safe user data
            admin_data = AdminSerializer(admin).data
            admin_data.pop("password", None)
            
            return JsonResponse({
                "admin": admin_data,
                "sessionExpiry": (timezone.now() + timezone.timedelta(seconds=settings.SESSION_COOKIE_AGE)).isoformat()
            })
    
    except Exception as e:
        logger.error(f"Admin login error: {str(e)}")
        return JsonResponse({"detail": "Authentication service unavailable"}, status=500)

@require_POST
@csrf_protect
def admin_logout(request):
    """Secure admin logout"""
    try:
        if request.admin:
            request.admin.clear_session()
            logger.info(f"Admin logout: {request.admin.email}")
        
        # Mark for middleware to delete cookie
        request._set_admin_session = None
        
        return JsonResponse({"detail": "Successfully logged out"})
    
    except Exception as e:
        logger.error(f"Admin logout error: {str(e)}")
        return JsonResponse({"detail": "Logout completed"})  # Always succeed

@require_GET
def admin_session_info(request):
    """Get current admin session information"""
    if not request.is_admin_authenticated:
        return JsonResponse({"isAuthenticated": False, "admin": None})
    
    admin_data = AdminSerializer(request.admin).data
    admin_data.pop("password", None)
    
    return JsonResponse({
        "isAuthenticated": True,
        "admin": admin_data,
        "sessionExpiry": (request.admin.last_activity + timezone.timedelta(seconds=settings.SESSION_COOKIE_AGE)).isoformat()
    })

# --- User Authentication ---
@require_POST
@csrf_protect
def user_login(request):
    """Secure user login with session management"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"detail": "Invalid JSON payload"}, status=400)
    
    email = payload.get("email", "").strip().lower()
    password = payload.get("password", "")
    
    # Input validation
    if not email or not password:
        return JsonResponse({"detail": "Email and password are required"}, status=400)
    
    try:
        with transaction.atomic():
            user = User.authenticate(email, password)
            
            if not user:
                logger.warning(f"Failed user login attempt for: {email} from IP: {request.META.get('REMOTE_ADDR')}")
                return JsonResponse({"detail": "Invalid credentials"}, status=401)
            
            # Clear any existing session
            if user.session_key:
                user.clear_session()
            
            # Create new session
            session_key = user.create_session()
            
            # Mark for middleware to set cookie
            request._set_user_session = user
            
            logger.info(f"User login successful: {user.email}")
            
            # Return safe user data
            user_data = UserSerializer(user).data
            user_data.pop("password", None)
            
            return JsonResponse({
                "user": user_data,
                "sessionExpiry": (timezone.now() + timezone.timedelta(seconds=settings.SESSION_COOKIE_AGE)).isoformat()
            })
    
    except Exception as e:
        logger.error(f"User login error: {str(e)}")
        return JsonResponse({"detail": "Authentication service unavailable"}, status=500)

@require_POST
@csrf_protect
def user_logout(request):
    """Secure user logout"""
    try:
        if request.user_obj:
            request.user_obj.clear_session()
            logger.info(f"User logout: {request.user_obj.email}")
        
        # Mark for middleware to delete cookie
        request._set_user_session = None
        
        return JsonResponse({"detail": "Successfully logged out"})
    
    except Exception as e:
        logger.error(f"User logout error: {str(e)}")
        return JsonResponse({"detail": "Logout completed"})  # Always succeed

@require_GET
def user_session_info(request):
    """Get current user session information"""
    if not request.is_user_authenticated:
        return JsonResponse({"isAuthenticated": False, "user": None})
    
    user_data = UserSerializer(request.user_obj).data
    user_data.pop("password", None)
    
    return JsonResponse({
        "isAuthenticated": True,
        "user": user_data,
        "sessionExpiry": (request.user_obj.last_activity + timezone.timedelta(seconds=settings.SESSION_COOKIE_AGE)).isoformat()
    })

# --- Password Change (Bonus security feature) ---
@require_POST
@csrf_protect
def change_password(request):
    """Secure password change for authenticated users"""
    if not (request.is_admin_authenticated or request.is_user_authenticated):
        return JsonResponse({"detail": "Authentication required"}, status=401)
    
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"detail": "Invalid JSON payload"}, status=400)
    
    current_password = payload.get("currentPassword", "")
    new_password = payload.get("newPassword", "")
    
    if not current_password or not new_password:
        return JsonResponse({"detail": "Current and new passwords required"}, status=400)
    
    # Get the current user/admin
    user_obj = request.admin if request.is_admin_authenticated else request.user_obj
    
    try:
        # Verify current password
        if not user_obj.check_password(current_password):
            return JsonResponse({"detail": "Current password is incorrect"}, status=400)
        
        # Validate new password
        validate_password(new_password, user_obj)
        
        # Update password and clear all sessions (force re-login)
        with transaction.atomic():
            user_obj.password = new_password  # Will be hashed in save()
            user_obj.clear_session()
            user_obj.save()
        
        logger.info(f"Password changed for: {user_obj.email}")
        
        return JsonResponse({"detail": "Password changed successfully. Please log in again."})
    
    except ValidationError as e:
        return JsonResponse({"detail": " ".join(e.messages)}, status=400)
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return JsonResponse({"detail": "Password change failed"}, status=500)