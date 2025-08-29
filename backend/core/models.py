from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.core.exceptions import ValidationError

# --- Admin Table ---
class Admin(models.Model):
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    # Automatically hash password before saving
    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    # Check password helper
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

# --- Users Table ---
class User(models.Model):
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    position = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    # Automatically hash password before saving
    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    # Check password helper
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

# --- Images Table ---
class Image(models.Model):
    STATUS_CHOICES = [
        ('Successful', 'Successful'),
        ('Failed', 'Failed'),
    ]
    
    DISTORTION_CHOICES = [
        ('Low Quality', 'Low Quality'),
        ('Horizontal Blur', 'Horizontal Blur'),
        ('Vertical Blur', 'Vertical Blur'),
        ('Low Light', 'Low Light'),
        ('Normal', 'Normal'),
    ]
    
    # User reference 
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='images',
        null=False,
        blank=False,
        help_text="User who uploaded this image. Can be null for anonymous uploads."
    )
    
    # Before image - REQUIRED field 
    before_image = models.ImageField(
        upload_to='before_images/',
        help_text="Original image before processing. This field is required."
    )
    
    # After image - nullable (processing might not be completed yet)
    after_image = models.ImageField(
        upload_to='after_images/',
        null=True,
        blank=True,
        help_text="Processed image after deblurring. Can be null if processing is incomplete."
    )
    
    # Date deblurred - nullable (processing might not be completed)
    date_deblurred = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the image was successfully deblurred. Null if not processed yet."
    )
    
    # Plate number - nullable (might not be detected or extracted yet)
    plate_no = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="License plate number extracted from the image. Can be null if not detected."
    )

    # Confidence score - nullable (might not be detected or extracted yet)
    conf_score = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Confidence score for the detected license plate number. Can be null if not detected."
    )
    
    # Status - nullable with default handling in business logic
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        null=True,
        blank=True,
        help_text="Processing status. Can be null for pending/in-progress items."
    )
    
    # Distortion type - nullable (might be determined during processing)
    distortion_type = models.CharField(
        max_length=20,
        choices=DISTORTION_CHOICES,
        null=True,
        blank=True,
        help_text="Type of distortion detected in the image. Can be null if not analyzed yet."
    )

    # After Distortion type - nullable (might be determined during processing)
    after_distortion_type = models.CharField(
        max_length=20,
        choices=DISTORTION_CHOICES,
        null=True,
        blank=True,
        help_text="Type of distortion detected in the image. Can be null if not analyzed yet."
    )
    
    # Creation timestamp - always set automatically
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Add database indexes for better query performance
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['date_deblurred']),
        ]
        # Add ordering for consistent results
        ordering = ['-created_at']
    
    def __str__(self):
        # Handle nullable plate_no and status gracefully
        plate_display = self.plate_no if self.plate_no else "Unknown Plate"
        status_display = self.status if self.status else "Pending"
        return f"{plate_display} - {status_display}"
    
    def clean(self):
        """
        Custom validation method for business logic validation.
        Called during model validation (e.g., in Django admin or when using full_clean()).
        """
        super().clean()
        
        # Validate that before_image is always provided
        if not self.before_image:
            raise ValidationError({
                'before_image': 'Before image is required and cannot be empty.'
            })
        
        # Business logic: if status is 'Successful', date_deblurred should be set
        if self.status == 'Successful' and not self.date_deblurred:
            raise ValidationError({
                'date_deblurred': 'Date deblurred must be set when status is Successful.'
            })
        
        # Business logic: if date_deblurred is set, status should not be null
        if self.date_deblurred and not self.status:
            raise ValidationError({
                'status': 'Status must be set when date_deblurred is provided.'
            })
    
    def save(self, *args, **kwargs):
        """
        Override save method to handle business logic and set defaults.
        """
        try:
            # Run validation before saving
            self.full_clean()
            
            # Auto-set date_deblurred when status changes to 'Successful'
            if self.status == 'Successful' and not self.date_deblurred:
                self.date_deblurred = timezone.now()
            
            # Performance optimization: only call super().save() once
            super().save(*args, **kwargs)
            
        except ValidationError as e:
            # Re-raise validation errors with context
            raise ValidationError(f"Image validation failed: {e}")
        except Exception as e:
            # Handle unexpected errors gracefully
            raise Exception(f"Error saving Image model: {str(e)}")
    

    def is_processing_complete(self):
        """
        Helper method to check if image processing is complete.
        Returns True if processing is done (successful or failed).
        """
        return self.status in ['Successful', 'Failed']
    
    def get_processing_status_display(self):
        """
        Helper method to get user-friendly status display.
        Handles nullable status gracefully.
        """
        if not self.status:
            return "Processing"
        return self.get_status_display()
    
    def has_valid_plate_number(self):
        """
        Helper method to check if a valid plate number is detected.
        """
        return bool(self.plate_no and self.plate_no.strip())
    
    @classmethod
    def get_pending_images(cls):
        """
        Class method to get all images that are pending processing.
        Useful for background processing tasks.
        """
        return cls.objects.filter(
            models.Q(status__isnull=True) | models.Q(status='')
        )
    
    @classmethod
    def get_successful_images_by_user(cls, user):
        """
        Class method to get successfully processed images for a specific user.
        Handles nullable user field gracefully.
        """
        if not user:
            return cls.objects.none()
        
        return cls.objects.filter(
            user=user,
            status='Successful'
        ).order_by('-date_deblurred')
    
