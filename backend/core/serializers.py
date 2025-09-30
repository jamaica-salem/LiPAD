from rest_framework import serializers
from .models import Admin, User, Image
from django.core.files.images import get_image_dimensions
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction
from django.utils.html import strip_tags
from .validators import validate_password_strength, validate_image_content

MAX_IMAGE_MB = 100

class SecureImageSerializer(serializers.ModelSerializer):
    """Enhanced image serializer with security features"""
    user = serializers.SerializerMethodField(read_only=True)
    before_image_url = serializers.SerializerMethodField(read_only=True)
    after_image_url = serializers.SerializerMethodField(read_only=True)
    file_size = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Image
        fields = [
            'id', 'user', 'before_image', 'after_image', 
            'before_image_url', 'after_image_url', 'file_size',
            'date_deblurred', 'plate_no', 'status', 
            'distortion_type', 'after_distortion_type', 
            'conf_score', 'created_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'before_image_url', 
            'after_image_url', 'user', 'file_size'
        ]

    def get_user(self, obj):
        """Safe user data exposure"""
        user = obj.user
        if user:
            return {
                'id': user.id,
                'email': user.email[:3] + "***" if user.email else None,  # Partially mask email
                'first_name': strip_tags(user.first_name or ''),
                'last_name': strip_tags(user.last_name or ''),
            }
        return None

    def get_before_image_url(self, obj):
        """Secure URL generation"""
        request = self.context.get('request')
        if obj.before_image and request:
            return request.build_absolute_uri(obj.before_image.url)
        return None

    def get_after_image_url(self, obj):
        """Secure URL generation"""
        request = self.context.get('request')
        if obj.after_image and request:
            return request.build_absolute_uri(obj.after_image.url)
        return None
    
    def get_file_size(self, obj):
        """Get file size in bytes"""
        if obj.before_image:
            try:
                return obj.before_image.size
            except:
                return None
        return None

    def validate_before_image(self, image):
        """Enhanced image validation"""
        return validate_image_content(image)

    def validate_plate_no(self, value):
        """Sanitize plate number input"""
        if value:
            # Remove HTML tags and limit length
            cleaned = strip_tags(str(value))[:50]
            # Basic sanitization - only allow alphanumeric, spaces, hyphens
            import re
            cleaned = re.sub(r'[^A-Za-z0-9\s\-]', '', cleaned).strip()
            return cleaned
        return value

    def validate(self, data):
        """Cross-field validation"""
        # Ensure before_image is present on create
        if self.instance is None and 'before_image' not in data:
            raise serializers.ValidationError({
                'before_image': 'This field is required for new uploads.'
            })
        return data

# Use the secure serializer
ImageSerializer = SecureImageSerializer

# --- AdminSerializer ---
class AdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Admin
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'email', 'password', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_password(self, value):
        """Enforce strong password policy"""
        return validate_password_strength(value)

    def create(self, validated_data):
        password = validated_data.pop('password')
        validate_password_strength(password)  # extra safety
        admin = Admin(**validated_data)
        admin.password = make_password(password)
        admin.save()
        return admin

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.password = make_password(validate_password_strength(password))
        instance.save()
        return instance


# --- UserSerializer ---
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'email', 'password', 'position', 'date_of_birth', 'created_at']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        """Enforce strong password policy"""
        return validate_password_strength(value)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.password = make_password(validate_password_strength(password))
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.password = make_password(validate_password_strength(password))
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
    
class AdminLoginSerializer(serializers.Serializer):
    """
    Validate admin login credentials.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # Ensure admin exists
        try:
            admin = Admin.objects.get(email=email)
        except Admin.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid credentials."})

        # Verify password
        if not check_password(password, admin.password):
            raise serializers.ValidationError({"detail": "Invalid credentials."})

        data["admin"] = admin
        return data

