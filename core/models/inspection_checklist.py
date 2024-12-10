# core/models/inspection_checklist.py
from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField, BooleanField
from datetime import datetime

class InspectionChecklist(Document):
    appraisal_request = ReferenceField('AppraisalRequest', required=True)
    inspector = ReferenceField('UserProfile', required=True)
    inspection_date = DateTimeField(default=datetime.now)
    
    # Property Condition
    roof_condition = StringField(choices=['good', 'fair', 'poor'])
    foundation_condition = StringField(choices=['good', 'fair', 'poor'])
    exterior_condition = StringField(choices=['good', 'fair', 'poor'])
    interior_condition = StringField(choices=['good', 'fair', 'poor'])
    
    # Features
    total_rooms = StringField()
    bedrooms = StringField()
    bathrooms = StringField()
    square_footage = StringField()
    
    # Systems
    hvac_system = BooleanField(default=False)
    electrical_system = BooleanField(default=False)
    plumbing_system = BooleanField(default=False)
    
    # Additional Notes
    notes = ListField(StringField())
    defects_found = ListField(StringField())
    
    # Status
    is_complete = BooleanField(default=False)
    completed_at = DateTimeField()

    meta = {
        'collection': 'inspection_checklists',
        'indexes': ['appraisal_request', 'inspector', 'inspection_date']
    }

    def complete_inspection(self):
        self.is_complete = True
        self.completed_at = datetime.now()
        self.save()