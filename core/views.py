# File: core/views.py
# Location: C:\git\_clapri\core\views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View  # Add View here
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
from .models import UserProfile, AppraisalRequest, Testimonial
from .forms import ContactForm, ProfileForm, AppraisalRequestForm, TestimonialForm
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

class TestimonialsView(TemplateView):
    template_name = 'core/testimonials.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_auth0_user(self.request)
        context['user'] = user
        
        # Get approved testimonials for public display
        context['testimonials'] = Testimonial.objects(is_approved=True).order_by('-created_at')
        
        # If user is logged in, get their testimonials too
        if user:
            context['user_testimonials'] = Testimonial.objects(user_id=user['sub']).order_by('-created_at')
        
        return context

class TestimonialCreateView(FormView):
    template_name = 'core/testimonial_form.html'
    form_class = TestimonialForm
    success_url = '/testimonials/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        context['is_edit'] = False
        return context

    def form_valid(self, form):
        user = get_auth0_user(self.request)
        
        testimonial = Testimonial(
            user_id=user['sub'],
            author_name=user.get('name', ''),
            author_company=form.cleaned_data.get('company', ''),
            title=form.cleaned_data['title'],
            content=form.cleaned_data['content'],
            rating=int(form.cleaned_data['rating'])
        )
        testimonial.save()
        
        messages.success(self.request, 'Your testimonial has been submitted and will be reviewed shortly.')
        return super().form_valid(form)

class TestimonialEditView(FormView):
    template_name = 'core/testimonial_form.html'
    form_class = TestimonialForm
    success_url = '/testimonials/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        testimonial = self.get_testimonial()
        return {
            'title': testimonial.title,
            'content': testimonial.content,
            'rating': str(testimonial.rating),
            'company': testimonial.author_company
        }

    def get_testimonial(self):
        user = get_auth0_user(self.request)
        testimonial = get_object_or_404(Testimonial, 
                                      id=self.kwargs['testimonial_id'],
                                      user_id=user['sub'])
        return testimonial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        context['is_edit'] = True
        context['testimonial'] = self.get_testimonial()
        return context

    def form_valid(self, form):
        testimonial = self.get_testimonial()
        testimonial.title = form.cleaned_data['title']
        testimonial.content = form.cleaned_data['content']
        testimonial.rating = int(form.cleaned_data['rating'])
        testimonial.author_company = form.cleaned_data.get('company', '')
        testimonial.is_approved = False  # Require re-approval after edit
        testimonial.save()
        
        messages.success(self.request, 'Your testimonial has been updated and will be reviewed again.')
        return super().form_valid(form)

class AdminTestimonialsView(TemplateView):
    template_name = 'core/admin/testimonials.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        user = get_auth0_user(self.request)
        if not user.get('app_metadata', {}).get('is_admin', False):
            messages.error(self.request, "You don't have permission to access this page.")
            return redirect('core:home')
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        
        # Get testimonials with filter options
        filter_status = self.request.GET.get('status', 'pending')
        if filter_status == 'pending':
            testimonials = Testimonial.objects(is_approved=False).order_by('-created_at')
        elif filter_status == 'approved':
            testimonials = Testimonial.objects(is_approved=True).order_by('-created_at')
        else:  # all
            testimonials = Testimonial.objects.order_by('-created_at')
            
        context.update({
            'testimonials': testimonials,
            'filter_status': filter_status,
            'pending_count': Testimonial.objects(is_approved=False).count(),
            'approved_count': Testimonial.objects(is_approved=True).count(),
            'total_count': Testimonial.objects.count(),
        })
        return context

class AdminTestimonialApproveView(View):
    @method_decorator(login_required)
    def post(self, request, testimonial_id):
        user = get_auth0_user(request)
        if not user.get('app_metadata', {}).get('is_admin', False):
            messages.error(request, "You don't have permission to perform this action.")
            return redirect('core:home')
            
        testimonial = get_object_or_404(Testimonial, id=testimonial_id)
        testimonial.is_approved = True
        testimonial.save()
        
        # Send notification email to the user
        try:
            user_profile = UserProfile.objects(user_id=testimonial.user_id).first()
            if user_profile and user_profile.email:
                send_mail(
                    subject="Your testimonial has been approved!",
                    message=f"Your testimonial '{testimonial.title}' has been approved and is now visible on our website.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user_profile.email],
                    fail_silently=True,
                )
        except Exception as e:
            logger.error(f"Failed to send approval notification: {str(e)}")
        
        messages.success(request, "Testimonial approved successfully.")
        return redirect('core:admin_testimonials')

class AdminTestimonialRejectView(View):
    @method_decorator(login_required)
    def post(self, request, testimonial_id):
        user = get_auth0_user(request)
        if not user.get('app_metadata', {}).get('is_admin', False):
            messages.error(request, "You don't have permission to perform this action.")
            return redirect('core:home')
            
        testimonial = get_object_or_404(Testimonial, id=testimonial_id)
        testimonial.delete()
        
        messages.success(request, "Testimonial rejected and deleted.")
        return redirect('core:admin_testimonials')

def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    user = get_auth0_user(self.request)
    
    # Check admin status using the correct paths
    is_admin = (
        user.get('is_admin') or 
        user.get('/app_metadata', {}).get('is_admin') or 
        user.get('/user_metadata', {}).get('is_admin')
    )
    
    auth_data = {
        'picture': user.get('picture', None),
        'email_verified': user.get('email_verified', False),
        'locale': user.get('locale', ''),
        'updated_at': user.get('updated_at', ''),
        'name': user.get('name', ''),
        'email': user.get('email', ''),
        'is_admin': is_admin,  # This should now be correct
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
        """Pre-populate form with existing profile data"""
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
        
        # Add debugging
        print("=== Auth0 Debug Info ===")
        print("Token:", token)
        print("Userinfo:", userinfo)
        print("ID Token:", token.get('id_token'))
        print("Access Token:", token.get('access_token'))
        print("=====================")
        
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