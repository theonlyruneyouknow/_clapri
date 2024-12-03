# File: core/views.py
# Location: C:\git\_clapri\core\views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import View, TemplateView, FormView, ListView
from django.views.generic.edit import FormView
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.decorators import method_decorator
from urllib.parse import quote, urlencode
from utils.auth import oauth, login_required, get_auth0_user
from .models import UserProfile, AppraisalRequest, Testimonial, Appointment
# from .forms import ContactForm, ProfileForm, AppraisalRequestForm, TestimonialForm
from .forms import ContactForm, ProfileForm, AppraisalRequestForm, TestimonialForm, AppointmentScheduleForm
from content_management.models import PageContent  # Add this import
from datetime import datetime, timedelta
from django.utils import timezone
import secrets
import logging
from django.http import JsonResponse
from django.views import View
from .ai_communicator import AICommunicator
import json
import traceback

# Configure logger
logger = logging.getLogger(__name__)

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        
        # Get current page content if it exists
        try:
            from content_management.models import PageContent
            content = PageContent.objects.filter(
                page_type='home',
                active=True,
                archived=False
            ).first()
            context['page_content'] = content
        except:
            context['page_content'] = None
            
        return context

class ServicesView(TemplateView):
    template_name = 'core/services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        
        # Get active content for the services page
        now = datetime.now()
        context['page_content'] = PageContent.objects.filter(
            page_type='services',
            active=True,
            archived=False
        ).filter(
            display_from__lte=now
        ).filter(
            display_until__gt=now
        ).first() or None
        
        return context
    
    template_name = 'core/services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        
        # Get active content for the services page
        now = datetime.now()
        context['page_content'] = PageContent.objects.filter(
            page_type='services',
            active=True,
            archived=False
        ).filter(
            display_from__lte=now
        ).filter(
            display_until__gt=now
        ).first() or None
        
        return context

class ProfileView(TemplateView):
    template_name = 'core/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_auth0_user(self.request)
        
        print("\n=== DEBUG USER INFO ===")
        print("Complete user object:", user)
        print("Is admin check paths:")
        print("- Direct is_admin:", user.get('is_admin'))
        print("- /app_metadata:", user.get('/app_metadata'))
        print("- /user_metadata:", user.get('/user_metadata'))
        print("======================\n")

        # Simplified admin check
        is_admin = bool(
            user.get('is_admin') or
            (user.get('/app_metadata', {}) or {}).get('is_admin') or
            (user.get('/user_metadata', {}) or {}).get('is_admin')
        )

        auth_data = {
            'picture': user.get('picture', None),
            'email_verified': user.get('email_verified', False),
            'locale': user.get('locale', ''),
            'updated_at': user.get('updated_at', ''),
            'name': user.get('name', ''),
            'email': user.get('email', ''),
            'is_admin': is_admin,  # This should now correctly reflect admin status
            'app_metadata': user.get('/app_metadata', {}),
            'user_metadata': user.get('/user_metadata', {})
        }

        context.update({
            'user': user,
            'auth0_data': auth_data
        })
        return context

class ProfileEditView(FormView):
    template_name = 'core/profile_edit.html'
    form_class = ProfileForm
    success_url = '/profile/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        user = get_auth0_user(self.request)
        profile = UserProfile.objects(user_id=user['sub']).first()
        
        if profile:
            return {
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'phone': profile.phone,
                'company': profile.company,
                'address': profile.address,
                'city': profile.city,
                'state': profile.state,
                'zip_code': profile.zip_code,
            }
        # Pre-fill with Auth0 data if no profile exists
        return {
            'first_name': user.get('given_name', ''),
            'last_name': user.get('family_name', ''),
            'email': user.get('email', ''),
        }

class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user = get_auth0_user(request)
        profile = UserProfile.objects(user_id=user['sub']).first()
        
        # Get recent appraisal requests
        recent_requests = AppraisalRequest.objects(user_id=user['sub']).order_by('-created_at')
        
        context = {
            'user': user,
            'profile': profile,
            'recent_requests': recent_requests,
        }
        
        return render(request, self.template_name, context)

class ContactView(FormView):
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = '/contact/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        return context

    def form_valid(self, form):
        try:
            # Your existing contact form logic
            messages.success(self.request, "Thank you for contacting us! We'll get back to you soon.")
        except Exception as e:
            logger.error(f"Email error: {str(e)}")
            messages.warning(
                self.request,
                "Your message was received but there was an issue sending confirmation emails. We'll still contact you soon."
            )
        return super().form_valid(form)   

class ServicesView(TemplateView):
    template_name = 'core/services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        
        # Get active content for the services page
        now = datetime.now()
        context['page_content'] = PageContent.objects.filter(
            page_type='services',
            active=True,
            archived=False
        ).filter(
            display_from__lte=now
        ).filter(
            display_until__gt=now
        ).first() or None
        
        return context
    
    template_name = 'core/services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        
        # Get active content for the services page
        now = datetime.now()
        context['page_content'] = PageContent.objects.filter(
            page_type='services',
            active=True,
            archived=False
        ).filter(
            display_from__lte=now
        ).filter(
            display_until__gt=now
        ).first() or None
        
        return context
    
class AboutView(TemplateView):
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        
        # Get active content for the about page
        now = datetime.now()
        context['page_content'] = PageContent.objects.filter(
            page_type='about',
            active=True,
            archived=False
        ).filter(
            display_from__lte=now
        ).filter(
            display_until__gt=now
        ).first() or None
        
        return context

class ChatView(View):
    def __init__(self):
        super().__init__()
        self.ai = AICommunicator()

    def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            contact_info = data.get('contact_info')

            if contact_info:
                # Handle contact information submission
                result = self.ai.collect_contact_info(contact_info)
                return JsonResponse(result)
            else:
                # Handle regular chat message
                response = self.ai.get_response(message, request.session.session_key)
                return JsonResponse({
                    'status': 'success',
                    'response': response['text'],
                    'collect_info': response['collect_info']
                })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)