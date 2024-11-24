# File: content_management/models.py
# Location: C:\git\_clapri\content_management\models.py

from mongoengine import Document, StringField, DateTimeField, BooleanField, ReferenceField
from datetime import datetime

class Theme(Document):
    name = StringField(required=True, unique=True)
    description = StringField()
    created_at = DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'themes',
        'ordering': ['-created_at']
    }

    def __str__(self):
        return self.name

class PageContent(Document):
    title = StringField(required=True)
    content = StringField(required=True)
    page_type = StringField(required=True, choices=['home', 'about', 'services'])
    theme = ReferenceField(Theme, required=False)  # Make theme optional
    active = BooleanField(default=False)
    display_from = DateTimeField()
    display_until = DateTimeField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    archived = BooleanField(default=False)
    
    meta = {
        'collection': 'page_contents',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['page_type', 'active', 'display_from', 'display_until']}
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(PageContent, self).save(*args, **kwargs)