# File: leads/forms.py
# Location: C:\git\_clapri\leads\forms.py

from django import forms
from .models import Lead

class LeadForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )
    company = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company Name (if applicable)'
        })
    )
    property_type = forms.ChoiceField(
        choices=Lead.PROPERTY_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    property_address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Property Address'
        })
    )
    source = forms.ChoiceField(
        choices=Lead.SOURCE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional Notes'
        })
    )

class LeadNoteForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter your note here...'
        })
    )

class LeadSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search leads...'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + list(Lead.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    source = forms.ChoiceField(
        choices=[('', 'All Sources')] + list(Lead.SOURCE_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )