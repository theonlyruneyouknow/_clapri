# File: leads/models.py
# Location: C:\git\_clapri\leads\models.py

from mongoengine import Document, StringField, DateTimeField, EmailField, ListField, ReferenceField
from mongoengine import BooleanField, IntField, DictField
from datetime import datetime

class Lead(Document):
    """Model for tracking business leads and their interactions"""
    
    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('proposal', 'Proposal Sent'),
        ('negotiating', 'Negotiating'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('inactive', 'Inactive')
    )

    SOURCE_CHOICES = (
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('direct', 'Direct Contact'),
        ('social', 'Social Media'),
        ('advertisement', 'Advertisement'),
        ('other', 'Other')
    )

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
    company = StringField(max_length=100)
    email = EmailField(required=True)
    phone = StringField(max_length=20)
    
    # Additional Contact Information
    alternate_phone = StringField(max_length=20)
    address = StringField(max_length=200)
    city = StringField(max_length=100)
    state = StringField(max_length=50)
    zip_code = StringField(max_length=10)
    
    # Lead Details
    status = StringField(choices=STATUS_CHOICES, default='new')
    source = StringField(choices=SOURCE_CHOICES)
    assigned_to = ReferenceField('UserProfile')  # Reference to the user handling this lead
    priority = IntField(min_value=1, max_value=5, default=3)  # 1=Lowest, 5=Highest
    
    # Timeline
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    last_contacted = DateTimeField()
    next_follow_up = DateTimeField()
    
    # Lead Properties
    property_type = StringField(choices=PROPERTY_TYPES)
    property_address = StringField()
    property_details = DictField()  # Flexible field for additional property information
    
    # Communication Preferences
    preferred_contact_method = StringField(choices=['email', 'phone', 'text'], default='email')
    best_time_to_contact = StringField()
    do_not_contact = BooleanField(default=False)
    
    # Tags for categorization
    tags = ListField(StringField(max_length=50))
    
    # Notes and custom fields
    notes = ListField(DictField())  # List of dictionaries containing notes with timestamps
    custom_fields = DictField()  # Flexible field for additional custom information

    meta = {
        'collection': 'leads',
        'ordering': ['-created_at'],
        'indexes': [
            'email',
            'status',
            'assigned_to',
            'created_at',
            'next_follow_up'
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(Lead, self).save(*args, **kwargs)

    def add_note(self, content: str, author: str):
        """Add a new note to the lead"""
        note = {
            'content': content,
            'author': author,
            'timestamp': datetime.now()
        }
        self.notes.append(note)
        self.save()

    def get_full_name(self) -> str:
        """Return the lead's full name"""
        return f"{self.first_name} {self.last_name}"

    @property
    def full_address(self) -> str:
        """Return the formatted full address"""
        address_parts = [
            self.address,
            self.city,
            self.state,
            self.zip_code
        ]
        return ', '.join(filter(None, address_parts))

class LeadInteraction(Document):
    """Model for tracking all interactions with a lead"""
    
    INTERACTION_TYPES = (
        ('email', 'Email'),
        ('phone', 'Phone Call'),
        ('meeting', 'Meeting'),
        ('note', 'Note'),
        ('document', 'Document'),
        ('proposal', 'Proposal'),
        ('other', 'Other')
    )

    lead = ReferenceField(Lead, required=True)
    type = StringField(choices=INTERACTION_TYPES, required=True)
    timestamp = DateTimeField(default=datetime.now)
    content = StringField(required=True)
    author = ReferenceField('UserProfile', required=True)
    
    # For email interactions
    email_subject = StringField()
    email_to = EmailField()
    email_from = EmailField()
    email_thread_id = StringField()
    
    # For document interactions
    document_url = StringField()
    document_type = StringField()
    
    # For tracking
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'lead_interactions',
        'ordering': ['-timestamp'],
        'indexes': [
            'lead',
            'type',
            'timestamp',
            'email_thread_id'
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        # Update the lead's last_contacted field
        if self.type in ['email', 'phone', 'meeting']:
            self.lead.last_contacted = self.timestamp
            self.lead.save()
        return super(LeadInteraction, self).save(*args, **kwargs)