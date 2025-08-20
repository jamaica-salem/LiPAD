# core/views_user_auth.py
"""
Session-based authentication endpoints for User (mirrors core/views_auth.py for Admin).

Provides:
- csrf_view_user      (GET)  -> ensures csrftoken cookie and returns token JSON
- login_user_view     (POST) -> accepts {email, password}, sets request.session['user_id']
- logout_user_view    (POST) -> clears session
- session_user_view   (GET)  -> returns currently-logged-in user info (or isAuthenticated: False)

Security & notes:
- Uses @csrf_protect on POST endpoints and @ensure_csrf_cookie on the CSRF endpoint.
- Uses case-insensitive email lookup and strips whitespace to avoid trivial mismatches.
- Avoids leaking whether an email exists (Generic "Invalid credentials.").
- Uses request.session.flush() on login to prevent session fixation.
- Returns safe user info (password removed).
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import User
from .serializers import UserSerializer

logger = logging.getLogger(__name__)


# --- CSRF endpoint (GET) ---
@require_GET
@ensure_csrf_cookie
def csrf_view_user(request):
    """
    Ensure that a 'csrftoken' cookie exists and return the token in JSON.
    Client should call this before sending POST/unsafe requests.
    """
    token = get_token(request)  # sets csrftoken cookie
    return JsonResponse({"csrfToken": token})


# --- Login endpoint (POST) ---
@require_POST
@csrf_protect
def login_user_view(request):
    """
    Session-based user login.
    Accepts JSON body: { "email": "<email>", "password": "<password>" }.
    On success:
      - prevents session fixation by request.session.flush()
      - sets request.session['user_id'] to the authenticated user's id
      - returns safe user info (no password)
    Errors:
      - 400 for invalid JSON or missing fields
      - 401 for invalid credentials
    """
    try:
        raw = request.body.decode("utf-8")
        payload = json.loads(raw)
    except Exception:
        logger.debug("login_user_view: invalid JSON payload")
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    email = (payload.get("email") or "").strip()
    password = payload.get("password") or ""

    if not email or not password:
        return JsonResponse({"detail": "Email and password are required."}, status=400)

    # Case-insensitive lookup to avoid trivial mismatches (e.g., uppercase letters)
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        # Generic message to avoid exposing which emails exist
        logger.info("User login failed: no user for email=%s", email)
        return JsonResponse({"detail": "Invalid credentials."}, status=401)

    # Use model helper for password checking
    try:
        if not user.check_password(password):
            logger.info("User login failed: bad password for user_id=%s", getattr(user, "id", "unknown"))
            return JsonResponse({"detail": "Invalid credentials."}, status=401)
    except Exception as e:
        logger.exception("Error checking password for user login: %s", e)
        return JsonResponse({"detail": "Invalid credentials."}, status=401)

    # Successful: create session safely
    request.session.flush()  # prevent session fixation: clear any existing session first
    request.session["user_id"] = user.id
    request.session["last_login"] = timezone.now().isoformat()

    # Return safe user info (no password)
    serializer = UserSerializer(user)
    data = serializer.data
    data.pop("password", None)
    return JsonResponse({"user": data}, status=200)


# --- Logout endpoint (POST) ---
@require_POST
@csrf_protect
def logout_user_view(request):
    """
    Logs the user out by clearing the session.
    """
    request.session.flush()
    return JsonResponse({"detail": "Logged out"}, status=200)


# --- Session user info endpoint (GET) ---
@require_GET
def session_user_view_user(request):
    """
    Return currently logged in user info if session exists.
    JSON:
      - { isAuthenticated: False, user: null }  if no session
      - { isAuthenticated: True, user: {...} }   if user is authenticated
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({"isAuthenticated": False, "user": None})

    user = get_object_or_404(User, id=user_id)
    serializer = UserSerializer(user)
    data = serializer.data
    data.pop("password", None)
    return JsonResponse({"isAuthenticated": True, "user": data})
