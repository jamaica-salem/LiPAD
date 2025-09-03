import base64
import io
from django.utils import timezone
from django.http import JsonResponse
from rest_framework import viewsets, status, permissions, throttling, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from .models import Admin, User, Image
from .serializers import AdminSerializer, UserSerializer, ImageSerializer, UserLoginSerializer, AdminLoginSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from core.ml.classifier.utils import load_cnn_model, predict_image
from core.ml.gans.gan_selector import load_gans, run_gan
from core.ml.ocr.ocr_wrapper import load_ocr, run_ocr
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from PIL import Image as PilImage
import os


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

    #def get_queryset(self):
    #    admin_id = self.request.session.get('admin_id')
    #    user_id = self.request.session.get('user_id')

        # If admin is logged in, return all images
     #   if admin_id and Admin.objects.filter(id=admin_id).exists():
     #       return Image.objects.all().order_by('-created_at')

        # If normal user is logged in, return only their images
      #  if user_id and User.objects.filter(id=user_id).exists():
        #    return Image.objects.filter(user_id=user_id).order_by('-created_at')

        # If no valid session, return nothing
      #  return Image.objects.none()

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
    
    def destroy(self, request, *args, **kwargs):
        """
        Securely delete an image record along with its files.
        Only allow deletion if the user owns the image or admin.
        """
        instance = self.get_object()
        user_id = request.session.get('user_id')
        admin_id = request.session.get('admin_id')

        if not admin_id and (not user_id or instance.user.id != user_id):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Delete media files safely
        try:
            if instance.before_image and os.path.isfile(instance.before_image.path):
                os.remove(instance.before_image.path)
            if instance.after_image and os.path.isfile(instance.after_image.path):
                os.remove(instance.after_image.path)
        except Exception as e:
            return Response({'detail': f'Error deleting files: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Delete DB record
        instance.delete()
        return Response({'detail': 'Image deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        

load_cnn_model()
load_gans()
load_ocr()

@api_view(["POST"])
def process_image(request):
    image_id = request.data.get("image_id")
    if not image_id:
        return JsonResponse({"error": "No image_id provided"}, status=400)
    
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

    # 2. classify distortion
    pred = predict_image(image_path)
    before_class_name = pred["class_name"]

    # 3. run GAN if distorted
    if before_class_name  == "normal":
        enhanced_img = PilImage.open(image_path).convert("RGB")
    else:
        enhanced_img = run_gan(image_path, before_class_name )

    # 4. classify AGAIN on AFTER image
    buffer = io.BytesIO()
    enhanced_img.save(buffer, format="JPEG")
    buffer.seek(0)  # rewind
    after_pred = predict_image(buffer)   # <-- re-classify after image
    after_class_name = after_pred["class_name"]

    # Map for human-readable names
    before_class_name = DISTORTION_MAP.get(before_class_name)
    after_class_name = DISTORTION_MAP.get(after_class_name)

    # 5. OCR on AFTER image
    result = run_ocr(enhanced_img)
    if result and result[0]:
        text = result[0][0][1][0]          
        conf_score = f"{result[0][0][1][1] * 100:.2f}"
    else:
        text = ""
        conf_score = "0"

    # 6. Save AFTER image
    buffer.seek(0)
    image_obj.after_image.save(
        f"enhanced_{image_obj.id}.jpg", 
        ContentFile(buffer.getvalue()),
        save=False
    )

    # 7. Save results to DB
    image_obj.plate_no = text
    image_obj.date_deblurred = timezone.now()
    image_obj.distortion_type = before_class_name
    image_obj.status = "Successful" if after_class_name == "Normal" and text != '' else "Failed"
    image_obj.after_distortion_type = after_class_name
    image_obj.conf_score = conf_score
    image_obj.save()

    return JsonResponse({
        "before_distortion": before_class_name,
        "after_distortion": after_class_name,
        "ocr": text,
        "status": image_obj.status
    })


@api_view(["POST"])
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
    image_obj.status = "Successful" if after_class_name == "Normal" and text != '' else "Failed"
    image_obj.save()

    print(f'OCR: {text}, Before distortion: {before_class_name}, After distortion: {after_class_name}, Status: {image_obj.status}')

    return JsonResponse({
        "before_distortion": before_class_name,
        "after_distortion": after_class_name,
        "ocr": text,
        "conf_score": conf_score,
        "status": image_obj.status
    })