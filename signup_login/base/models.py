# app/models.py 
from django.db import models
#from django.contrib.auth.models import User

# models.py
#from django.contrib.auth.models import AbstractUser
from django.db import models
"""
class User(AbstractUser):
    # Remove the 'password' field since AbstractUser already has it
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    
    # Remove the password field - AbstractUser already has it properly implemented
    # password field is already handled by AbstractUser with proper hashing
    
    # Required: specify custom fields for authentication
    USERNAME_FIELD = 'email'  # Use email as login identifier
    REQUIRED_FIELDS = ['username', 'name']  # Fields required when creating user

    def __str__(self):
        return self.email
"""

from django.db import models

class User(models.Model):
    user_id = models.AutoField(primary_key=True)  # Auto-incrementing user_id starting from 1
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=255)  # hashed password

    def __str__(self):
        return self.email

class Timetable(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        to_field='user_id'  # Reference the user_id field instead of the default id
    )
    class_name = models.CharField(max_length=50)
    no_of_days = models.IntegerField()
    no_of_periods = models.IntegerField()
    start_time = models.TimeField()
    duration_minutes = models.IntegerField()
    no_of_breaks = models.IntegerField()
    
    # Individual break fields
    break1_after_period = models.IntegerField(null=True, blank=True)
    break2_after_period = models.IntegerField(null=True, blank=True)
    break3_after_period = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'class_name']  # Prevents duplicate class names per user

