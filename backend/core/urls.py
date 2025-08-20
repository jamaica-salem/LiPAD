from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import AdminViewSet, UserViewSet, ImageViewSet, UserLoginView
from .views_auth import csrf_view, login_view, logout_view, session_user_view

router = DefaultRouter()
router.register(r'admins', AdminViewSet)
router.register(r'users', UserViewSet)
router.register(r'images', ImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path("csrf/", csrf_view, name="csrf"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("user/", session_user_view, name="session-user"),
]
