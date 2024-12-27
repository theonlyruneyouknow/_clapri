from mongoengine import Document, StringField, DateTimeField, BooleanField, EmailField
from datetime import datetime
from django import forms
from django.utils import timezone

class UserProfile(Document):
    ROLES = (
        ('admin', 'Administrator'),
        ('appraiser', 'Appraiser'),
        ('user', 'Standard User')
    )

    user_id = StringField(required=True, unique=True)
    email = EmailField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    role = StringField(choices=ROLES, default='user')
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
            'email',
            'role',
            [('created_at', -1)]  # Proper index specification for descending sort
        ]
    }

    @property
    def is_admin(self):
        return self.role == 'admin'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
