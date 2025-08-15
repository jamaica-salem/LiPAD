from rest_framework import serializers
from .models import Admin, User, Image
from django.core.files.images import get_image_dimensions

# Max image size 10MB
MAX_IMAGE_MB = 100

def validate_image_file(image):
    """Validate uploaded image size and format."""
    if image.size > MAX_IMAGE_MB * 1024 * 1024:
        raise serializers.ValidationError(f"Image too large (max {MAX_IMAGE_MB} MB).")
    try:
        # Ensure the file is a valid image
        get_image_dimensions(image)
    except Exception:
        raise serializers.ValidationError("Invalid image file.")
    return image

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['id','first_name','middle_name','last_name','email','created_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name','middle_name','last_name','email','date_of_birth','position','created_at']

class ImageSerializer(serializers.ModelSerializer):
    """Handles image validation and URL generation for frontend"""
    user = UserSerializer(read_only=True)  # nested user info
    before_image_url = serializers.SerializerMethodField(read_only=True)
    after_image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Image
        fields = [
            'id', 'user', 'before_image', 'after_image',
            'before_image_url', 'after_image_url',
            'date_deblurred', 'plate_no', 'status', 'distortion_type', 'created_at'
        ]
        read_only_fields = ['id','created_at','before_image_url','after_image_url']

    def get_before_image_url(self, obj):
        """Return absolute URL for Vue frontend"""
        request = self.context.get('request')
        if obj.before_image and request:
            return request.build_absolute_uri(obj.before_image.url)
        return None

    def get_after_image_url(self, obj):
        """Return absolute URL for Vue frontend"""
        request = self.context.get('request')
        if obj.after_image and request:
            return request.build_absolute_uri(obj.after_image.url)
        return None

    # Validate images before saving
    def validate_before_image(self, image):
        return validate_image_file(image)

    def validate_after_image(self, image):
        return validate_image_file(image)
