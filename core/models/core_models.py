# File: core/models.py
# Location: C:\git\_clapri\core\models.py

from mongoengine import Document, StringField, DateTimeField, BooleanField, EmailField, IntField, FloatField, DecimalField, ListField, ReferenceField
from datetime import datetime
from django import forms
# from .models import UserProfile, AppraisalRequest


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

    request_id = StringField(unique=True)  # Auto-generated ID
    user_id = StringField(required=True)  # Auth0 user ID
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
    purpose = StringField(required=False)
    status = StringField(required=True, choices=STATUS_CHOICES, default='pending')

    notes = StringField()
    documents = ListField(StringField())  # URLs to uploaded documents
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    scheduled_date = DateTimeField()
    assigned_appraiser = StringField()
    estimated_value = DecimalField()
    
    meta = {
        'collection': 'appraisal_requests',
        'ordering': ['-created_at'],
        'indexes': [
            'user_id',
            'status',
            'request_id'
        ]
    }

    def save(self, *args, **kwargs):
        if not self.request_id:
            # Generate a unique request ID
            year = str(datetime.now().year)[2:]
            count = AppraisalRequest.objects.count() + 1
            self.request_id = f'APR{year}-{count:04d}'
        self.updated_at = datetime.now()
        return super(AppraisalRequest, self).save(*args, **kwargs)

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
    def full_property_address(self):
        return f"{self.property_address}, {self.property_city}, {self.property_state} {self.property_zip}"


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