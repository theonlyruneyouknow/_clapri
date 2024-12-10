from mongoengine import Document, ReferenceField, DateTimeField, StringField, BooleanField, IntField, FloatField, ListField, DecimalField
from datetime import datetime
from django.utils import timezone

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

    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)  # Use timezone.now instead of datetime.now
    notes = StringField()
    documents = ListField(StringField())  # URLs to uploaded documents
    
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
