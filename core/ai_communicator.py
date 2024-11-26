# File: core/ai_communicator.py
# Location: C:\git\_clapri\core\ai_communicator.py

import re
import logging
import requests
from typing import Dict, List
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

class AICommunicator:
    def __init__(self):
        self.patterns = {
            'pricing': {
                'pattern': r'(?i).*(cost|price|fee|charge|how much|estimate).*',
                'response': """
                    I can help explain our pricing structure. Appraisal fees are based on:

                    For Residential Properties:
                    • Single Family: Usually $500-700
                    • Condos/Townhouses: Usually $450-600
                    • Multi-Family: Starting at $800
                    • Rush Service: Additional $150-200

                    Would you like to:
                    1. Get a specific quote for your property?
                    2. Schedule a consultation?
                    3. Learn about what's included in the appraisal?

                    Note: These are general ranges. For an exact quote, please provide your property details or call us at (541) 520-9552.
                """
            },
            'residential_info': {
                'pattern': r'(?i).*(house|home|condo|apartment|residential|townhouse).*',
                'response': """
                    For residential appraisals, here's what we provide:

                    Standard Package ($500-700):
                    • Full property inspection (interior & exterior)
                    • Detailed market analysis with 3-5 comparables
                    • Property condition assessment
                    • 15-20 page comprehensive report
                    • Completion in 3-5 business days

                    The report is accepted by:
                    • All major banks and lenders
                    • Government agencies
                    • Courts and legal proceedings
                    
                    Would you like to schedule an appointment or learn more about our residential process?
                """
            },
            'commercial_info': {
                'pattern': r'(?i).*(commercial|business|office|retail|industrial).*',
                'response': """
                    Our commercial appraisal services include:

                    Process Overview:
                    1. Initial free consultation
                    2. Property inspection & market research
                    3. Financial analysis (including income approach)
                    4. Detailed valuation report

                    Types We Handle:
                    • Office Buildings: 5,000-100,000+ sq ft
                    • Retail Spaces: Strip malls to large retail centers
                    • Industrial Properties: Warehouses, manufacturing
                    • Mixed-Use Developments
                    
                    Would you like to schedule a free consultation to discuss your commercial property?
                """
            },
            'process': {
                'pattern': r'(?i).*(process|step|involve|what.*happen|how.*work).*',
                'response': """
                    Here's our simple 4-step appraisal process:

                    1. Initial Contact (Today):
                       • Schedule appointment
                       • Get price quote
                       • Discuss requirements

                    2. Property Inspection (Day of Appointment):
                       • Interior & exterior inspection
                       • Photos and measurements
                       • 30-60 minutes typically

                    3. Valuation Analysis (2-3 Days):
                       • Market research
                       • Comparable property analysis
                       • Detailed report preparation

                    4. Report Delivery (3-5 Business Days):
                       • Complete valuation report
                       • Available in PDF format
                       • Review with appraiser if needed

                    Ready to start the process? I can help schedule your appointment now.
                """
            },
            'timing': {
                'pattern': r'(?i).*(how long|time|duration|when|schedule|available|turnaround).*',
                'response': """
                    Our typical timeline:

                    Appointment Scheduling:
                    • Next available: Usually within 2-3 business days
                    • Rush service available

                    Report Completion:
                    • Standard: 3-5 business days after inspection
                    • Rush Service: 1-2 business days (additional fee)

                    Current Availability:
                    • Monday-Friday: 9:00 AM - 5:00 PM
                    • Saturday: 10:00 AM - 2:00 PM
                    • Flexible hours by appointment

                    Would you like to check specific dates for your appointment?
                """
            },
            'documents': {
                'pattern': r'(?i).*(document|paper|bring|need|required).*',
                'response': """
                    Documents that help with your appraisal:

                    Essential Documents:
                    • Property deed or tax bill
                    • Recent tax assessment
                    • House plans (if available)

                    If Available:
                    • Recent improvements list
                    • Previous appraisal reports
                    • Home inspection reports
                    • HOA documents (if applicable)

                    Note: Don't worry if you don't have all items - we can still complete your appraisal. Would you like to schedule now?
                """
            },
            'greeting': {
                'pattern': r'(?i)^\s*(hi|hello|hey|good|afternoon|morning|evening).*',
                'response': """
                    Welcome to Jeffrey Martin Appraisal Services! 
                    
                    I can help you with:
                    1. Getting a price quote
                    2. Scheduling an appraisal
                    3. Understanding our process
                    4. Required documents
                    
                    What information can I provide for you today?
                """
            }
        }
        
        # Follow-up responses based on previous context
        self.follow_ups = {
            'pricing': [
                "Would you like a specific quote for your property type?",
                "Should I explain what's included in our appraisal fees?",
                "Would you like to schedule an appointment?"
            ],
            'residential_info': [
                "Would you like to know the typical timeline for residential appraisals?",
                "Shall I explain what documents you'll need?",
                "Would you like to schedule an appointment now?"
            ],
            'commercial_info': [
                "Would you like to schedule a free consultation?",
                "Shall I explain our commercial appraisal process?",
                "Would you like information about our commercial rates?"
            ]
        }

    def get_response(self, user_input: str, session_id: str = None) -> str:
        try:
            # Match pattern and get response
            for category, data in self.patterns.items():
                if re.search(data['pattern'], user_input.lower()):
                    response = data['response'].strip()
                    
                    # Add follow-up if available
                    if category in self.follow_ups:
                        import random
                        response += f"\n\n{random.choice(self.follow_ups[category])}"
                    
                    return response

            # Default response with specific call to action
            return """
                I can provide specific information about:

                • Pricing and quotes for your property
                • Our appraisal process (3-5 business days)
                • Required documents
                • Scheduling an appointment
                • Commercial or residential services

                What would you like to know more about?
            """.strip()

        except Exception as e:
            logger.error(f"Error in get_response: {str(e)}")
            return "I apologize for the confusion. Please call us at (541) 520-9552 for immediate assistance, or let me know what specific information you need about our appraisal services."
