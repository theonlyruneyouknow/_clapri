# File: core/forms.py
# Location: C:\git\_clapri\core\forms.py

from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from .models import AppraisalRequest

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
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Street Address'
        })
    )
    property_city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    property_state = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State'
        })
    )
    property_zip = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ZIP Code'
        })
    )
    property_type = forms.ChoiceField(
        choices=AppraisalRequest.PROPERTY_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    square_footage = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Square Footage'
        })
    )
    year_built = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Year Built'
        })
    )
    bedrooms = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of Bedrooms'
        })
    )
    bathrooms = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.5',
            'placeholder': 'Number of Bathrooms'
        })
    )
    lot_size = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Lot Size (e.g., 0.25 acres)'
        })
    )
    purpose = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Purpose of Appraisal'
        })
    )
    preferred_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    alternate_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
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