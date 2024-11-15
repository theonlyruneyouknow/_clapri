# File: profiles/models.py

from mongoengine import Document, StringField, DateTimeField, ReferenceField, BooleanField, EmailField
from datetime import datetime

class Profile(Document):
    user_id = StringField(required=True, unique=True)  # Auth0 user ID
    email = EmailField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    company = StringField(max_length=100)
    phone = StringField(max_length=20)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'profiles',
        'indexes': [
            'user_id',
            'email'
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(Profile, self).save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or "Anonymous"

class Testimonial(Document):
    profile = ReferenceField(Profile, required=True)
    title = StringField(required=True, max_length=200)
    content = StringField(required=True)
    rating = StringField(choices=['1', '2', '3', '4', '5'], required=True)
    approved = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'testimonials',
        'ordering': ['-created_at'],
        'indexes': [
            'profile',
            'approved'
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(Testimonial, self).save(*args, **kwargs)