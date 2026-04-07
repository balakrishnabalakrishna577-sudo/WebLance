from django import forms
from .models import WebsiteRequest

class WebsiteRequestForm(forms.ModelForm):
    class Meta:
        model = WebsiteRequest
        fields = ['name', 'business_name', 'phone', 'email', 'website_type', 'budget', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name'
            }),
            'business_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Business/Company Name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'website_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'budget': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Project Description',
                'rows': 8
            }),
        }
