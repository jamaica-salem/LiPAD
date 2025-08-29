from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import AdminViewSet, UserViewSet, ImageViewSet, UserLoginView
from .views_auth import csrf_view, login_view, logout_view, session_user_view
from .views_user_auth import csrf_view_user, login_user_view, logout_user_view, session_user_view_user
from . import views

router = DefaultRouter()
router.register(r'admins', AdminViewSet)
router.register(r'users', UserViewSet)
router.register(r'images', ImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("lipad/login/", UserLoginView.as_view(), name='user-login'),
    path("csrf/", csrf_view, name="csrf"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("user/", session_user_view, name="session-user"),
    path("user/csrf/", csrf_view_user, name="user-csrf"),
    path("user/login/", login_user_view, name="user-login"),
    path("user/logout/", logout_user_view, name="user-logout"),
    path("user/session/", session_user_view_user, name="use r-session"),
    path("process/", views.process_image, name="process_image"),
    path("process-gan/", views.process_gan_only, name="process_gan_only")
]
