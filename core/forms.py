# File: core/forms.py
# Location: C:\git\_clapri\core\forms.py
from mongoengine import Document, StringField, DateTimeField, EmailField, ListField, ReferenceField
from mongoengine import BooleanField, IntField, DictField
from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
import pytz
from .models import AppraisalRequest, TimeSlot, Lead
from django import forms
from .models import Lead

class Lead(Document):
    """Model for tracking business leads and their interactions"""
    
    PROPERTY_TYPES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('land', 'Land/Lot'),
        ('multi_family', 'Multi-Family'),
        ('industrial', 'Industrial'),
        ('other', 'Other')
    ]

    # Basic Information
    first_name = StringField(required=True, max_length=50)
    last_name = StringField(required=True, max_length=50)
    email = EmailField(required=True)
    phone = StringField(max_length=20)
    property_type = StringField(choices=PROPERTY_TYPES)
    message = StringField()  # For additional notes
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'leads',
        'ordering': ['-created_at']
    }

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
class ScheduleSelectionForm(forms.Form):
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'max': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        })
    )
    
    time_slot = forms.ChoiceField(
        choices=TimeSlot.SLOT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    def clean_appointment_date(self):
        date = self.cleaned_data['appointment_date']
        if date < datetime.now().date() + timedelta(days=1):
            raise forms.ValidationError("Please select a date at least 1 day in advance")
        if date > datetime.now().date() + timedelta(days=90):
            raise forms.ValidationError("Please select a date within 90 days")
        if date.weekday() >= 5:  # Weekend
            raise forms.ValidationError("Please select a weekday (Monday-Friday)")
        return date


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
            ('estate', 'Estate Valuation'),
            ('tax', 'Tax Assessment'),
            ('consulting', 'Consulting Services'),
            ('other', 'Other Services')
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

class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name'
    }))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone Number'
    }))
    company = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Company Name'
    }))
    address = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Street Address'
    }))
    city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'City'
    }))
    state = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'State'
    }))
    zip_code = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'ZIP Code'
    }))

class AppraisalRequestForm(forms.Form):
    property_address = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    property_city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    property_state = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    property_zip = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    property_type = forms.ChoiceField(
        choices=[
            ('residential', 'Residential'),
            ('commercial', 'Commercial'),
            ('land', 'Land'),
            ('multi_family', 'Multi-Family')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    square_footage = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    year_built = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    bedrooms = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    bathrooms = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'})
    )
    lot_size = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    purpose = forms.CharField(  # Make sure this field exists and is required
        required=False,  # Explicitly mark as required
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Please describe the purpose of this appraisal'
        })
    )
    appointment_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    time_slot = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Select a time slot'),
            ('morning', 'Morning: 8:00 AM - 11:00 AM'),
            ('afternoon1', 'Early Afternoon: 12:00 PM - 3:00 PM'),
            ('afternoon2', 'Late Afternoon: 3:00 PM - 6:00 PM')
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter any special requirements or preferred times if the available slots don\'t work for you.'
        })
    )

    
    




    purpose = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        })
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        })
    )
    def clean_appointment_date(self):
        date = self.cleaned_data.get('appointment_date')
        if date:
            if date < datetime.now().date() + timedelta(days=1):
                raise forms.ValidationError("Please select a date at least 1 day in advance")
            if date > datetime.now().date() + timedelta(days=90):
                raise forms.ValidationError("Please select a date within 90 days")
            if date.weekday() >= 5:  # Weekend
                raise forms.ValidationError("Please select a weekday (Monday-Friday)")
        return date

class TestimonialForm(forms.Form):
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Title for your testimonial'
        })
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Share your experience with our service'
        })
    )
    rating = forms.ChoiceField(
        choices=[
            (5, '⭐⭐⭐⭐⭐ Excellent'),
            (4, '⭐⭐⭐⭐☆ Very Good'),
            (3, '⭐⭐⭐☆☆ Good'),
            (2, '⭐⭐☆☆☆ Fair'),
            (1, '⭐☆☆☆☆ Poor')
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    company = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Company (Optional)'
        })
    )

# class AppointmentScheduleForm(forms.Form):
#     date = forms.DateTimeField(
#         widget=forms.DateTimeInput(attrs={
#             'class': 'form-control',
#             'type': 'datetime-local'
#         }),
#         help_text="Select your preferred appointment date and time"
#     )
#     notes = forms.CharField(
#         required=False,
#         widget=forms.Textarea(attrs={
#             'class': 'form-control',
#             'rows': 3,
#             'placeholder': 'Any special instructions or notes'
#         })
#     )

#     def clean_date(self):
#         date = self.cleaned_data['date']
#         now = datetime.now()
#         min_date = now + timedelta(days=1)
#         max_date = now + timedelta(days=90)

#         if date < min_date:
#             raise forms.ValidationError("Appointments must be scheduled at least 24 hours in advance")
#         if date > max_date:
#             raise forms.ValidationError("Appointments cannot be scheduled more than 90 days in advance")
#         return date


class AppointmentScheduleForm(forms.Form):
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        help_text="Select your preferred appointment date and time"
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any special instructions or notes'
        })
    )

    def clean_date(self):
        date = self.cleaned_data['date']
        
        # Convert to timezone-aware datetime
        if timezone.is_naive(date):
            date = timezone.make_aware(date)
            
        now = timezone.now()
        min_date = now + timedelta(days=1)
        max_date = now + timedelta(days=90)

        if date < min_date:
            raise forms.ValidationError("Appointments must be scheduled at least 24 hours in advance")
        if date > max_date:
            raise forms.ValidationError("Appointments cannot be scheduled more than 90 days in advance")
            
        # Ensure appointment is during business hours (9 AM to 5 PM)
        if date.hour < 9 or date.hour >= 17:
            raise forms.ValidationError("Appointments must be scheduled between 9 AM and 5 PM")
            
        # Check if it's a weekend
        if date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            raise forms.ValidationError("Appointments cannot be scheduled on weekends")

        return date

class LeadForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    property_type = forms.ChoiceField(
        choices=Lead.PROPERTY_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )