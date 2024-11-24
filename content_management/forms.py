# File: content_management/forms.py
# Location: C:\git\_clapri\content_management\forms.py

from django import forms
from .models import Theme

class ThemeForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter theme name'
        })
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter theme description'
        })
    )
    css_variables = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': '{\n    "--primary-color": "#007bff",\n    "--secondary-color": "#6c757d"\n}'
        }),
        help_text="Enter CSS variables in JSON format"
    )

    def clean_css_variables(self):
        data = self.cleaned_data['css_variables']
        if data:
            try:
                import json
                # Try to parse as JSON to validate format
                json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError("Please enter valid JSON format")
        return data

class PageContentForm(forms.Form):
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Content Title'
    }))
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'id': 'content-editor',
        'rows': 15
    }))
    page_type = forms.ChoiceField(choices=[
        ('home', 'Home Page'),
        ('about', 'About Us'),
        ('services', 'Services'),
        ('contact', 'Contact'),
        ('appointments', 'Appointments'),
        ('opening_hours', 'Opening Hours'),
        ('holiday_schedule', 'Holiday Schedule'),
        ('testimonials', 'Testimonials'),
        ('privacy', 'Privacy Policy'),
        ('terms', 'Terms of Service'),
        ('faq', 'FAQ'),
        ('other', 'Other')
    ], widget=forms.Select(attrs={
        'class': 'form-control'
    }))
    theme = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    display_from = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    display_until = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate theme choices
        themes = Theme.objects.all()
        self.fields['theme'].choices = [('', '----')] + [(str(t.id), t.name) for t in themes]