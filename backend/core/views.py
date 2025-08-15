from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Admin, User, Image
from .serializers import AdminSerializer, UserSerializer, ImageSerializer
from rest_framework.parsers import MultiPartParser, FormParser

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
