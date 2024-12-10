# File: leads/email_handler.py
# Location: C:\git\_clapri\leads\email_handler.py

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from typing import Dict, List, Optional
from datetime import datetime
import logging
from .models import Lead, LeadInteraction

logger = logging.getLogger(__name__)

class LeadEmailHandler:
    """Handler for all email communications with leads"""
    
    def __init__(self):
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.reply_to = settings.ADMIN_EMAIL

    def send_lead_email(
        self,
        lead: Lead,
        subject: str,
        template_name: str,
        context: Dict,
        from_email: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email to a lead using a template
        Returns True if successful, False otherwise
        """
        try:
            # Prepare the email
            context['lead'] = lead
            context['company_name'] = settings.COMPANY_NAME
            context['company_phone'] = settings.COMPANY_PHONE
            
            # Render the HTML content
            html_content = render_to_string(f'leads/emails/{template_name}.html', context)
            text_content = strip_tags(html_content)
            
            # Create the email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email or self.from_email,
                to=[lead.email],
                cc=cc,
                bcc=bcc,
                reply_to=[self.reply_to]
            )
            
            # Attach HTML alternative
            email.attach_alternative(html_content, "text/html")
            
            # Send the email
            email.send()
            
            # Record the interaction
            LeadInteraction(
                lead=lead,
                type='email',
                content=text_content,
                email_subject=subject,
                email_to=lead.email,
                email_from=from_email or self.from_email,
                author=context.get('author')
            ).save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to lead {lead.id}: {str(e)}")
            return False

    def send_welcome_email(self, lead: Lead, author) -> bool:
        """Send a welcome email to a new lead"""
        context = {
            'author': author,
            'is_welcome': True
        }
        return self.send_lead_email(
            lead=lead,
            subject=f"Welcome to {settings.COMPANY_NAME}",
            template_name='welcome',
            context=context
        )

    def send_follow_up_email(self, lead: Lead, author, custom_message: str = None) -> bool:
        """Send a follow-up email to a lead"""
        context = {
            'author': author,
            'custom_message': custom_message
        }
        return self.send_lead_email(
            lead=lead,
            subject=f"Following up on your appraisal inquiry",
            template_name='follow_up',
            context=context
        )

    def send_proposal_email(
        self,
        lead: Lead,
        author,
        proposal_url: str,
        proposal_details: Dict
    ) -> bool:
        """Send a proposal email to a lead"""
        context = {
            'author': author,
            'proposal_url': proposal_url,
            'proposal_details': proposal_details
        }
        return self.send_lead_email(
            lead=lead,
            subject=f"Your {settings.COMPANY_NAME} Appraisal Proposal",
            template_name='proposal',
            context=context
        )

    def send_appointment_confirmation(
        self,
        lead: Lead,
        author,
        appointment_date: datetime,
        appointment_details: Dict
    ) -> bool:
        """Send an appointment confirmation email"""
        context = {
            'author': author,
            'appointment_date': appointment_date,
            'appointment_details': appointment_details
        }
        return self.send_lead_email(
            lead=lead,
            subject=f"Appraisal Appointment Confirmation",
            template_name='appointment_confirmation',
            context=context
        )