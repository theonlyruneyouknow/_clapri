from datetime import datetime
from typing import Dict, List, Optional
import logging
from pathlib import Path
from core.models import InspectionChecklist, PhotoGallery

class ReportGenerator:
    """Handles generation of inspection reports and photo documentation"""
    
    def __init__(self, inspection: InspectionChecklist, gallery: PhotoGallery = None):
        self.inspection = inspection
        self.gallery = gallery
        self.logger = logging.getLogger(__name__)

    def generate_inspection_report(self) -> Dict:
        """Generate a complete inspection report with all findings"""
        try:
            report_data = {
                'report_info': self._get_report_info(),
                'property_overview': self._get_property_overview(),
                'exterior_inspection': self._get_exterior_details(),
                'interior_inspection': self._get_interior_details(),
                'systems_inspection': self._get_systems_details(),
                'issues_and_concerns': self._get_issues_summary(),
                'photo_references': self._get_photo_references() if self.gallery else None,
                'validation': self.inspection.validate_checklist()
            }
            
            return {
                'success': True,
                'data': report_data,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating inspection report: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now()
            }

    def generate_photo_documentation(self) -> Dict:
        """Generate organized photo documentation with descriptions"""
        if not self.gallery:
            return {'success': False, 'error': 'No photo gallery provided'}

        try:
            photo_doc = {
                'property_info': self._get_property_info(),
                'photo_summary': self._get_photo_summary(),
                'categorized_photos': self._get_categorized_photos(),
                'validation': self.gallery.validate_required_photos()
            }
            
            return {
                'success': True,
                'data': photo_doc,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating photo documentation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now()
            }

    def _get_report_info(self) -> Dict:
        """Get basic report information"""
        return {
            'inspector': self.inspection.inspector,
            'inspection_date': self.inspection.inspection_date,
            'weather_conditions': self.inspection.weather_conditions,
            'occupancy_status': self.inspection.occupancy_status,
            'contact_info': {
                'name': self.inspection.contact_name,
                'phone': self.inspection.contact_phone
            }
        }

    def _get_property_overview(self) -> Dict:
        """Get property overview information"""
        appraisal = self.inspection.appraisal_report
        return {
            'address': appraisal.location.address,
            'city': appraisal.location.city,
            'state': appraisal.location.state,
            'zip_code': appraisal.location.zip_code,
            'property_type': appraisal.characteristics.property_type,
            'year_built': appraisal.characteristics.year_built,
            'square_footage': {
                'reported': appraisal.characteristics.square_footage,
                'verified': self.inspection.verified_square_footage,
                'measurement_method': self.inspection.measurement_method,
                'notes': self.inspection.square_footage_notes
            }
        }

    def _get_exterior_details(self) -> Dict:
        """Get detailed exterior inspection findings"""
        exterior = self.inspection.exterior
        return {
            'foundation': {
                'type': exterior.foundation_type,
                'condition': exterior.foundation_condition
            },
            'exterior_walls': {
                'type': exterior.exterior_walls_type,
                'condition': exterior.exterior_walls_condition
            },
            'roof': {
                'type': exterior.roof_type,
                'condition': exterior.roof_condition
            },
            'windows': {
                'type': exterior.windows_type,
                'condition': exterior.windows_condition
            },
            'landscaping': {
                'condition': exterior.landscaping_condition
            },
            'driveway': {
                'type': exterior.driveway_type,
                'condition': exterior.driveway_condition
            },
            'defects': exterior.defects,
            'notes': exterior.notes
        }

    def _get_interior_details(self) -> List[Dict]:
        """Get detailed interior inspection findings by room"""
        return [{
            'room_type': room.room_type,
            'floor_level': room.floor_level,
            'dimensions': room.dimensions,
            'features': {
                'flooring': room.flooring,
                'walls': room.walls,
                'ceiling': room.ceiling,
                'windows': room.windows,
                'closets': room.closets
            },
            'condition': room.condition,
            'special_features': room.features,
            'defects': room.defects,
            'notes': room.notes
        } for room in self.inspection.rooms]

    def _get_systems_details(self) -> Dict:
        """Get detailed systems inspection findings"""
        systems = self.inspection.systems
        return {
            'heating': {
                'type': systems.heating_type,
                'age': systems.heating_age,
                'condition': systems.heating_condition
            },
            'cooling': {
                'type': systems.cooling_type,
                'age': systems.cooling_age,
                'condition': systems.cooling_condition
            },
            'plumbing': {
                'type': systems.plumbing_type,
                'condition': systems.plumbing_condition
            },
            'electrical': {
                'type': systems.electrical_type,
                'condition': systems.electrical_condition
            },
            'defects': systems.defects,
            'notes': systems.notes
        }

    def _get_issues_summary(self) -> Dict:
        """Summarize all identified issues and concerns"""
        return {
            'deferred_maintenance': self.inspection.deferred_maintenance,
            'environmental_issues': self.inspection.environmental_issues,
            'improvements': self.inspection.improvements_since_last_sale,
            'general_notes': self.inspection.additional_notes
        }

    def _get_property_info(self) -> Dict:
        """Get basic property information for photo documentation"""
        appraisal = self.inspection.appraisal_report
        return {
            'address': appraisal.location.address,
            'inspection_date': self.inspection.inspection_date,
            'inspector': self.inspection.inspector,
            'property_type': appraisal.characteristics.property_type
        }

    def _get_photo_summary(self) -> Dict:
        """Get summary of photo documentation"""
        return {
            'total_photos': self.gallery.total_photos,
            'photo_types': self._get_photo_type_counts(),
            'primary_photo': self._get_primary_photo_info(),
            'upload_complete': self.gallery.upload_complete
        }

    def _get_photo_type_counts(self) -> Dict[str, int]:
        """Get count of photos by type"""
        counts = {}
        for photo in self.gallery.photos:
            counts[photo.photo_type] = counts.get(photo.photo_type, 0) + 1
        return counts

    def _get_primary_photo_info(self) -> Optional[Dict]:
        """Get information about the primary photo"""
        primary = self.gallery.get_primary_photo()
        if primary:
            return {
                'url': primary.photo_url,
                'type': primary.photo_type,
                'description': primary.description,
                'taken_at': primary.taken_at
            }
        return None

    def _get_categorized_photos(self) -> Dict[str, List[Dict]]:
        """Get photos organized by category with details"""
        categories = {}
        for photo in self.gallery.photos:
            photo_info = {
                'url': photo.photo_url,
                'description': photo.description,
                'location': photo.location,
                'taken_at': photo.taken_at,
                'coordinates': photo.coordinates,
                'tags': photo.tags
            }
            
            if photo.photo_type not in categories:
                categories[photo.photo_type] = []
            categories[photo.photo_type].append(photo_info)
            
        return categories

    def _get_photo_references(self) -> Dict:
        """Get photo references for inspection findings"""
        if not self.gallery:
            return None
            
        references = {
            'exterior': {},
            'interior': {},
            'defects': [],
            'systems': {}
        }
        
        for photo in self.gallery.photos:
            if photo.photo_type.startswith('exterior'):
                references['exterior'][photo.location] = photo.photo_url
            elif photo.photo_type == 'interior_room':
                references['interior'][photo.location] = photo.photo_url
            elif photo.photo_type == 'defect':
                references['defects'].append({
                    'url': photo.photo_url,
                    'description': photo.description,
                    'location': photo.location
                })
            
        return references