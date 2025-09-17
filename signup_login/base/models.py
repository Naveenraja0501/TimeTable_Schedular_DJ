# app/models.py
from django.db import models
#from django.contrib.auth.models import User
class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=255)  # hashed password

    def __str__(self):
        return self.email

class Timetable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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


    #def __str__(self):
        #return f"{self.user.username} - {self.class_name}"


