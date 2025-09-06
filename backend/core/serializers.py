from rest_framework import serializers
from .models import Admin, User, Image
from django.core.files.images import get_image_dimensions
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.contrib.auth.hashers import check_password
from .validators import validate_password_strength

MAX_IMAGE_MB = 100

def validate_image_file(image):
    if image.size > MAX_IMAGE_MB * 1024 * 1024:
        raise serializers.ValidationError(f"Image too large (max {MAX_IMAGE_MB} MB).")
    try:
        get_image_dimensions(image)
    except Exception:
        raise serializers.ValidationError("Invalid image file.")
    return image

class ImageSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    before_image_url = serializers.SerializerMethodField(read_only=True)
    after_image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Image
        fields = ['id','user','before_image','after_image','before_image_url','after_image_url','date_deblurred','plate_no','status','distortion_type','after_distortion_type', 'conf_score', 'created_at']
        read_only_fields = ['id','created_at','before_image_url','after_image_url','user']

    def get_user(self, obj):
        user = obj.user
        if user:
            return {
                'id': user.id,
                'email': getattr(user, 'email', None),
                'first_name': getattr(user, 'first_name', ''),
                'last_name': getattr(user, 'last_name', ''),
            }


    def get_before_image_url(self, obj):
        req = self.context.get('request')
        return req.build_absolute_uri(obj.before_image.url) if obj.before_image and req else None

    def get_after_image_url(self, obj):
        req = self.context.get('request')
        return req.build_absolute_uri(obj.after_image.url) if obj.after_image and req else None

    def validate_before_image(self, image):
        return validate_image_file(image)

    def validate(self, data):
        # Ensure before_image is present on create
        if self.instance is None and 'before_image' not in data:
            raise serializers.ValidationError({'before_image': 'This field is required.'})
        return data

# serializers.py (add import)
from .validators import validate_password_strength

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

