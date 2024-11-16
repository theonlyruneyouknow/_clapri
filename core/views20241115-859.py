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
from .models import UserProfile
from .forms import ContactForm, ProfileForm
import logging
import secrets


logger = logging.getLogger(__name__)

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
            # Send email to admin
            admin_email_context = {
                'name': form.cleaned_data['name'],
                'email': form.cleaned_data['email'],
                'phone': form.cleaned_data['phone'],
                'service_type': form.cleaned_data['service_type'],
                'message': form.cleaned_data['message'],
            }
            
            admin_email_body = render_to_string('core/emails/contact_admin.txt', admin_email_context)
            
            send_mail(
                subject=f"New Contact Form Submission from {form.cleaned_data['name']}",
                message=admin_email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,
            )

            # Send confirmation email to user
            user_email_context = {
                'name': form.cleaned_data['name'],
            }
            
            user_email_body = render_to_string('core/emails/contact_confirmation.txt', user_email_context)
            
            send_mail(
                subject="We've Received Your Message - Appraisal Pro",
                message=user_email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[form.cleaned_data['email']],
                fail_silently=True,
            )

            messages.success(self.request, "Thank you for contacting us! We'll get back to you soon.")
        except Exception as e:
            logger.error(f"Email error: {str(e)}")
            messages.warning(
                self.request,
                "Your message was received but there was an issue sending confirmation emails. We'll still contact you soon."
            )
        
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

class ProfileView(TemplateView):
    template_name = 'core/profile.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_auth0_user(self.request)
        profile = UserProfile.objects(user_id=user['sub']).first()
        
        context.update({
            'user': user,
            'profile': profile
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
        return {}

    def form_valid(self, form):
        user = get_auth0_user(self.request)
        profile = UserProfile.objects(user_id=user['sub']).first()
        
        if not profile:
            profile = UserProfile(
                user_id=user['sub'],
                email=user['email']
            )
        
        profile.first_name = form.cleaned_data['first_name']
        profile.last_name = form.cleaned_data['last_name']
        profile.phone = form.cleaned_data['phone']
        profile.company = form.cleaned_data['company']
        profile.address = form.cleaned_data['address']
        profile.city = form.cleaned_data['city']
        profile.state = form.cleaned_data['state']
        profile.zip_code = form.cleaned_data['zip_code']
        
        profile.save()
        
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)
    


    
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
