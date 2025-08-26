from rest_framework import viewsets, status, permissions, throttling, serializers
from rest_framework.response import Response
from .models import Admin, User, Image
from .serializers import AdminSerializer, UserSerializer, ImageSerializer, UserLoginSerializer, AdminLoginSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie



class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all().order_by('-created_at')
    serializer_class = AdminSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    pagination_class = None  

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    """
    Session-based user login.
    Mirrors the admin session-based login flow (no JWT).
    Accepts JSON: { "email": "...", "password": "..." }
    On success: sets request.session['user_id'] and returns safe user info.
    """
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Prevent session fixation
        request.session.flush()
        # Store minimal identifier in session
        request.session['user_id'] = user.id
        # Optionally store last_login time for convenience (not required)
        from django.utils import timezone
        request.session['last_login'] = timezone.now().isoformat()

        # Return safe user info (do not return password)
        data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        return Response({'user': data}, status=status.HTTP_200_OK)
    
class UploadThrottle(throttling.AnonRateThrottle):
    rate = '20/min'  # modest throttle for uploads

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CsrfView(APIView):
    """
    GET /api/csrf/ – sets csrftoken cookie for the browser (no body).
    """
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return Response({'detail': 'CSRF cookie set'})

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all().order_by('-created_at')
    serializer_class = ImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]  # session auth enforced in create
    throttle_classes = [UploadThrottle]

    def create(self, request, *args, **kwargs):
        # require session-based user_id (set by your login view)
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_403_FORBIDDEN)

        # defend against stale sessions
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            request.session.flush()
            return Response({'detail': 'Invalid session. Please log in again.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            instance = serializer.save(user=user)  # attach user FK
            out = self.get_serializer(instance, context={'request': request})
            return Response(out.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as exc:
            return Response({'errors': exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            # log exception server-side; return safe message client-side
            return Response({'errors': 'Server error while saving image.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)