from django import forms
from django.contrib.auth import get_user_model
from .models import *

AuthUser = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = AuthUser
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

class EstateForm(forms.ModelForm):
    class Meta:
        model = Estate
        fields = ['name', 'image', 'description', 'location_name', 'exact_address', 'bedrooms', 'bathrooms', 'total_built_area', 'plot_size', 'amenities', 'latitude', 'longitude']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mandate-input', 'placeholder': 'Property name'}),
            'location_name': forms.Select(attrs={'class': 'mandate-input'}),
            'description': forms.Textarea(attrs={'class': 'mandate-input mandate-textarea', 'rows': 5, 'placeholder': 'Describe the property'}),
            'exact_address': forms.TextInput(attrs={'id': 'autocomplete-address', 'class': 'mandate-input', 'placeholder': 'Exact detailed address search'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'mandate-input', 'min': 0, 'placeholder': 'Bedrooms'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'mandate-input', 'min': 0, 'placeholder': 'Bathrooms'}),
            'total_built_area': forms.NumberInput(attrs={'class': 'mandate-input', 'min': 0, 'step': '0.01', 'placeholder': 'Total built area'}),
            'plot_size': forms.NumberInput(attrs={'class': 'mandate-input', 'min': 0, 'step': '0.01', 'placeholder': 'Plot size'}),
            'amenities': forms.HiddenInput(attrs={'id': 'selected-amenities'}),
            'image': forms.ClearableFileInput(attrs={'class': 'mandate-file-input'}),
            'latitude': forms.HiddenInput(attrs={'id': 'property-lat'}),
            'longitude': forms.HiddenInput(attrs={'id': 'property-lng'}),
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name','email','date']

class UpdateLocationForm(forms.Form):
    latitude = forms.DecimalField(max_digits=9, decimal_places=6)
    longitude = forms.DecimalField(max_digits=9, decimal_places=6)

class EditEstateForm(forms.ModelForm):
    class Meta:
        model = Estate
        fields = ['name', 'image', 'description', 'location_name', 'exact_address', 'bedrooms', 'bathrooms', 'total_built_area', 'plot_size', 'amenities', 'latitude', 'longitude']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mandate-input', 'placeholder': 'Property name'}),
            'location_name': forms.Select(attrs={'class': 'mandate-input'}),
            'description': forms.Textarea(attrs={'class': 'mandate-input mandate-textarea', 'rows': 5, 'placeholder': 'Describe the property'}),
            'exact_address': forms.TextInput(attrs={'id': 'autocomplete-address', 'class': 'mandate-input', 'placeholder': 'Exact detailed address search'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'mandate-input', 'min': 0, 'placeholder': 'Bedrooms'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'mandate-input', 'min': 0, 'placeholder': 'Bathrooms'}),
            'total_built_area': forms.NumberInput(attrs={'class': 'mandate-input', 'min': 0, 'step': '0.01', 'placeholder': 'Total built area'}),
            'plot_size': forms.NumberInput(attrs={'class': 'mandate-input', 'min': 0, 'step': '0.01', 'placeholder': 'Plot size'}),
            'amenities': forms.HiddenInput(attrs={'id': 'selected-amenities'}),
            'image': forms.ClearableFileInput(attrs={'class': 'mandate-file-input'}),
            'latitude': forms.HiddenInput(attrs={'id': 'property-lat'}),
            'longitude': forms.HiddenInput(attrs={'id': 'property-lng'}),
        }