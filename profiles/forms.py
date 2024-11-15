# File: profiles/forms.py

from django import forms

class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name'
    }))
    company = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Company Name'
    }))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone Number'
    }))

class TestimonialForm(forms.Form):
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Title of your testimonial'
    }))
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 5,
        'placeholder': 'Share your experience...'
    }))
    rating = forms.ChoiceField(choices=[
        ('5', '★★★★★ Excellent'),
        ('4', '★★★★☆ Very Good'),
        ('3', '★★★☆☆ Good'),
        ('2', '★★☆☆☆ Fair'),
        ('1', '★☆☆☆☆ Poor')
    ], widget=forms.Select(attrs={
        'class': 'form-control'
    }))