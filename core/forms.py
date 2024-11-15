# File: core/forms.py
# Location: C:\git\_clapri\core\forms.py

from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Email'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Phone Number (Optional)'
        })
    )
    service_type = forms.ChoiceField(
        choices=[
            ('', 'Select Service Type'),
            ('residential', 'Residential Appraisal'),
            ('commercial', 'Commercial Appraisal'),
            ('specialized', 'Specialized Services'),
            ('other', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Your Message',
            'rows': 5
        })
    )