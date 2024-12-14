# File: core/models.py
# Location: C:\git\_clapri\core\models.py

from mongoengine import Document, StringField, DateTimeField, BooleanField, EmailField, IntField, FloatField, DecimalField, ListField, ReferenceField, DateField
from datetime import datetime
from django import forms
from django.utils import timezone
# from .models import UserProfile, AppraisalRequest

class TimeSlot(Document):
    SLOT_CHOICES = [
        ('morning', '8:00 AM - 11:00 AM'),
        ('afternoon1', '12:00 PM - 3:00 PM'),
        ('afternoon2', '3:00 PM - 6:00 PM')
    ]

    date = DateField(required=True)
    slot = StringField(required=False, choices=SLOT_CHOICES)
    is_available = BooleanField(default=True)
    appraisal_request = ReferenceField('AppraisalRequest')
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'time_slots',
        'indexes': [
            {'fields': ['date', 'slot'], 'unique': True},
            'is_available'
        ]
    }

    @classmethod
    def get_available_slots(cls, start_date, end_date):
        return cls.objects(
            date__gte=start_date,
            date__lte=end_date,
            is_available=True
        ).order_by('date', 'slot')




class Appointment(Document):
    appraisal_request = ReferenceField('AppraisalRequest', required=True)
    scheduled_date = DateTimeField(required=True)
    status = StringField(choices=['scheduled', 'completed', 'cancelled', 'rescheduled'], default='scheduled')
    notes = StringField()
    confirmation_sent = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'appointments',
        'ordering': ['-scheduled_date'],
        'indexes': [
            'appraisal_request',
            'scheduled_date',
            'status'
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(Appointment, self).save(*args, **kwargs)

    def reschedule(self, new_date):
        old_date = self.scheduled_date
        self.scheduled_date = new_date
        self.status = 'rescheduled'
        self.save()
        return old_date

class UserProfile(Document):
    user_id = StringField(required=True, unique=True)
    email = EmailField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    phone = StringField(max_length=20)
    company = StringField(max_length=100)
    address = StringField(max_length=200)
    city = StringField(max_length=100)
    state = StringField(max_length=50)
    zip_code = StringField(max_length=10)
    is_verified = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'user_profiles',
        'indexes': [
            'user_id',
            'email'
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(UserProfile, self).save(*args, **kwargs)

    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return "Anonymous"

    @property
    def full_address(self):
        address_parts = [
            self.address,
            self.city,
            self.state,
            self.zip_code
        ]
        return ', '.join(filter(None, address_parts))

class AppraisalRequest(Document):
    PROPERTY_TYPES = (
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('land', 'Land'),
        ('industrial', 'Industrial')
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('reviewing', 'Under Review'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )

    request_id = StringField(unique=True)
    user_id = StringField(required=True)
    property_address = StringField(required=True, max_length=200)
    property_city = StringField(required=True, max_length=100)
    property_state = StringField(required=True, max_length=50)
    property_zip = StringField(required=True, max_length=10)
    property_type = StringField(required=True, choices=PROPERTY_TYPES)
    square_footage = IntField(required=True)
    year_built = IntField()
    bedrooms = IntField()
    bathrooms = FloatField()
    lot_size = StringField()
    purpose = StringField(required=True)
    status = StringField(required=True, choices=STATUS_CHOICES, default='pending')
    preferred_date = DateTimeField()
    alternate_date = DateTimeField()
    notes = StringField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    scheduled_date = DateTimeField()
    assigned_appraiser = StringField()
    
    meta = {
        'collection': 'appraisal_requests',
        'ordering': ['-created_at']
    }

    @property
    def status_color(self):
        return {
            'pending': 'warning',
            'scheduled': 'info',
            'in_progress': 'primary',
            'reviewing': 'secondary',
            'completed': 'success',
            'cancelled': 'danger'
        }.get(self.status, 'secondary')
    
    @property
    def formatted_address(self):
        """Returns a nicely formatted full address"""
        return f"{self.property_address}, {self.property_city}, {self.property_state} {self.property_zip}"
    
    @property
    def property_type_display(self):
        """Returns the display name for the property type"""
        return dict(self.PROPERTY_TYPES).get(self.property_type, self.property_type)
    
    @property
    def status_display(self):
        """Returns the display name for the status"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

class Testimonial(Document):
    user_id = StringField(required=True)  # Auth0 user ID
    author_name = StringField(required=True)
    author_company = StringField()
    title = StringField(required=True)
    content = StringField(required=True)
    rating = IntField(min_value=1, max_value=5, required=True)
    is_approved = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'testimonials',
        'ordering': ['-created_at'],
        'indexes': [
            'user_id',
            'is_approved'
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(Testimonial, self).save(*args, **kwargs)

    @property
    def rating_stars(self):
        return '★' * self.rating + '☆' * (5 - self.rating)

class Lead(Document):
    """Model for tracking business leads"""
    
    PROPERTY_TYPES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('land', 'Land/Lot'),
        ('multi_family', 'Multi-Family'),
        ('industrial', 'Industrial'),
        ('other', 'Other')
    ]

    # Basic Information
    name = StringField(required=True)  # Keep this for backwards compatibility
    email = EmailField(required=True)
    phone = StringField(max_length=20)
    property_type = StringField(choices=PROPERTY_TYPES)
    message = StringField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'leads',
        'ordering': ['-created_at']
    }

    def get_full_name(self):
        return self.name