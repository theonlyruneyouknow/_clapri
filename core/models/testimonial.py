from mongoengine import Document, StringField, DateTimeField, BooleanField, EmailField, IntField, FloatField, DecimalField, ListField, ReferenceField
from datetime import datetime
from django import forms
from django.utils import timezone

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