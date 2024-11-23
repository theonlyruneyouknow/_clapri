# File: content_management/models.py

from mongoengine import Document, StringField, DateTimeField, BooleanField, ListField, ReferenceField
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
    theme = ReferenceField(Theme)
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

    def clean(self):
        self.updated_at = datetime.now()
        
    def is_visible(self):
        now = datetime.now()
        if not self.active or self.archived:
            return False
        if self.display_from and self.display_from > now:
            return False
        if self.display_until and self.display_until < now:
            return False
        return True

    def duplicate(self):
        new_content = PageContent(
            title=f"Copy of {self.title}",
            content=self.content,
            page_type=self.page_type,
            theme=self.theme,
            active=False,  # Set inactive by default
            display_from=self.display_from,
            display_until=self.display_until
        )
        new_content.save()
        return new_content