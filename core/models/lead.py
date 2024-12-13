# core/models/lead.py
from mongoengine import Document, StringField, DateTimeField, EmailField
from datetime import datetime

class Lead(Document):
    PROPERTY_TYPES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('land', 'Land/Lot'),
        ('multi_family', 'Multi-Family'),
        ('industrial', 'Industrial'),
        ('other', 'Other')
    ]

    name = StringField(required=True, max_length=100)
    email = EmailField(required=True)
    phone = StringField(max_length=20)
    property_type = StringField(choices=PROPERTY_TYPES)
    message = StringField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'leads',
        'ordering': ['-created_at']
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.email})"