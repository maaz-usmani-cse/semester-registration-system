
# Create your models here.
from django.db import models
from django.utils import timezone
from datetime import timedelta

class UserProfile(models.Model):
    # Core User Details (Naye signup form se completely mapped)
    full_name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True, default='') 
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, default='') # Form ke name="mobile" se exact match
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    # Secure Password Space: Isme 'make_password' se secure hash ho kar password save hoga
    password = models.CharField(max_length=255) 
    
    # Pro Max OTP Security System
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False) # OTP status checker flag

    # Heavy Logic Engine: Exact 5 Minutes Expiry Validation Control
    def is_otp_valid(self):
        if self.otp_created_at:
            return timezone.now() < self.otp_created_at + timedelta(minutes=5)
        return False

    def __str__(self):
        return f"{self.full_name} (@{self.username})"

    class Meta:
        verbose_name_plural = "User Profiles"