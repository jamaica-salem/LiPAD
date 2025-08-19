from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import AdminViewSet, UserViewSet, ImageViewSet, UserLoginView, AdminLoginView

router = DefaultRouter()
router.register(r'admins', AdminViewSet)
router.register(r'users', UserViewSet)
router.register(r'images', ImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('auth/admin-login/', AdminLoginView.as_view(), name='admin-login'),
]
