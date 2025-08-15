from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

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
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    before_image = models.ImageField(upload_to='before_images/')
    after_image = models.ImageField(upload_to='after_images/')
    date_deblurred = models.DateTimeField(default=timezone.now)
    plate_no = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    distortion_type = models.CharField(max_length=20, choices=DISTORTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plate_no} - {self.status}"
