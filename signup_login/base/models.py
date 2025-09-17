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
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # link to logged-in user
    class_name = models.CharField(max_length=50)
    no_of_days = models.IntegerField()
    no_of_periods = models.IntegerField()
    start_time = models.TimeField()
    duration_minutes = models.IntegerField()
    no_of_breaks = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)  # timestamp
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.class_name}"


class TimetableSlot(models.Model):
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name="slots")
    day = models.CharField(max_length=15)  # Monday, Tuesday, etc.
    type = models.CharField(max_length=10, choices=[('period', 'Period'), ('break', 'Break')])
    number = models.IntegerField()  # Period number or Break number
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.timetable.class_name} - {self.day} - {self.type} {self.number}"