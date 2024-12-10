# core/models/photo_gallery.py
from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField, URLField
from datetime import datetime

class PhotoGallery(Document):
    appraisal_request = ReferenceField('AppraisalRequest', required=True)
    uploaded_by = ReferenceField('UserProfile', required=True)
    created_at = DateTimeField(default=datetime.now)
    
    # Photo Information
    photos = ListField(URLField())
    photo_descriptions = ListField(StringField(max_length=500))
    
    # Categories
    PHOTO_CATEGORIES = [
        'exterior',
        'interior',
        'roof',
        'foundation',
        'damage',
        'improvements',
        'other'
    ]
    categories = ListField(StringField(choices=PHOTO_CATEGORIES))
    
    # Metadata
    total_photos = StringField()
    primary_photo_url = URLField()
    
    meta = {
        'collection': 'photo_galleries',
        'indexes': [
            'appraisal_request',
            'uploaded_by',
            'created_at'
        ]
    }

    def add_photo(self, url, description, category):
        self.photos.append(url)
        self.photo_descriptions.append(description)
        if category not in self.categories:
            self.categories.append(category)
        self.total_photos = str(len(self.photos))
        self.save()

    def remove_photo(self, url):
        if url in self.photos:
            index = self.photos.index(url)
            self.photos.pop(index)
            self.photo_descriptions.pop(index)
            self.total_photos = str(len(self.photos))
            self.save()