from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminViewSet, UserViewSet, ImageViewSet, process_image, process_gan_only
from .views_auth import (
    csrf_view,
    admin_login,
    admin_logout,
    admin_session_info,
    user_login,
    user_logout,
    user_session_info,
    change_password,
)

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r"admins", AdminViewSet, basename='admin')
router.register(r"users", UserViewSet, basename='user') 
router.register(r"images", ImageViewSet, basename='image')

urlpatterns = [
    # DRF ViewSet routes
    path("", include(router.urls)),
    
    # CSRF token endpoint
    path("csrf/", csrf_view, name="csrf-token"),
    
    # Admin authentication endpoints
    path("admin/login/", admin_login, name="admin-login"),
    path("admin/logout/", admin_logout, name="admin-logout"),
    path("admin/session/", admin_session_info, name="admin-session"),
    
    # User authentication endpoints  
    path("user/login/", user_login, name="user-login"),
    path("user/logout/", user_logout, name="user-logout"),
    path("user/session/", user_session_info, name="user-session"),
    
    # Shared endpoints
    path("change-password/", change_password, name="change-password"),
    
    # Image processing endpoints
    path("process/", process_image, name="process-image"),
    path("process-gan/", process_gan_only, name="process-gan"),
]