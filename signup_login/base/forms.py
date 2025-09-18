# app/forms.py
from django import forms
from .models import Timetable

class TimetableForm(forms.ModelForm):
    pass

    class Meta:
        model = Timetable
        fields = ['class_name', 'no_of_days', 'no_of_periods', 'start_time', 'duration_minutes', 'no_of_breaks']
