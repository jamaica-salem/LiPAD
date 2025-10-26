# core/views.py - Secure ViewSets with proper role-based access control
import os
import io
import logging
from django.http import JsonResponse
from django.utils import timezone
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import viewsets, status, serializers, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.parsers import MultiPartParser, FormParser
from PIL import Image as PilImage
from django.core.files.base import ContentFile
from django.views.decorators.cache import never_cache
from .models import Admin, User, Image
from .serializers import AdminSerializer, UserSerializer, ImageSerializer
from core.ml.classifier.utils import load_cnn_model, predict_image
from core.ml.gans.gan_selector import load_gans, run_gan
from core.ml.ocr.ocr_wrapper import load_ocr, run_ocr
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

# Custom Permission Classes
class IsAdminAuthenticated(permissions.BasePermission):
    """Ensure request has valid admin authentication"""
    message = "Admin authentication required"
    
    def has_permission(self, request, view):
        return getattr(request, 'is_admin_authenticated', False) and request.admin

class IsUserAuthenticated(permissions.BasePermission):
    """Ensure request has valid user authentication"""
    message = "User authentication required"
    
    def has_permission(self, request, view):
        return getattr(request, 'is_user_authenticated', False) and request.user_obj

class IsAdminOrOwner(permissions.BasePermission):
    """Admin can access all, users can only access their own data"""
    message = "Access denied"
    
    def has_permission(self, request, view):
        return (getattr(request, 'is_admin_authenticated', False) or 
                getattr(request, 'is_user_authenticated', False))
    
    def has_object_permission(self, request, view, obj):
        if getattr(request, 'is_admin_authenticated', False):
            return True
        if getattr(request, 'is_user_authenticated', False):
            return obj.user == request.user_obj
        return False

class SecureViewMixin:
    """Mixin providing security utilities for ViewSets"""
    
    def check_admin_permission(self, request):
        """Ensure request has admin authentication"""
        if not request.is_admin_authenticated:
            raise PermissionDenied("Admin authentication required")
        return request.admin
    
    def check_user_permission(self, request):
        """Ensure request has user authentication (admin or user)"""
        if not (request.is_admin_authenticated or request.is_user_authenticated):
            raise PermissionDenied("Authentication required")
        return request.admin if request.is_admin_authenticated else request.user_obj
    
    def get_current_user_for_filtering(self, request):
        """Get current user for data filtering"""
        if request.is_admin_authenticated:
            return None  # Admin sees all data
        elif request.is_user_authenticated:
            return request.user_obj
        else:
            raise PermissionDenied("Authentication required")

@method_decorator(csrf_protect, name='dispatch')
class AdminViewSet(SecureViewMixin, viewsets.ModelViewSet):
    """Admin management viewset - Admin only"""
    queryset = Admin.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = AdminSerializer
    
    def list(self, request, *args, **kwargs):
        """List all admins - Admin only"""
        self.check_admin_permission(request)
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """Get specific admin - Admin only"""
        self.check_admin_permission(request)
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Create new user - Admin only"""
        self.check_admin_permission(request)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Update user - Admin only or self-update"""
        instance = self.get_object()
        
        if request.is_admin_authenticated:
            # Admin can update any user
            return super().update(request, *args, **kwargs)
        elif request.is_user_authenticated and instance.id == request.user_obj.id:
            # User can update their own data (restricted fields)
            allowed_fields = ['first_name', 'middle_name', 'last_name', 'position']
            restricted_data = {k: v for k, v in request.data.items() if k in allowed_fields}
            request._data = restricted_data
            return super().update(request, *args, **kwargs)
        else:
            raise PermissionDenied("Access denied")
    
    def destroy(self, request, *args, **kwargs):
        """Delete user - Admin only"""
        self.check_admin_permission(request)
        return super().destroy(request, *args, **kwargs)
    
