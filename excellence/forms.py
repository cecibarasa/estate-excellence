from django import forms
from .models import *

class EstateForm(forms.ModelForm):
    class Meta:
        model = Estate
        fields = ['name','location_name',]