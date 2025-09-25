from django import forms
from .models import Unavailability

class UnavailabilityForm(forms.ModelForm):
    class Meta:
        model = Unavailability
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'start_date': "Дата початку",
            'end_date': "Дата завершення",
            'reason': "Причина (необов'язково)",
        }