@method_decorator(csrf_protect, name='dispatch')
class UserViewSet(SecureViewMixin, viewsets.ModelViewSet):
    """User management viewset - Admin only for management, Users can view their own data"""
    serializer_class = UserSerializer
    
    def get_queryset(self):
        """Return users based on permissions"""
        if not hasattr(self.request, 'is_admin_authenticated'):
            return User.objects.none()
        
        if self.request.is_admin_authenticated:
            return User.objects.filter(is_active=True).order_by('-created_at')
        elif self.request.is_user_authenticated:
            # Users can only see their own data
            return User.objects.filter(id=self.request.user_obj.id, is_active=True)
        else:
            return User.objects.none()
    
    def list(self, request, *args, **kwargs):
        """List users based on role"""
        self.check_user_permission(request)
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """Get specific user"""
        self.check_user_permission(request)
        
        instance = self.get_object()
        
        # Users can only access their own data
        if request.is_user_authenticated and instance.id != request.user_obj.id:
            raise PermissionDenied("Access denied")
        
        return super().retrieve(request, *args, **kwargs)

# Separate Image ViewSets for different roles
@method_decorator([csrf_protect, never_cache], name='dispatch')
class AdminImageViewSet(SecureViewMixin, viewsets.ModelViewSet):
    """Admin image management - Full access to all images"""
    serializer_class = ImageSerializer
    permission_classes = [IsAdminAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Admin sees all images"""
        return Image.objects.all().order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Admins cannot upload directly - use processing endpoints"""
        return Response(
            {"detail": "Admins cannot upload images directly"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    def destroy(self, request, *args, **kwargs):
        """Admin delete with file cleanup"""
        instance = self.get_object()
        
        try:
            with transaction.atomic():
                # Clean up files
                if instance.before_image and os.path.isfile(instance.before_image.path):
                    os.remove(instance.before_image.path)
                if instance.after_image and os.path.isfile(instance.after_image.path):
                    os.remove(instance.after_image.path)
                
                user_email = instance.user.email if instance.user else "unknown"
                logger.info(f"Image deleted by admin {request.admin.email}: {instance.id} (owner: {user_email})")
                
                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            logger.error(f"Admin image deletion error: {str(e)}")
            return Response(
                {"detail": "Image deletion failed"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@method_decorator([csrf_protect, never_cache], name='dispatch')
class UserImageViewSet(SecureViewMixin, viewsets.ModelViewSet):
    """User image management - Users can only access their own images"""
    serializer_class = ImageSerializer
    permission_classes = [IsUserAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Users only see their own images"""
        if not getattr(self.request, 'is_user_authenticated', False):
            return Image.objects.none()
        return Image.objects.filter(
            user=self.request.user_obj
        ).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """User image upload"""
        # Fix: Check authentication and get user properly
        if not getattr(request, 'is_user_authenticated', False):
            return Response(
                {"detail": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Fix: Use request.user_obj directly
        user = request.user_obj
        if not user:
            return Response(
                {"detail": "User not found"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                
                # Auto-assign to current user
                image = serializer.save(user=user)
                
                logger.info(f"Image uploaded by user {user.email}: {image.id}")
                
                # Return full serialized data with URLs
                response_serializer = self.get_serializer(
                    image, 
                    context={'request': request}
                )
                
                return Response(
                    response_serializer.data, 
                    status=status.HTTP_201_CREATED
                )
        
        except serializers.ValidationError as e:
            logger.warning(f"User image upload validation error: {e.detail}")
            return Response(
                {"errors": e.detail}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"User image upload error: {str(e)}", exc_info=True)
            return Response(
                {"detail": f"Image upload failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """User delete own image"""
        instance = self.get_object()
        
        # Double-check ownership
        if instance.user_id != request.user_obj.id:
            raise PermissionDenied("Access denied")
        
        try:
            with transaction.atomic():
                # Clean up files
                if instance.before_image and os.path.isfile(instance.before_image.path):
                    os.remove(instance.before_image.path)
                if instance.after_image and os.path.isfile(instance.after_image.path):
                    os.remove(instance.after_image.path)
                
                logger.info(f"Image deleted by user {request.user_obj.email}: {instance.id}")
                
                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            logger.error(f"User image deletion error: {str(e)}")
            return Response(
                {"detail": "Image deletion failed"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
# Initialize ML models once at startup
try:
    load_cnn_model()
    load_gans()
    load_ocr()
    logger.info("ML models loaded successfully")
except Exception as e:
    logger.error(f"Failed to load ML models: {str(e)}")

@api_view(["POST"])
@csrf_protect
def process_image(request):
    """Process image with automatic distortion detection"""
    # Check authentication
    if not (request.is_admin_authenticated or request.is_user_authenticated):
        return JsonResponse({"detail": "Authentication required"}, status=403)
    
    image_id = request.data.get("image_id")
    if not image_id:
        return JsonResponse({"error": "image_id is required"}, status=400)
    
    try:
        with transaction.atomic():
            # Get image with permission check
            try:
                image_obj = Image.objects.get(pk=image_id)
                
                # Check ownership for non-admin users
                if request.is_user_authenticated and not image_obj.is_owned_by(request.user_obj):
                    return JsonResponse({"error": "Access denied"}, status=403)
                    
            except Image.DoesNotExist:
                return JsonResponse({"error": "Image not found"}, status=404)
            
            # Verify file exists
            if not image_obj.before_image or not os.path.isfile(image_obj.before_image.path):
                return JsonResponse({"error": "Image file not found"}, status=404)
            
            image_path = image_obj.before_image.path
            
            # Distortion mapping
            DISTORTION_MAP = {
                "h_blur": "Horizontal Blur",
                "v_blur": "Vertical Blur", 
                "low_qual": "Low Quality",
                "low_light": "Low Light",
                "normal": "Normal",
            }
            
            # Step 1: Classify distortion in original image
            pred = predict_image(image_path)
            before_class_name = pred["class_name"]
            
            # Step 2: Apply appropriate GAN enhancement
            if before_class_name == "normal":
                enhanced_img = PilImage.open(image_path).convert("RGB")
            else:
                enhanced_img = run_gan(image_path, before_class_name)
            
            # Step 3: Re-classify enhanced image
            buffer = io.BytesIO()
            enhanced_img.save(buffer, format="JPEG")
            buffer.seek(0)
            after_pred = predict_image(buffer)
            after_class_name = after_pred["class_name"]
            
            # Map to human-readable names
            before_display = DISTORTION_MAP.get(before_class_name, before_class_name)
            after_display = DISTORTION_MAP.get(after_class_name, after_class_name)
            
            # Step 4: OCR on enhanced image
            ocr_result = run_ocr(enhanced_img)
            if ocr_result and ocr_result[0]:
                plate_text = ocr_result[0][0][1][0]
                confidence = f"{ocr_result[0][0][1][1] * 100:.2f}"
            else:
                plate_text = ""
                confidence = "0"
            
            # Step 5: Save enhanced image
            buffer.seek(0)
            image_obj.after_image.save(
                f"enhanced_{image_obj.id}.jpg",
                ContentFile(buffer.getvalue()),
                save=False
            )
            
            # Step 6: Update database record
            image_obj.plate_no = plate_text
            image_obj.date_deblurred = timezone.now()
            image_obj.distortion_type = before_display
            image_obj.after_distortion_type = after_display
            image_obj.conf_score = confidence
            image_obj.status = "Successful" if after_display == "Normal" and plate_text and len(plate_text) >= 6 and float(confidence) >= 85 else "Failed"
            image_obj.save()
            
            logger.info(f"Image processed successfully: {image_obj.id} by user {request.user_obj.email if request.is_user_authenticated else request.admin.email}")
            
            return JsonResponse({
                "before_distortion": before_display,
                "after_distortion": after_display,
                "ocr": plate_text,
                "confidence": confidence,
                "status": image_obj.status
            })
    
    except Exception as e:
        logger.error(f"Image processing error: {str(e)}")
        return JsonResponse({"error": "Processing failed"}, status=500)

@api_view(["POST"])
@csrf_protect
def reprocess_image(request):
    """
    Creates a new image record for reprocessing. It uses the 'after_image' 
    of an existing record as the 'before_image' for the new one.
    """
    # 1. Check for authenticated user
    if not (request.is_admin_authenticated or request.is_user_authenticated):
        return JsonResponse({"detail": "Authentication required"}, status=403)
    
    original_image_id = request.data.get("image_id")
    if not original_image_id:
        return JsonResponse({"error": "image_id is required"}, status=400)

    try:
        with transaction.atomic():
            # 2. Get the original image, ensuring it exists
            original_image = get_object_or_404(Image, pk=original_image_id)
            
            user = request.user_obj if request.is_user_authenticated else request.admin
            
            # 3. Check ownership for security
            if request.is_user_authenticated and not original_image.is_owned_by(user):
                return JsonResponse({"error": "Access denied"}, status=403)

            # 4. Verify there is a result image to reprocess
            if not original_image.after_image or not hasattr(original_image.after_image, 'path'):
                return JsonResponse({"error": "No processed image available to deblur again."}, status=400)
            
            # 5. Create a new Image instance for the reprocessing task
            new_image = Image(user=original_image.user, status='Processing')
            
            # 6. Read the file content from the original 'after_image'
            original_after_image_file = original_image.after_image
            original_after_image_file.open(mode='rb')
            file_content = original_after_image_file.read()
            original_after_image_file.close()

            new_before_image_name = f"reprocessed_{os.path.basename(original_after_image_file.name)}"
            
            # 7. Save this content to the 'before_image' of the new record
            new_image.before_image.save(
                new_before_image_name,
                ContentFile(file_content),
                save=True  # This saves the new_image instance to the DB
            )

            logger.info(f"Image {original_image_id} queued for reprocessing by {user.email}. New image ID: {new_image.id}")

            # 8. Return the ID of the newly created image record
            return JsonResponse({"new_image_id": new_image.id}, status=201)

    except Image.DoesNotExist:
        return JsonResponse({"error": "Original image not found"}, status=404)
    except Exception as e:
        logger.error(f"Reprocessing setup error for image {original_image_id}: {str(e)}")
        return JsonResponse({"error": "Failed to set up reprocessing."}, status=500)

@api_view(["POST"])
@csrf_protect 
def process_gan_only(request):
    image_id = request.data.get("image_id")
    distortion_key = request.data.get("distortion_type")
    if not image_id or not distortion_key:
        return JsonResponse({"error": "image_id and distortion_type are required"}, status=400)

    print('INNNNNN')
    DISTORTION_MAP = {
        "h_blur": "Horizontal Blur",
        "v_blur": "Vertical Blur",
        "low_qual": "Low Quality",
        "low_light": "Low Light",
        "normal": "Normal",   
    }

    # 1. Get the image from DB
    image_obj = get_object_or_404(Image, pk=image_id)
    image_path = image_obj.before_image.path

    # 2. Run GAN directly (skip initial classification)
    if distortion_key == "normal":
        enhanced_img = PilImage.open(image_path).convert("RGB")
    else:
        enhanced_img = run_gan(image_path, distortion_key)

    # 3. Classify on AFTER image
    buffer = io.BytesIO()
    enhanced_img.save(buffer, format="JPEG")
    buffer.seek(0)
    after_pred = predict_image(buffer)   # classify GAN output
    after_class_name = after_pred["class_name"]

    # Map for human-readable names
    before_class_name = DISTORTION_MAP.get(distortion_key, distortion_key)
    after_class_name = DISTORTION_MAP.get(after_class_name, after_class_name)

    # 4. OCR on AFTER image
    result = run_ocr(enhanced_img)
    if result and result[0]:
        text = result[0][0][1][0]
        conf_score = f"{result[0][0][1][1] * 100:.2f}"
    else:
        text = ""
        conf_score = "0"

    # 5. Save AFTER image
    buffer.seek(0)
    image_obj.after_image.save(
        f"enhanced_{image_obj.id}.jpg", 
        ContentFile(buffer.getvalue()),
        save=False
    )

    # 6. Save results to DB
    image_obj.plate_no = text
    image_obj.date_deblurred = timezone.now()
    image_obj.distortion_type = before_class_name
    image_obj.after_distortion_type = after_class_name
    image_obj.conf_score = conf_score
    image_obj.status = "Successful" if after_class_name == "Normal" and text != '' and len(text) >= 6 and float(conf_score) >= 85 else "Failed"
    image_obj.save()

    print(f'OCR: {text}, Before distortion: {before_class_name}, After distortion: {after_class_name}, Status: {image_obj.status}')

    return JsonResponse({
        "before_distortion": before_class_name,
        "after_distortion": after_class_name,
        "ocr": text,
        "conf_score": conf_score,
        "status": image_obj.status
    })