# core/views_auth.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.middleware.csrf import get_token
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone

from .models import Admin  # your Admin model
from .serializers import AdminSerializer

# --- CSRF endpoint (GET) ---
@require_GET
@ensure_csrf_cookie
def csrf_view(request):
    """
    Ensure that a 'csrftoken' cookie exists and return the token in JSON.
    Client should call this before sending POST/unsafe requests.
    """
    token = get_token(request)  # sets csrftoken cookie
    return JsonResponse({"csrfToken": token})

# --- Login endpoint (POST) ---
@require_POST
@csrf_protect
def login_view(request):
    """
    Accepts JSON body { email, password }.
    Performs secure password check against Admin model, and on success:
    - sets request.session['admin_id']
    - returns serialized admin info (no password)
    """
    try:
        data = request.body.decode("utf-8")
        import json
        payload = json.loads(data)
    except Exception:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        return JsonResponse({"detail": "Email and password are required."}, status=400)

    try:
        admin = Admin.objects.get(email=email)
    except Admin.DoesNotExist:
        # Generic error to avoid exposing which emails exist
        return JsonResponse({"detail": "Invalid credentials."}, status=401)

    # Use Django's secure hash check
    if not check_password(password, admin.password):
        return JsonResponse({"detail": "Invalid credentials."}, status=401)

    # Successful: create session
    request.session.flush()  # prevent session fixation: clear any existing session first
    request.session['admin_id'] = admin.id
    # Optionally store last_login time
    request.session['last_login'] = timezone.now().isoformat()

    # Optionally set expiry (e.g., 2 hours) — server-side session expiry
    # request.session.set_expiry(60 * 60 * 2)

    # Return safe admin info (no password)
    serializer = AdminSerializer(admin)
    data = serializer.data
    data.pop('password', None)  # ensure not returned
    return JsonResponse({"admin": data})

# --- Logout endpoint (POST) ---
@require_POST
@csrf_protect
def logout_view(request):
    """
    Logs the admin out by clearing the session.
    """
    # flush clears session data and deletes the cookie
    request.session.flush()
    return JsonResponse({"detail": "Logged out"}, status=200)

# --- Session user info endpoint (GET) ---
@require_GET
def session_user_view(request):
    """
    Return currently logged in admin info if session exists.
    """
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return JsonResponse({"isAuthenticated": False, "admin": None})
    admin = get_object_or_404(Admin, id=admin_id)
    # Return minimal safe fields
    serializer = AdminSerializer(admin)
    data = serializer.data
    data.pop('password', None)
    return JsonResponse({"isAuthenticated": True, "admin": data})
