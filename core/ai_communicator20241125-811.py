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
        # Rule-based responses
        self.responses = {
            r'(?i).*hour.*|.*time.*|.*open.*': """
                Our business hours are:
                - Monday-Friday: 9:00 AM - 5:00 PM
                - Saturday: 10:00 AM - 2:00 PM
                - Sunday: Closed
            """,
            r'(?i).*service.*|.*offer.*': """
                We offer several appraisal services:
                - Residential Appraisals (homes, condos, multi-family)
                - Commercial Appraisals (office, retail, industrial)
                - Estate Valuations (for planning and probate)
                - Tax Assessment Reviews (property tax appeals)
            """,
            r'(?i).*price.*|.*cost.*|.*fee.*': """
                For accurate pricing, we need to assess the specific property and service needed.
                Please:
                1. Call our office at (541) 520-9552 for a quote
                2. Schedule a consultation online
                3. Or provide details about your property type and location
            """,
            r'(?i).*contact.*|.*phone.*|.*email.*': """
                You can reach us through:
                - Phone: (541) 520-9552
                - Email: info@appraisalpro.com
                - Office: 123 Main Street, City, State 12345
                
                For urgent matters, please call during business hours.
            """,
            r'(?i).*appointment.*|.*schedule.*|.*book.*': """
                To schedule an appointment:
                1. Log in to your account (or create one)
                2. Use our online scheduling system
                3. Choose your preferred date and time
                
                Or call us at (541) 520-9552 during business hours.
            """,
            r'(?i).*residential.*|.*house.*|.*home.*': """
                Our residential appraisal services include:
                - Single-family homes
                - Condominiums and townhouses
                - Multi-family units
                - New construction
                
                Would you like to schedule a residential appraisal?
            """,
            r'(?i).*commercial.*|.*business.*|.*office.*': """
                Our commercial appraisal services cover:
                - Office buildings
                - Retail spaces
                - Industrial properties
                - Multi-use facilities
                
                For commercial appraisals, we recommend scheduling a consultation first.
            """,
            r'(?i).*process.*|.*how.*work.*': """
                Our appraisal process includes:
                1. Initial consultation
                2. Property inspection
                3. Market analysis
                4. Detailed report preparation
                
                Would you like more details about any of these steps?
            """,
            r'(?i).*document.*|.*need.*|.*require.*': """
                For appraisals, these documents are helpful:
                - Property deed
                - Recent tax assessment
                - Floor plans (if available)
                - Recent improvements list
                
                Don't worry if you don't have everything - we can discuss during consultation.
            """
        }
        
        # Fallback to free API if no rule matches
        self.api_url = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
        self.headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}

    def get_response(self, user_input: str) -> str:
        try:
            # First, check cache
            cache_key = f"chat_response_{hash(user_input)}"
            cached_response = cache.get(cache_key)
            if cached_response:
                return cached_response

            # Check rule-based responses
            for pattern, response in self.responses.items():
                if re.search(pattern, user_input):
                    cache.set(cache_key, response.strip(), 3600)  # Cache for 1 hour
                    return response.strip()

            # If no rule matches, try API
            try:
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json={"inputs": user_input},
                    timeout=5  # 5 second timeout
                )
                
                if response.status_code == 200:
                    api_response = response.json()[0]['generated_text']
                    # Clean up API response
                    api_response = self._clean_response(api_response)
                    cache.set(cache_key, api_response, 3600)
                    return api_response
                    
            except Exception as api_error:
                logger.error(f"API Error: {str(api_error)}")
                
            # If API fails, return default response
            default_response = """
                I understand you're interested in our appraisal services.
                Would you like to:
                1. Learn about our specific services
                2. Check our business hours
                3. Schedule an appointment
                4. Get contact information
                5. Understand the appraisal process
                
                Please let me know how I can help!
            """
            cache.set(cache_key, default_response.strip(), 3600)
            return default_response.strip()

        except Exception as e:
            logger.error(f"Error in get_response: {str(e)}")
            return "I apologize, but I'm having trouble processing your request. Please try again or contact our office directly."

    def _clean_response(self, response: str) -> str:
        """Clean up API responses to maintain professional tone"""
        # Remove multiple spaces and newlines
        response = ' '.join(response.split())
        # Ensure first letter is capitalized
        response = response.capitalize()
        # Add period if missing
        if response and response[-1] not in '.!?':
            response += '.'
        return response