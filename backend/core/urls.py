from django.urls import path, include
from rest_framework.routers import DefaultRouter
# 👇 1. Import the new view here
from .views import (
    AdminViewSet, 
    UserViewSet, 
    AdminImageViewSet, 
    UserImageViewSet, 
    process_image, 
    process_gan_only, 
    reprocess_image
)
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

# Separate routers for different roles
admin_router = DefaultRouter()
admin_router.register(r"images", AdminImageViewSet, basename="admin-image")
admin_router.register(r"users", UserViewSet, basename="admin-user")

user_router = DefaultRouter()
user_router.register(r"images", UserImageViewSet, basename="user-image")

# Main admin management router
main_router = DefaultRouter()
main_router.register(r"admins", AdminViewSet, basename='admin')

urlpatterns = [
    # Main admin routes
    path("", include(main_router.urls)),
    
    # Role-specific routes
    path("admin/", include(admin_router.urls)),
    path("user/", include(user_router.urls)),
    
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
    
    # Image processing endpoints (role-aware)
    path("process/", process_image, name="process-image"),
    path("process-gan/", process_gan_only, name="process-gan"),
    # 👇 2. Add the new URL path here
    path("reprocess/", reprocess_image, name="reprocess-image"), 
]
