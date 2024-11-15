# File: content_management/forms.py

from django import forms
from .models import PageContent, Theme

class ThemeForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 3
    }))

class PageContentForm(forms.Form):
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 10,
        'id': 'content-editor'
    }))
    page_type = forms.ChoiceField(choices=[
        ('home', 'Home'),
        ('about', 'About'),
        ('services', 'Services')
    ], widget=forms.Select(attrs={
        'class': 'form-control'
    }))
    theme = forms.ChoiceField(required=False, widget=forms.Select(attrs={
        'class': 'form-control'
    }))
    active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input'
    }))
    display_from = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={
        'class': 'form-control',
        'type': 'datetime-local'
    }))
    display_until = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={
        'class': 'form-control',
        'type': 'datetime-local'
    }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate theme choices
        themes = Theme.objects.all()
        self.fields['theme'].choices = [('', '----')] + [(str(t.id), t.name) for t in themes]