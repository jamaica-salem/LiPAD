from rest_framework import serializers
from .models import Admin, User, Image
from django.core.files.images import get_image_dimensions
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.contrib.auth.hashers import check_password

# Max image size 100MB
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
    """
    Serializer for Admin model.
    Hashes password automatically when creating/updating.
    """
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Admin
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'email', 'password', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        """Create Admin with hashed password and proper error handling."""
        try:
            with transaction.atomic():  # ensures atomic DB transaction
                password = validated_data.pop('password')
                admin = Admin(**validated_data)
                # Hash the password before saving
                admin.password = make_password(password)
                admin.save()
                return admin
        except Exception as e:
            raise serializers.ValidationError({"detail": f"Failed to create admin: {str(e)}"})

    def update(self, instance, validated_data):
        """Update Admin and hash new password if provided."""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.password = make_password(password)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Automatically hashes password.
    """
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'middle_name', 'last_name',
            'email', 'password', 'position', 'date_of_birth', 'created_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True}  # never send password to frontend
        }

    def create(self, validated_data):
        """Create user with hashed password and proper error handling."""
        try:
            with transaction.atomic():
                password = validated_data.pop('password', None)
                user = User(**validated_data)
                if password:
                    # If model has set_password (recommended), use it
                    if hasattr(user, 'set_password'):
                        user.set_password(password)
                    else:
                        # fallback hashing
                        user.password = make_password(password)
                user.save()
                return user
        except Exception as e:
            raise serializers.ValidationError({"detail": f"Failed to create user: {str(e)}"})

    def update(self, instance, validated_data):
        """Update user and hash new password if provided."""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            if hasattr(instance, 'set_password'):
                instance.set_password(password)
            else:
                instance.password = make_password(password)
        instance.save()
        return instance

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Check user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid credentials."})

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError({"detail": "Invalid credentials."})

        data['user'] = user
        return data


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
