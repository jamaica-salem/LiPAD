from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def health_check(request):
    """Simple health check endpoint for load balancers"""
    return JsonResponse({"status": "healthy", "service": "lipad-backend"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path("health/", health_check, name="health-check"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve media files in development only, comment out for now
"""if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers for production
if not settings.DEBUG:
    def handler404(request, exception):
        return JsonResponse({"detail": "Not found"}, status=404)
    
    def handler500(request):
        return JsonResponse({"detail": "Server error"}, status=500)
    
    handler404 = handler404
    handler500 = handler5"""