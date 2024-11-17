# File: core/views.py
# Location: C:\git\_clapri\core\views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.decorators import method_decorator
from urllib.parse import quote, urlencode
from utils.auth import oauth, login_required, get_auth0_user
from .models import UserProfile, AppraisalRequest
from .forms import ContactForm, ProfileForm, AppraisalRequestForm
from .forms import ProfileForm
from .models import UserProfile
from datetime import datetime  # Add this line
import secrets
import logging

logger = logging.getLogger(__name__)

# Keep only these existing views for now
class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        return context

class AboutView(TemplateView):
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        return context

class ServicesView(TemplateView):
    template_name = 'core/services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        return context

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
    
class ProfileView(TemplateView):
    template_name = 'core/profile.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_auth0_user(self.request)
        context['user'] = user
        
        # Get or create profile
        profile = UserProfile.objects(user_id=user['sub']).first()
        if not profile and user:
            # Create profile with Auth0 data
            profile = UserProfile(
                user_id=user['sub'],
                email=user.get('email', ''),
                first_name=user.get('given_name', ''),
                last_name=user.get('family_name', ''),
                # Add any other fields that Auth0 might provide
            )
            profile.save()
        
        context.update({
            'profile': profile,
            'auth0_data': {
                'picture': user.get('picture', None),
                'email_verified': user.get('email_verified', False),
                'locale': user.get('locale', ''),
                'updated_at': user.get('updated_at', ''),
                'name': user.get('name', ''),
                'email': user.get('email', ''),
            }
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
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_auth0_user(self.request)
        profile = UserProfile.objects(user_id=user['sub']).first()

        # For now, we'll use placeholder data
        # Later, we'll replace these with real data from the database
        context.update({
            'user': user,
            'profile': profile,
            'statistics': {
                'total_requests': 0,
                'pending_requests': 0,
                'completed_requests': 0,
                'in_progress': 0
            },
            'recent_requests': [],
            'upcoming_appointments': [],
            'notifications': [
                {
                    'type': 'info',
                    'message': 'Welcome to your dashboard! Start by creating your first appraisal request.',
                    'date': datetime.now()
                }
            ]
        })
        return context
    
class AppraisalRequestView(FormView):
    template_name = 'core/appraisal_request.html'
    form_class = AppraisalRequestForm
    success_url = '/dashboard/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        user = get_auth0_user(self.request)
        
        appraisal_request = AppraisalRequest(
            user_id=user['sub'],
            property_address=form.cleaned_data['property_address'],
            property_city=form.cleaned_data['property_city'],
            property_state=form.cleaned_data['property_state'],
            property_zip=form.cleaned_data['property_zip'],
            property_type=form.cleaned_data['property_type'],
            square_footage=form.cleaned_data['square_footage'],
            year_built=form.cleaned_data['year_built'],
            bedrooms=form.cleaned_data['bedrooms'],
            bathrooms=form.cleaned_data['bathrooms'],
            lot_size=form.cleaned_data['lot_size'],
            purpose=form.cleaned_data['purpose'],
            preferred_date=form.cleaned_data['preferred_date'],
            alternate_date=form.cleaned_data['alternate_date'],
            notes=form.cleaned_data['notes']
        )
        appraisal_request.save()
        
        messages.success(self.request, 'Your appraisal request has been submitted successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        return context






    



def login(request):
    state = secrets.token_urlsafe(32)
    request.session['auth_state'] = state
    return_to = request.GET.get('returnTo', '/')
    request.session['return_to'] = return_to
    
    return oauth.auth0.authorize_redirect(
        request,
        request.build_absolute_uri(reverse('core:callback')),
        audience=settings.AUTH0_AUDIENCE
    )

def callback(request):
    try:
        token = oauth.auth0.authorize_access_token(request)
        userinfo = token.get('userinfo')
        
        if not userinfo:
            logger.error("No user info in token")
            messages.error(request, "Failed to get user information")
            return redirect('core:home')

        request.session['user'] = userinfo
        return_to = request.session.pop('return_to', '/')
        
        messages.success(request, f"Welcome, {userinfo.get('name', 'User')}!")
        return redirect(return_to)

    except Exception as e:
        logger.exception("Callback error")
        messages.error(request, "Authentication failed. Please try again.")
        return redirect('core:home')

def logout(request):
    request.session.clear()
    params = {
        'returnTo': request.build_absolute_uri('/'),
        'client_id': settings.AUTH0_CLIENT_ID
    }
    return redirect(f"https://{settings.AUTH0_DOMAIN}/v2/logout?{urlencode(params)}")