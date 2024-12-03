from mongoengine import Document, EmbeddedDocument, StringField, DateTimeField, IntField, FloatField, \
    BooleanField, ListField, EmbeddedDocumentField, ReferenceField, URLField, DictField
from datetime import datetime

class RoomDetails(EmbeddedDocument):
    """Detailed room inspection data"""
    room_type = StringField(required=True, choices=[
        'bedroom', 'bathroom', 'kitchen', 'living_room', 'dining_room', 
        'family_room', 'basement', 'garage', 'other'
    ])
    floor_level = IntField()  # 1 for first floor, 2 for second, etc.
    dimensions = StringField()  # e.g., "12x14"
    flooring = StringField()
    walls = StringField()
    ceiling = StringField()
    windows = IntField()
    closets = IntField()
    condition = StringField(choices=['poor', 'fair', 'average', 'good', 'excellent'])
    features = ListField(StringField())
    defects = ListField(StringField())
    notes = StringField()

class ExteriorInspection(EmbeddedDocument):
    """Exterior elements inspection data"""
    foundation_type = StringField()
    foundation_condition = StringField(choices=['poor', 'fair', 'average', 'good', 'excellent'])
    exterior_walls_type = StringField()
    exterior_walls_condition = StringField(choices=['poor', 'fair', 'average', 'good', 'excellent'])
    roof_type = StringField()
    roof_condition = StringField(choices=['poor', 'fair', 'average', 'good', 'excellent'])
    windows_type = StringField()
    windows_condition = StringField(choices=['poor', 'fair', 'average', 'good', 'excellent'])
    landscaping_condition = StringField(choices=['poor', 'fair', 'average', 'good', 'excellent'])
    driveway_type = StringField()
    driveway_condition = StringField(choices=['poor', 'fair', 'average', 'good', 'excellent'])
    defects = ListField(StringField())
    notes = StringField()

class SystemsInspection(EmbeddedDocument):
    """Property systems inspection data"""
    heating_type = StringField()
    heating_age = IntField()
    heating_condition = StringField(choices=['poor', 'fair', 'average', 'good', 'excellent'])
    cooling_type = StringField()
    cooling_age = IntField()
    cooling_condition = StringField(choices=['poor', 'fair', 'average', 'good', 'excellent'])
    plumbing_type = StringField()
    plumbing_condition = StringField(choices=['poor', 'fair', 'average', 'good', 'excellent'])
    electrical_type = StringField()
    electrical_condition = StringField(choices=['poor', 'fair', 'average', 'good', 'excellent'])
    defects = ListField(StringField())
    notes = StringField()

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

class InspectionChecklist(Document):
    """Main inspection checklist document"""
    appraisal_report = ReferenceField('AppraisalReport', required=True)
    inspector = StringField(required=True)
    inspection_date = DateTimeField(required=True)
    weather_conditions = StringField()
    occupancy_status = StringField(choices=[
        'owner_occupied', 'tenant_occupied', 'vacant', 'unknown'
    ])
    
    # Access and Contact
    contact_name = StringField()
    contact_phone = StringField()
    access_notes = StringField()
    
    # Inspection Components
    rooms = ListField(EmbeddedDocumentField(RoomDetails))
    exterior = EmbeddedDocumentField(ExteriorInspection)
    systems = EmbeddedDocumentField(SystemsInspection)
    
    # Measurements and Verification
    verified_square_footage = FloatField()
    measurement_method = StringField(choices=[
        'laser', 'tape', 'plans', 'tax_records', 'other'
    ])
    square_footage_notes = StringField()
    
    # Additional Information
    improvements_since_last_sale = ListField(StringField())
    deferred_maintenance = ListField(StringField())
    environmental_issues = ListField(StringField())
    additional_notes = StringField()
    
    # Status
    checklist_complete = BooleanField(default=False)
    reviewed_by = StringField()
    review_date = DateTimeField()
    
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'inspection_checklists',
        'ordering': ['-inspection_date'],
        'indexes': [
            'appraisal_report',
            'inspection_date',
            'inspector'
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(InspectionChecklist, self).save(*args, **kwargs)

    def validate_checklist(self):
        """Validate checklist completeness"""
        required_sections = {
            'rooms': len(self.rooms) > 0,
            'exterior': bool(self.exterior),
            'systems': bool(self.systems),
            'square_footage': bool(self.verified_square_footage)
        }
        
        return {
            'is_complete': all(required_sections.values()),
            'missing_sections': [k for k, v in required_sections.items() if not v]
        }

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
        'ordering': ['-created_at'],
        'indexes': ['appraisal_report']
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