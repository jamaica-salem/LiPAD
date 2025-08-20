from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Admin, User, Image
from .serializers import AdminSerializer, UserSerializer, ImageSerializer, UserLoginSerializer, AdminLoginSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

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
    
class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all().order_by('-created_at')
    serializer_class = ImageSerializer
    parser_classes = [MultiPartParser, FormParser]  # for file uploads

    def create(self, request, *args, **kwargs):
        """Handle file upload errors gracefully"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except serializers.ValidationError as e:
            return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
