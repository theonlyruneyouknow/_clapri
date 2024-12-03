import re
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from django.core.cache import cache

logger = logging.getLogger(__name__)

class AICommunicator:
    def __init__(self):
        self.company_name = "Jeffrey Martin Appraisal Services"
        self.phone = "541 520-9552"
        self.knowledge_base = {
            'services': [
                'Residential Appraisals',
                'Commercial Appraisals',
                'Estate Valuations',
                'Tax Assessment Reviews'
            ],
            'business_hours': {
                'Monday-Friday': '9:00 AM - 5:00 PM',
                'Saturday': '10:00 AM - 2:00 PM',
                'Sunday': 'Closed'
            }
        }
        
        # Define response patterns
        self.patterns = {
            'pricing': {
                'pattern': r'(?i).*(cost|price|fee|charge|how much).*',
                'response': f"""Our appraisal fees vary based on property type and complexity. 
                    For specific pricing, please call us at {self.phone}.
                    Would you like to schedule a consultation to discuss your needs?"""
            },
            'schedule': {
                'pattern': r'(?i).*(schedule|appointment|book|meet).*',
                'response': f"""I can help you schedule an appointment. 
                    Our available times are:
                    - Monday-Friday: 9:00 AM - 5:00 PM
                    - Saturday: 10:00 AM - 2:00 PM
                    
                    Would you like to provide your contact information to schedule an appointment?"""
            },
            'contact': {
                'pattern': r'(?i).*(email|call|contact|reach).*',
                'response': f"""You can reach us at {self.phone} during business hours.
                    Would you like me to collect your information for a callback?"""
            }
        }

    def get_response(self, user_input: str, session_id: str = None) -> Dict:
        try:
            # Check for key patterns
            for key, data in self.patterns.items():
                if re.search(data['pattern'], user_input):
                    return {
                        'text': data['response'],
                        'type': key,
                        'collect_info': key == 'schedule' or key == 'contact'
                    }
            
            # Default response
            return {
                'text': f"""I can help you with information about our appraisal services,
                    scheduling appointments, or connecting you with our team.
                    What would you like to know more about?""",
                'type': 'general',
                'collect_info': False
            }

        except Exception as e:
            logger.error(f"Error in AI response: {str(e)}")
            return {
                'text': f"Please call us at {self.phone} for immediate assistance.",
                'type': 'error',
                'collect_info': False
            }

    def collect_contact_info(self, info: Dict) -> Dict:
        """Process contact information submission"""
        try:
            # Validate the information
            required_fields = ['name', 'phone', 'email']
            if not all(field in info and info[field] for field in required_fields):
                return {
                    'success': False,
                    'message': "Please provide your name, phone number, and email."
                }

            # Store the information (implement your storage logic here)
            # For now, we'll just return success
            return {
                'success': True,
                'message': f"""Thank you, {info['name']}! We'll contact you shortly 
                    to confirm your appointment. You can also reach us at {self.phone}."""
            }

        except Exception as e:
            logger.error(f"Error collecting contact info: {str(e)}")
            return {
                'success': False,
                'message': f"There was an error processing your information. Please call us at {self.phone}."
            }