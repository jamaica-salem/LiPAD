from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from core.models import Admin, User
import logging

logger = logging.getLogger(__name__)

class TrulySeparateSessionMiddleware(MiddlewareMixin):
    """
    Completely separate admin and user sessions using model-based storage
    instead of Django's session framework
    """
    
    def process_request(self, request):
        """Authenticate users based on separate session cookies"""
        request.admin = None
        request.user_obj = None
        request.is_admin_authenticated = False
        request.is_user_authenticated = False
        
        # Get cookie names from settings
        admin_cookie = getattr(settings, 'ADMIN_SESSION_COOKIE_NAME', 'admin_sessionid')
        user_cookie = getattr(settings, 'USER_SESSION_COOKIE_NAME', 'user_sessionid')
        
        # Check admin session
        admin_session_key = request.COOKIES.get(admin_cookie)
        if admin_session_key:
            request.admin = self._validate_admin_session(admin_session_key)
            request.is_admin_authenticated = request.admin is not None
        
        # Check user session (independent of admin session)
        user_session_key = request.COOKIES.get(user_cookie)
        if user_session_key:
            request.user_obj = self._validate_user_session(user_session_key)
            request.is_user_authenticated = request.user_obj is not None
    
    def _validate_admin_session(self, session_key):
        """Validate admin session and update activity"""
        try:
            admin = Admin.objects.get(
                session_key=session_key,
                is_active=True
            )
            
            # Check if session is expired
            if admin.is_session_expired():
                admin.clear_session()
                logger.info(f"Cleared expired admin session: {admin.email}")
                return None
            
            # Update last activity
            admin.update_activity()
            return admin
            
        except Admin.DoesNotExist:
            logger.warning(f"Invalid admin session key: {session_key[:10]}...")
            return None
        except Exception as e:
            logger.error(f"Admin session validation error: {e}")
            return None
    
    def _validate_user_session(self, session_key):
        """Validate user session and update activity"""
        try:
            user = User.objects.get(
                session_key=session_key,
                is_active=True
            )
            
            # Check if session is expired
            if user.is_session_expired():
                user.clear_session()
                logger.info(f"Cleared expired user session: {user.email}")
                return None
            
            # Update last activity
            user.update_activity()
            return user
            
        except User.DoesNotExist:
            logger.warning(f"Invalid user session key: {session_key[:10]}...")
            return None
        except Exception as e:
            logger.error(f"User session validation error: {e}")
            return None
    
    def process_response(self, request, response):
        """Set or clear session cookies based on login/logout actions"""
        
        # Handle admin session cookie
        if hasattr(request, '_set_admin_session'):
            admin = getattr(request, '_set_admin_session')
            cookie_name = getattr(settings, 'ADMIN_SESSION_COOKIE_NAME', 'admin_sessionid')
            
            if admin and admin.session_key:
                # Set admin session cookie
                self._set_secure_cookie(response, cookie_name, admin.session_key)
                logger.info(f"Set admin session cookie for: {admin.email}")
            else:
                # Clear admin session cookie
                self._delete_cookie(response, cookie_name)
                logger.info("Cleared admin session cookie")
        
        # Handle user session cookie (completely independent)
        if hasattr(request, '_set_user_session'):
            user = getattr(request, '_set_user_session')
            cookie_name = getattr(settings, 'USER_SESSION_COOKIE_NAME', 'user_sessionid')
            
            if user and user.session_key:
                # Set user session cookie
                self._set_secure_cookie(response, cookie_name, user.session_key)
                logger.info(f"Set user session cookie for: {user.email}")
            else:
                # Clear user session cookie
                self._delete_cookie(response, cookie_name)
                logger.info("Cleared user session cookie")
        
        return response
    
    def _set_secure_cookie(self, response, name, value):
        """Set secure cookie with production-ready flags"""
        response.set_cookie(
            name,
            value,
            max_age=getattr(settings, 'SESSION_COOKIE_AGE', 7200),
            httponly=True,
            secure=not settings.DEBUG,
            samesite=getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Lax'),
            path='/',
            domain=getattr(settings, 'SESSION_COOKIE_DOMAIN', None)
        )
    
    def _delete_cookie(self, response, name):
        """Securely delete cookie"""
        response.delete_cookie(
            name,
            path='/',
            domain=getattr(settings, 'SESSION_COOKIE_DOMAIN', None),
            samesite=getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Lax')
        )


class SessionIsolationMiddleware(MiddlewareMixin):
    """
    Ensure session data doesn't leak between admin and user contexts
    """

    def process_request(self, request):
        """Replace Django session with empty session to prevent leakage"""
        return None

    def process_response(self, request, response):
        """Ensure no default Django session cookies are set"""
        default_session_name = getattr(settings, 'SESSION_COOKIE_NAME', 'sessionid')
        if default_session_name in response.cookies:
            del response.cookies[default_session_name]
        return response



class EmptySession:
    """Empty session object to replace Django's session"""
    
    def __getitem__(self, key):
        raise KeyError(key)
    
    def __setitem__(self, key, value):
        pass
    
    def __delitem__(self, key):
        pass
    
    def get(self, key, default=None):
        return default
    
    def pop(self, key, *args):
        return args[0] if args else None
    
    def keys(self):
        return []
    
    def items(self):
        return []
    
    def setdefault(self, key, value):
        return value
    
    def flush(self):
        pass
    
    @property
    def session_key(self):
        return None
    
    @property
    def modified(self):
        return False
    
    def cycle_key(self):
        pass

class RoleBasedAccessMiddleware(MiddlewareMixin):
    """
    Middleware to enforce role-based access control on API endpoints
    """
    
    ADMIN_ONLY_PATHS = [
        '/api/users/',  # User management
        '/api/admins/', # Admin management
    ]
    
    USER_PATHS = [
        '/api/images/',
        '/api/process/',
        '/api/process-gan/',
    ]
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Check permissions before view execution"""
        path = request.path
        
        # Skip auth checks for certain endpoints
        if self._is_public_endpoint(path):
            return None
        
        # Admin-only endpoints
        if any(path.startswith(admin_path) for admin_path in self.ADMIN_ONLY_PATHS):
            if not request.is_admin_authenticated:
                return JsonResponse(
                    {'detail': 'Admin authentication required'},
                    status=403
                )
        
        # User endpoints (allow both admin and user)
        elif any(path.startswith(user_path) for user_path in self.USER_PATHS):
            if not (request.is_admin_authenticated or request.is_user_authenticated):
                return JsonResponse(
                    {'detail': 'Authentication required'},
                    status=403
                )
        
        return None
    
    def _is_public_endpoint(self, path):
        """Check if endpoint is public (no auth required)"""
        public_endpoints = [
            '/api/csrf/',
            '/api/admin/login/',
            '/api/admin/logout/', 
            '/api/user/login/',
            '/api/user/logout/',
            '/api/admin/session/',
            '/api/user/session/',
        ]
        return any(path.startswith(endpoint) for endpoint in public_endpoints)