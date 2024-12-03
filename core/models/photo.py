from mongoengine import Document, EmbeddedDocument, StringField, DateTimeField, IntField, \
    BooleanField, ListField, EmbeddedDocumentField, ReferenceField, URLField, DictField
from datetime import datetime

class PropertyPhoto(EmbeddedDocument):
    """Individual property photo with metadata"""
    photo_url = URLField(required=True)
    photo_type = StringField(required=True, choices=[
        'exterior_front', 'exterior_rear', 'exterior_side',
        'interior_room', 'street_scene', 'view', 'defect', 'comparable'
    ])
    location = StringField()  # Room or exterior location
    description = StringField()
    is_primary = BooleanField(default=False)
    taken_at = DateTimeField()
    coordinates = DictField()  # For GPS coordinates if available
    tags = ListField(StringField())

class PhotoGallery(Document):
    """Photo collection for an appraisal"""
    appraisal_report = ReferenceField('AppraisalReport', required=True)
    photos = ListField(EmbeddedDocumentField(PropertyPhoto))
    upload_complete = BooleanField(default=False)
    total_photos = IntField(default=0)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'photo_galleries',
        'ordering': ['-created_at']
    }

    def save(self, *args, **kwargs):
        self.total_photos = len(self.photos)
        self.updated_at = datetime.now()
        return super(PhotoGallery, self).save(*args, **kwargs)

    def add_photo(self, photo_data):
        """Add a new photo to the gallery"""
        new_photo = PropertyPhoto(**photo_data)
        self.photos.append(new_photo)
        self.save()
        return new_photo

    def get_photos_by_type(self, photo_type):
        """Get all photos of a specific type"""
        return [photo for photo in self.photos if photo.photo_type == photo_type]

    def get_primary_photo(self):
        """Get the primary photo for the property"""
        primary_photos = [photo for photo in self.photos if photo.is_primary]
        return primary_photos[0] if primary_photos else None

    def validate_required_photos(self):
        """Validate that all required photo types are present"""
        required_types = ['exterior_front', 'exterior_rear', 'street_scene']
        existing_types = set(photo.photo_type for photo in self.photos)
        return {
            'is_complete': all(rt in existing_types for rt in required_types),
            'missing_types': [rt for rt in required_types if rt not in existing_types]
        }