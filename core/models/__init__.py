from .core_models import UserProfile, AppraisalRequest, Testimonial, Appointment

# Import new models
from .appraisal import AppraisalReport
from .inspection import InspectionChecklist
from .photo import PhotoGallery, PropertyPhoto

# Make all models available at the package level
__all__ = [
    'UserProfile',
    'AppraisalRequest',
    'Testimonial',
    'AppraisalReport',
    'InspectionChecklist',
    'PhotoGallery',
    'PropertyPhoto',
    'Appointment'
]