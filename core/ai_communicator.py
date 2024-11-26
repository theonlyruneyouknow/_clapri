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
        logger.debug("Initializing Enhanced AICommunicator")
        # Context tracking
        self.conversation_context = {}
        
        # Main response patterns
        self.responses = {
            # Property Type Related
            r'(?i).*residential.*|.*house.*|.*home.*|.*condo.*': {
                'response': """
                    For residential properties, we provide comprehensive appraisals for:
                    • Single-family homes
                    • Condominiums and townhouses
                    • Multi-family units
                    • New construction
                    
                    Would you like to discuss a specific type of residential property?
                """,
                'context': 'residential',
                'follow_up': ['specific_property_type', 'schedule_appointment']
            },

            # Commercial Queries
            r'(?i).*commercial.*|.*office.*|.*retail.*|.*business.*': {
                'response': """
                    Our commercial appraisal services include:
                    • Office buildings
                    • Retail spaces
                    • Industrial properties
                    • Mixed-use developments
                    
                    Commercial appraisals typically require more detailed analysis. Would you like to schedule a consultation?
                """,
                'context': 'commercial',
                'follow_up': ['property_size', 'schedule_consultation']
            },

            # Timeline Questions
            r'(?i).*how.*long.*|.*timeline.*|.*when.*complete.*': {
                'response': """
                    Typical timelines for our services:
                    • Residential appraisals: 3-5 business days
                    • Commercial appraisals: 5-10 business days
                    • Rush services available for urgent needs
                    
                    Would you like to discuss specific timing requirements?
                """,
                'context': 'timeline',
                'follow_up': ['rush_service', 'schedule_appointment']
            },

            # Process Questions
            r'(?i).*process.*|.*step.*|.*involve.*|.*what.*happen.*': {
                'response': """
                    Our appraisal process includes:
                    1. Initial consultation and property information gathering
                    2. Physical property inspection
                    3. Market research and analysis
                    4. Detailed report preparation
                    
                    Which part of the process would you like to learn more about?
                """,
                'context': 'process',
                'follow_up': ['process_details', 'schedule_appointment']
            },

            # Document Requirements
            r'(?i).*document.*|.*need.*bring.*|.*require.*|.*paperwork.*': {
                'response': """
                    Helpful documents for your appraisal:
                    • Recent property tax assessment
                    • Floor plans or surveys if available
                    • List of recent improvements
                    • Previous appraisal reports (if any)
                    
                    Don't worry if you don't have all these - we can discuss during the inspection.
                """,
                'context': 'documents',
                'follow_up': ['document_questions', 'schedule_appointment']
            }
        }

        # Follow-up responses based on context
        self.follow_up_responses = {
            'specific_property_type': {
                'condo': "For condominiums, we analyze both the unit and common elements...",
                'single_family': "For single-family homes, we consider factors like lot size, improvements...",
                'multi_family': "Multi-family appraisals include analysis of rental income potential..."
            },
            'property_size': {
                'small': "For properties under 5,000 sq ft...",
                'medium': "For properties between 5,000-20,000 sq ft...",
                'large': "For properties over 20,000 sq ft..."
            },
            'process_details': {
                'inspection': "The inspection typically takes 1-3 hours depending on property size...",
                'report': "Our detailed reports include comparable sales analysis...",
                'research': "We conduct extensive market research specific to your property type..."
            }
        }

    def get_response(self, user_input: str, session_id: str = None) -> str:
        try:
            # Track conversation context
            if session_id not in self.conversation_context:
                self.conversation_context[session_id] = {
                    'last_context': None,
                    'interaction_count': 0,
                    'topics_discussed': set()
                }
            
            context = self.conversation_context[session_id]
            context['interaction_count'] += 1

            # Check for follow-up questions based on previous context
            if context['last_context']:
                follow_up_response = self._handle_follow_up(user_input, context)
                if follow_up_response:
                    return follow_up_response

            # Process main response patterns
            for pattern, response_data in self.responses.items():
                if re.search(pattern, user_input):
                    context['last_context'] = response_data['context']
                    context['topics_discussed'].add(response_data['context'])
                    return self._format_response(response_data['response'])

            # If no pattern matches, use contextual default response
            return self._get_contextual_default_response(context)

        except Exception as e:
            logger.error(f"Error in get_response: {str(e)}")
            return "I apologize for the confusion. Could you please rephrase your question about our appraisal services?"

    def _handle_follow_up(self, user_input: str, context: Dict) -> str:
        """Handle follow-up questions based on conversation context"""
        last_context = context['last_context']
        
        if last_context == 'residential':
            if re.search(r'(?i).*condo.*', user_input):
                return self.follow_up_responses['specific_property_type']['condo']
            elif re.search(r'(?i).*house.*|.*home.*', user_input):
                return self.follow_up_responses['specific_property_type']['single_family']

        elif last_context == 'process':
            if re.search(r'(?i).*inspect.*|.*visit.*', user_input):
                return self.follow_up_responses['process_details']['inspection']
            elif re.search(r'(?i).*report.*', user_input):
                return self.follow_up_responses['process_details']['report']

        return None

    def _get_contextual_default_response(self, context: Dict) -> str:
        """Generate a contextual default response based on conversation history"""
        if context['interaction_count'] == 1:
            return """
                Welcome! I'm here to help with your appraisal needs. I can provide information about:
                • Our appraisal services and process
                • Required documentation
                • Timelines and scheduling
                • Specific property types
                
                What would you like to know about?
            """
        
        # If we've discussed multiple topics, suggest related topics
        if len(context['topics_discussed']) > 0:
            if 'residential' in context['topics_discussed']:
                return """
                    I see we've discussed residential properties. Would you like to:
                    • Learn about our appraisal process
                    • Discuss required documents
                    • Schedule an appointment
                    • Get pricing information
                """
            
            if 'process' in context['topics_discussed']:
                return """
                    Now that we've covered the process, would you like to:
                    • Schedule an appointment
                    • Discuss document requirements
                    • Learn about our pricing
                    • Ask about specific property types
                """

        return """
            I'd be happy to help you with:
            • Information about our appraisal services
            • Understanding the appraisal process
            • Scheduling appointments
            • Document requirements
            • Pricing information
            
            Please let me know what interests you.
        """

    def _format_response(self, response: str) -> str:
        """Clean and format the response text"""
        # Remove extra whitespace and normalize line endings
        response = re.sub(r'\s+', ' ', response.strip())
        # Ensure proper capitalization and punctuation
        response = response.strip()
        if response and response[-1] not in '.!?':
            response += '.'
        return response