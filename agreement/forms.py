from django import forms
from .models import Agreement


class AgreementForm(forms.ModelForm):
    class Meta:
        model  = Agreement
        fields = [
            'client_name', 'company_name', 'client_email', 'client_phone',
            'client_address', 'project_type', 'project_title', 'description',
            'start_date', 'end_date', 'total_cost', 'advance_percent',
            'payment_terms', 'additional_terms',
        ]
        widgets = {
            'client_name':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'company_name':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company / Business name'}),
            'client_email':    forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'client@email.com'}),
            'client_phone':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 XXXXX XXXXX'}),
            'client_address':  forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full address'}),
            'project_type':    forms.Select(attrs={'class': 'form-select'}),
            'project_title':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Business Website for ABC Corp'}),
            'description':     forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed project scope...'}),
            'start_date':      forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date':        forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_cost':      forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '25000'}),
            'advance_percent': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'payment_terms':   forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'e.g. 50% advance, 50% on delivery...'}),
            'additional_terms':forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Any additional clauses...'}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end   = cleaned.get('end_date')
        if start and end and end <= start:
            raise forms.ValidationError('End date must be after start date.')
        return cleaned
