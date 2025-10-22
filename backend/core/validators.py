# core/validators.py

from django.core.exceptions import ValidationError
from PIL import Image
import io

MAX_IMAGE_MB = 5

def validate_image_content(image):
    """
    Validate uploaded image without requiring libmagic.
    Uses PIL/Pillow to verify it's a valid image.
    """
    # Check file size
    max_size = MAX_IMAGE_MB * 1024 * 1024
    if image.size > max_size:
        raise ValidationError(f'Image size must be under {MAX_IMAGE_MB}MB')
    
    # Check file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG', '.WEBP']
    file_ext = image.name.lower().split('.')[-1] if '.' in image.name else ''
    if f'.{file_ext}' not in allowed_extensions:
        raise ValidationError('Only jpg, png, and webp images are allowed')
    
    try:
        # Try to open and verify it's a valid image using PIL
        img = Image.open(image)
        img.verify()  # Verify it's actually an image
        
        # Reset file pointer after verify
        image.seek(0)
        
        # Re-open to check format (verify() closes the file)
        img = Image.open(image)
        
        # Check image format
        if img.format not in ['.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG', '.WEBP']:
            raise ValidationError('Invalid image format. Only jpg, png, and webp are supported')
        
        # Optional: Check dimensions (prevent extremely large images)
        width, height = img.size
        max_dimension = 10000  # 10k pixels max per side
        if width > max_dimension or height > max_dimension:
            raise ValidationError(f'Image dimensions too large. Max {max_dimension}x{max_dimension} pixels')
        
        # Reset file pointer for Django to read
        image.seek(0)
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f'Invalid or corrupted image file: {str(e)}')
    
    return image


def validate_password_strength(password):
    """
    Validate password meets security requirements.
    """
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')
    
    if not any(c.isupper() for c in password):
        raise ValidationError('Password must contain at least one uppercase letter')
    
    if not any(c.islower() for c in password):
        raise ValidationError('Password must contain at least one lowercase letter')
    
    if not any(c.isdigit() for c in password):
        raise ValidationError('Password must contain at least one number')
    
    return password