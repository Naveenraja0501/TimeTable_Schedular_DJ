# app/models.py 
from django.db import models
#from django.contrib.auth.models import User
from django.db import models


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

    break1_duration = models.IntegerField(null=True, blank=True)
    break2_duration = models.IntegerField(null=True, blank=True)
    break3_duration = models.IntegerField(null=True, blank=True) 

    class Meta:
        unique_together = ['user', 'class_name']  # Prevents duplicate class names per user

class TimetableEntry(models.Model):
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='entries')
    day = models.CharField(max_length=20)  # Monday, Tuesday, etc.
    period_number = models.IntegerField()
    subject = models.CharField(max_length=100, blank=True, null=True)
    teacher = models.CharField(max_length=100, blank=True, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False)

    class Meta:
        unique_together = ['timetable', 'day', 'period_number']
        ordering = ['timetable', 'day', 'period_number']

    def __str__(self):
        return f"{self.day} - Period {self.period_number}: {self.subject or 'BREAK'}"