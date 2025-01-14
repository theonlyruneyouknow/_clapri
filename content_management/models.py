# File: content_management/models.py
# Location: C:\git\_clapri\content_management\models.py

from mongoengine import Document, StringField, DateTimeField, ReferenceField, BooleanField
from datetime import datetime



class Theme(Document):
    name = StringField(required=True, unique=True)
    description = StringField()
    css_variables = StringField()  # Store custom CSS variables as JSON
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'themes',
        'ordering': ['-created_at']
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(Theme, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class PageContent(Document):
    title = StringField(required=True)
    content = StringField(required=True)
    page_type = StringField(required=True, choices=[
        'home', 'about', 'services', 'contact', 
        'appointments', 'opening_hours', 'holiday_schedule',
        'testimonials', 'privacy', 'terms', 'faq', 'other'
    ])
    theme = ReferenceField('Theme')
    active = BooleanField(default=False)
    display_from = DateTimeField(required=False)
    display_until = DateTimeField(required=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    archived = BooleanField(default=False)
    
    meta = {
        'collection': 'page_contents',
        'ordering': ['-created_at'],
        'indexes': [
            'page_type',
            ('page_type', 'active', 'archived'),
            ('page_type', 'active', 'archived', 'display_from', 'display_until')
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(PageContent, self).save(*args, **kwargs)

    def is_visible(self) -> bool:
        """
        Determine if the content should be visible based on its status and display dates.
        Returns True if:
        1. Content is active and not archived
        2. Either no display dates are set (meaning always visible)
        3. Or current time falls within the display date range
        """
        now = datetime.now()

        # First check if content is active and not archived
        if not self.active or self.archived:
            return False

        # If no display dates are set, content is visible
        if not self.display_from and not self.display_until:
            return True

        # Check display_from if set
        if self.display_from and self.display_from > now:
            return False

        # Check display_until if set
        if self.display_until and self.display_until < now:
            return False

        return True

    @classmethod
    def get_visible_content(cls, page_type: str):
        """
        Get the currently visible content for a specific page type.
        This method handles all visibility logic in one place.
        """
        now = datetime.now()
        
        # Base query for active, non-archived content of the specified type
        base_query = {
            'page_type': page_type,
            'active': True,
            'archived': False
        }
        
        # Query for content with no display dates OR within display date range
        return cls.objects(__raw__={
            **base_query,
            '$or': [
                # No display dates set
                {
                    'display_from': None,
                    'display_until': None
                },
                # Within display date range
                {
                    '$or': [
                        {'display_from': None},
                        {'display_from': {'$lte': now}}
                    ],
                    '$or': [
                        {'display_until': None},
                        {'display_until': {'$gt': now}}
                    ]
                }
            ]
        }).order_by('-created_at')

    def duplicate(self):
        """Create a copy of the current content"""
        new_content = PageContent(
            title=f"Copy of {self.title}",
            content=self.content,
            page_type=self.page_type,
            theme=self.theme,
            active=False  # Set inactive by default
        )
        new_content.save()
        return new_content