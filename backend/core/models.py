from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.core.exceptions import ValidationError
import secrets
import hashlib

class BaseUserModel(models.Model):
    """Abstract base model for common user fields and session management"""
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Session management fields
    session_key = models.CharField(max_length=255, blank=True, null=True, unique=True)
    session_created = models.DateTimeField(blank=True, null=True)
    last_activity = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['session_key']),
            models.Index(fields=['is_active']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        # Hash password if it's not already hashed
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def create_session(self):
        """Create a new session key and update session timestamps"""
        self.session_key = self._generate_session_key()
        self.session_created = timezone.now()
        self.last_activity = timezone.now()
        self.save(update_fields=['session_key', 'session_created', 'last_activity'])
        return self.session_key
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def clear_session(self):
        """Clear session data"""
        self.session_key = None
        self.session_created = None
        self.last_activity = None
        self.save(update_fields=['session_key', 'session_created', 'last_activity'])
    
    def is_session_expired(self, max_age_seconds=7200):  # 2 hours default
        """Check if session is expired"""
        if not self.last_activity:
            return True
        return (timezone.now() - self.last_activity).seconds > max_age_seconds
    
    def _generate_session_key(self):
        """Generate cryptographically secure session key"""
        random_bytes = secrets.token_bytes(32)
        user_info = f"{self.id}:{self.email}:{timezone.now().isoformat()}"
        combined = random_bytes + user_info.encode('utf-8')
        return hashlib.sha256(combined).hexdigest()

class Admin(BaseUserModel):
    """Admin user model with enhanced security"""
    
    class Meta:
        db_table = 'core_admin'
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'
    
    @classmethod
    def authenticate(cls, email, password):
        """Secure admin authentication"""
        try:
            admin = cls.objects.get(email=email.strip().lower(), is_active=True)
            if admin.check_password(password):
                return admin
        except cls.DoesNotExist:
            # Prevent timing attacks by still running password check
            make_password(password)
        return None

class User(BaseUserModel):
    """Regular user model with role-based access"""
    date_of_birth = models.DateField()
    position = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'core_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    @classmethod
    def authenticate(cls, email, password):
        """Secure user authentication"""
        try:
            user = cls.objects.get(email=email.strip().lower(), is_active=True)
            if user.check_password(password):
                return user
        except cls.DoesNotExist:
            # Prevent timing attacks
            make_password(password)
        return None

class Image(models.Model):
    """Image model with enhanced security and validation"""
    STATUS_CHOICES = [
        ('Successful', 'Successful'),
        ('Failed', 'Failed'),
        ('Processing', 'Processing'),
    ]
    
    DISTORTION_CHOICES = [
        ('Low Quality', 'Low Quality'),
        ('Horizontal Blur', 'Horizontal Blur'),
        ('Vertical Blur', 'Vertical Blur'),
        ('Low Light', 'Low Light'),
        ('Normal', 'Normal'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='images',
        db_index=True
    )
    
    before_image = models.ImageField(
        upload_to='secure_uploads/before/%Y/%m/%d/',
        help_text="Original image before processing"
    )
    
    after_image = models.ImageField(
        upload_to='secure_uploads/after/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text="Processed image after enhancement"
    )
    
    date_deblurred = models.DateTimeField(null=True, blank=True)
    plate_no = models.CharField(max_length=20, null=True, blank=True)
    conf_score = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Processing'
    )
    distortion_type = models.CharField(
        max_length=20,
        choices=DISTORTION_CHOICES,
        null=True,
        blank=True
    )
    after_distortion_type = models.CharField(
        max_length=20,
        choices=DISTORTION_CHOICES,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['date_deblurred']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        plate_display = self.plate_no or "Unknown Plate"
        return f"{plate_display} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Auto-set date_deblurred when status changes to 'Successful'
        if self.status == 'Successful' and not self.date_deblurred:
            self.date_deblurred = timezone.now()
        super().save(*args, **kwargs)
    
    def is_owned_by(self, user):
        """Check if image belongs to specified user"""
        return self.user_id == user.id if user else False