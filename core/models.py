# File: core/models.py
# Location: C:\git\_clapri\core\models.py

from mongoengine import Document, StringField, DateTimeField, BooleanField, EmailField
from datetime import datetime

class UserProfile(Document):
    user_id = StringField(required=True, unique=True)  # Auth0 user ID
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