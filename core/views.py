# File: core/views.py
# Location: C:\git\_clapri\core\views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, TemplateView, FormView, ListView
from django.views.generic.edit import FormView, CreateView
from django.urls import reverse, reverse_lazy
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.decorators import method_decorator
from django.http import HttpResponseForbidden
from urllib.parse import quote, urlencode
from utils.auth import oauth, login_required, get_auth0_user
from .models import UserProfile, AppraisalRequest, Testimonial, Appointment, TimeSlot, Lead
from mongoengine.queryset.visitor import Q
# from .forms import ContactForm, ProfileForm, AppraisalRequestForm, TestimonialForm
from .forms import ContactForm, ProfileForm, AppraisalRequestForm, TestimonialForm, AppointmentScheduleForm, ScheduleSelectionForm, LeadForm
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
from .models import AppraisalReport, InspectionChecklist, PhotoGallery
from .services.report_generator import ReportGenerator
from django.utils import timezone
from datetime import datetime, timedelta
from django.views.generic import DetailView
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.contrib import messages


logger = logging.getLogger(__name__)




def get_active_content(page_type):
    """Get active content for a specific page type"""
    now = timezone.now()
    
    print(f"\nDEBUG: get_active_content for {page_type}")
    print(f"Current time: {now}")
    
    try:
        content = PageContent.objects(
            page_type=page_type,
            active=True,
            archived=False,
            display_from__lte=now
        ).first()
        
        if content:
            print(f"Found content: {content.title}")
            print(f"Active: {content.active}")
            print(f"Archived: {content.archived}")
            print(f"Display From: {content.display_from}")
            print(f"Display Until: {content.display_until}")
        else:
            print("No content found")
            
        return content
        
    except Exception as e:
        print(f"Error in get_active_content: {str(e)}")
        return None
    
class LeadEditView(View):
    template_name = 'leads/lead_edit.html'

    @method_decorator(login_required)
    def get(self, request, id):
        user = get_auth0_user(request)
        is_admin = (user.get('is_admin') or user.get('/app_metadata', {}).get('is_admin'))
        
        if not is_admin:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('core:home')
            
        try:
            lead = Lead.objects.get(id=id)
            # Split the name field into first and last name
            name_parts = lead.name.split(' ', 1)
            initial_data = {
                'first_name': name_parts[0],
                'last_name': name_parts[1] if len(name_parts) > 1 else '',
                'email': lead.email,
                'phone': lead.phone,
                'property_type': lead.property_type,
                'message': lead.message
            }
            form = LeadForm(initial=initial_data)
            
            context = {
                'form': form,
                'lead': lead,
                'user': user
            }
            return render(request, self.template_name, context)
            
        except Lead.DoesNotExist:
            messages.error(request, 'Lead not found.')
            return redirect('core:lead_list')

    @method_decorator(login_required)
    def post(self, request, id):
        user = get_auth0_user(request)
        is_admin = (user.get('is_admin') or user.get('/app_metadata', {}).get('is_admin'))
        
        if not is_admin:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('core:home')
            
        try:
            lead = Lead.objects.get(id=id)
            form = LeadForm(request.POST)
            
            if form.is_valid():
                # Combine first and last name
                full_name = f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}"
                
                lead.name = full_name
                lead.email = form.cleaned_data['email']
                lead.phone = form.cleaned_data.get('phone', '')
                lead.property_type = form.cleaned_data.get('property_type')
                lead.message = form.cleaned_data.get('message', '')
                lead.updated_at = datetime.now()
                
                lead.save()
                messages.success(request, 'Lead updated successfully!')
                return redirect('core:lead_detail', id=id)
            
            context = {
                'form': form,
                'lead': lead,
                'user': user
            }
            return render(request, self.template_name, context)
            
        except Lead.DoesNotExist:
            messages.error(request, 'Lead not found.')
            return redirect('core:lead_list')    
    
class LeadCreateView(View):
    template_name = 'leads/lead_create.html'

    @method_decorator(login_required)
    def get(self, request):
        user = get_auth0_user(request)
        if not user.get('app_metadata', {}).get('is_admin'):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('core:home')
            
        context = {
            'form': LeadForm(),
            'user': user
        }
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request):
        user = get_auth0_user(request)
        if not user.get('app_metadata', {}).get('is_admin'):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('core:home')
            
        form = LeadForm(request.POST)
        if form.is_valid():
            try:
                lead = Lead(
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data.get('phone', ''),
                    property_type=form.cleaned_data.get('property_type'),
                    message=form.cleaned_data.get('message', '')
                )
                lead.save()
                messages.success(request, 'Lead created successfully!')
                return redirect('core:lead_list')
            except Exception as e:
                messages.error(request, f'Error creating lead: {str(e)}')
        
        context = {
            'form': form,
            'user': user
        }
        return render(request, self.template_name, context)
    
class LeadCreateView(View):
    template_name = 'leads/lead_create.html'

    @method_decorator(login_required)
    def get(self, request):
        user = get_auth0_user(request)
        is_admin = (
            user.get('is_admin') or 
            user.get('/app_metadata', {}).get('is_admin')
        )
        
        if not is_admin:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('core:home')
            
        context = {
            'form': LeadForm(),
            'user': user
        }
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    @method_decorator(login_required)
    def post(self, request):
        print("\n=== Processing Lead Creation POST Request ===")
        user = get_auth0_user(request)
        is_admin = (
            user.get('is_admin') or 
            user.get('/app_metadata', {}).get('is_admin')
        )
        
        if not is_admin:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('core:home')
        
        form = LeadForm(request.POST)
        print("Form Data:", request.POST)
        
        if form.is_valid():
            print("Form is valid")
            try:
                # Combine first and last name
                full_name = f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}"
                
                lead = Lead(
                    name=full_name,
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data.get('phone', ''),
                    property_type=form.cleaned_data.get('property_type'),
                    message=form.cleaned_data.get('message', '')
                )
                
                # Print debug information
                print("Creating lead with data:", {
                    'name': lead.name,
                    'email': lead.email,
                    'phone': lead.phone,
                    'property_type': lead.property_type,
                    'message': lead.message
                })
                
                lead.save()
                print("Lead saved successfully")
                messages.success(request, 'Lead created successfully!')
                return redirect('core:lead_list')
            except Exception as e:
                print(f"Error saving lead: {str(e)}")
                messages.error(request, f'Error creating lead: {str(e)}')
                
                # Additional error information
                import traceback
                print("Full error traceback:")
                print(traceback.format_exc())
        else:
            print("Form errors:", form.errors)
        
        context = {
            'form': form,
            'user': user
        }
        return render(request, self.template_name, context)


class PrivacyPolicyView(TemplateView):
    template_name = 'core/privacy_policy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        return context

class TermsOfServiceView(TemplateView):
    template_name = 'core/terms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        return context

class ScheduleSelectionView(View):
    template_name = 'core/schedule_selection.html'

    @method_decorator(login_required)
    def get(self, request, request_id):
        try:
            appraisal_request = AppraisalRequest.objects.get(request_id=request_id)
            
            # Check if user owns this request
            if appraisal_request.user_id != request.user['sub']:
                messages.error(request, "You don't have permission to schedule this appointment.")
                return redirect('core:dashboard')
            
            form = ScheduleSelectionForm()
            
            context = {
                'form': form,
                'appraisal_request': appraisal_request,
                'user': get_auth0_user(request)
            }
            return render(request, self.template_name, context)
            
        except AppraisalRequest.DoesNotExist:
            messages.error(request, 'Appraisal request not found.')
            return redirect('core:dashboard')

    @method_decorator(login_required)
    def post(self, request, request_id):
        try:
            appraisal_request = AppraisalRequest.objects.get(request_id=request_id)
            form = ScheduleSelectionForm(request.POST)
            
            if form.is_valid():
                # Get the selected date and time slot
                date = form.cleaned_data['appointment_date']
                slot = form.cleaned_data['time_slot']
                
                # Check if slot is available
                existing_slot = TimeSlot.objects(
                    date=date,
                    slot=slot,
                    is_available=True
                ).first()
                
                if not existing_slot:
                    # Create new slot if it doesn't exist
                    existing_slot = TimeSlot(
                        date=date,
                        slot=slot,
                        is_available=True
                    )
                
                # Book the slot
                existing_slot.is_available = False
                existing_slot.appraisal_request = appraisal_request
                existing_slot.save()
                
                # Update appraisal request
                appraisal_request.status = 'scheduled'
                appraisal_request.scheduled_date = date
                appraisal_request.save()
                
                messages.success(request, 'Appointment scheduled successfully!')
                return redirect('core:appraisal_request_detail', request_id=request_id)
            
            context = {
                'form': form,
                'appraisal_request': appraisal_request,
                'user': get_auth0_user(request)
            }
            return render(request, self.template_name, context)
            
        except AppraisalRequest.DoesNotExist:
            messages.error(request, 'Appraisal request not found.')
            return redirect('core:dashboard')


class AppraisalReportView(LoginRequiredMixin, View):
    template_name = 'core/reports/appraisal_report.html'

    def get(self, request, report_id):
        try:
            report = get_object_or_404(AppraisalReport, id=report_id)
            inspection = get_object_or_404(InspectionChecklist, appraisal_report=report)
            gallery = PhotoGallery.objects.filter(appraisal_report=report).first()

            context = {
                'user': get_auth0_user(request),
                'report': report,
                'inspection': inspection,
                'gallery': gallery
            }
            return render(request, self.template_name, context)
        except Exception as e:
            messages.error(request, f"Error loading report: {str(e)}")
            return redirect('core:dashboard')
        

class AppraisalListView(LoginRequiredMixin, View):
    template_name = 'core/appraisal_list.html'

    def get(self, request):
        try:
            reports = AppraisalReport.objects.order_by('-created_at')
            context = {
                'user': get_auth0_user(request),
                'reports': reports
            }
            return render(request, self.template_name, context)
        except Exception as e:
            messages.error(request, f"Error loading reports: {str(e)}")
            return redirect('core:dashboard')

class AppraisalRequestView(FormView):
    template_name = 'core/appraisal_request.html'
    form_class = AppraisalRequestForm
    success_url = '/dashboard/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['min_date'] = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        context['max_date'] = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        context['user'] = get_auth0_user(self.request)
        return context

    def form_valid(self, form):
        user = get_auth0_user(self.request)
    
        try:
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
                notes=form.cleaned_data.get('notes', ''),
                status='pending'
            )

            # Handle appointment scheduling
            appointment_date = form.cleaned_data.get('appointment_date')
            time_slot = form.cleaned_data.get('time_slot')
            
            if appointment_date and time_slot:
                appraisal_request.status = 'scheduled'
                # Store the appointment information
                appraisal_request.scheduled_date = appointment_date
                appraisal_request.time_slot = time_slot
                
            appraisal_request.save()
            messages.success(self.request, 'Your appraisal request has been submitted successfully!')
            return super().form_valid(form)

        except Exception as e:
            logger.error(f"Error creating appraisal request: {str(e)}")
            messages.error(
                self.request,
                'There was an error processing your request. Please try again or contact support.'
            )
            return self.form_invalid(form)
    

# Keep only these existing views for now
class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        
        # Get active content for the home page
        now = datetime.now()
        content = PageContent.objects.filter(
            page_type='home',
            active=True,
            archived=False
        )
        
        # Debug prints
        print("\n=== Debug: Home Page Content ===")
        print(f"Number of content items: {content.count()}")
        for c in content:
            print(f"ID: {c.id}")
            print(f"Title: {c.title}")
            print(f"Active: {c.active}")
            print(f"Display From: {c.display_from}")
            print(f"Display Until: {c.display_until}")
            print("Content preview:", c.content[:100] if c.content else "No content")
        print("============================\n")
        
        context['page_content'] = content.first()
        context['debug'] = True  # Add this to show debug info in template
        
        return context
    
# class AboutView(TemplateView):
#     template_name = 'core/about.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['user'] = get_auth0_user(self.request)
        
#         # Get active content for the about page
#         now = datetime.now()
#         context['page_content'] = PageContent.objects.filter(
#             page_type='about',
#             active=True,
#             archived=False
#         ).filter(
#             display_from__lte=now
#         ).filter(
#             display_until__gt=now
#         ).first() or None
        
#         return context

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


class ContentDebugView(View):
    @method_decorator(login_required)
    def get(self, request, page_type):
        # Get user and verify admin status
        user = get_auth0_user(request)
        is_admin = user.get('app_metadata', {}).get('is_admin', False)
        
        if not is_admin:
            return HttpResponseForbidden()
            
        now = timezone.now()
        all_content = PageContent.objects(page_type=page_type)
        
        debug_info = {
            'current_time': now.isoformat(),
            'page_type': page_type,
            'total_content_count': all_content.count(),
            'contents': [{
                'id': str(content.id),
                'title': content.title,
                'active': content.active,
                'archived': content.archived,
                'display_from': content.display_from.isoformat() if content.display_from else None,
                'display_until': content.display_until.isoformat() if content.display_until else None,
                'status': 'Current' if (
                    content.active and 
                    not content.archived and 
                    content.display_from <= now and 
                    (not content.display_until or content.display_until > now)
                ) else 'Inactive',
                'page_type': content.page_type
            } for content in all_content]
        }
        
        return JsonResponse(debug_info)

class TermsOfServiceView(TemplateView):
    template_name = 'core/terms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        print("\n=== Terms of Service View Debug ===")
        # Try both possible page type values
        content = get_active_content('terms-of-service') or get_active_content('terms')
        print(f"Content found: {bool(content)}")
        context['page_content'] = content
        print("===========================\n")
        return context
    
    
# class ServicesView(TemplateView):
#     template_name = 'core/services.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['user'] = get_auth0_user(self.request)
        
#         # Get active content for the services page
#         now = datetime.now()
#         context['page_content'] = PageContent.objects.filter(
#             page_type='services',
#             active=True,
#             archived=False
#         ).filter(
#             display_from__lte=now
#         ).filter(
#             display_until__gt=now
#         ).first() or None
        
#         return context
    
#     template_name = 'core/services.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['user'] = get_auth0_user(self.request)
        
#         # Get active content for the services page
#         now = datetime.now()
#         context['page_content'] = PageContent.objects.filter(
#             page_type='services',
#             active=True,
#             archived=False
#         ).filter(
#             display_from__lte=now
#         ).filter(
#             display_until__gt=now
#         ).first() or None
        
#         return context
    
class faqServicesView(TemplateView):
    template_name = 'core/faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        
        # Get active content for the services page
        now = datetime.now()
        context['page_content'] = PageContent.objects.filter(
            page_type='faq',
            active=True,
            archived=False
        ).filter(
            display_from__lte=now
        ).filter(
            display_until__gt=now
        ).first() or None
        
        return context
    
    template_name = 'core/faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        
        # Get active content for the services page
        now = datetime.now()
        context['page_content'] = PageContent.objects.filter(
            page_type='faq',
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
        # Use the new method to get visible content
        visible_content = PageContent.get_visible_content('about').first()
        context['page_content'] = visible_content
        return context

class ServicesView(TemplateView):
    template_name = 'core/services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        context['services'] = [
            {
                'title': 'Residential Appraisals',
                'description': 'Comprehensive valuation for homes and residential properties.',
                'icon': 'bi-house'
            },
            {
                'title': 'Commercial Appraisals',
                'description': 'Expert valuation services for commercial real estate.',
                'icon': 'bi-building'
            },
            {
                'title': 'Property Consultations',
                'description': 'Professional guidance on property values and market trends.',
                'icon': 'bi-chat-square-text'
            }
        ]
        return context
    
class FAQView(TemplateView):
    template_name = 'core/faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        # Use the new method to get visible content
        visible_content = PageContent.get_visible_content('faq').first()
        context['page_content'] = visible_content
        return context      
    
class TermsOfServiceView(TemplateView):
    template_name = 'core/terms_of_service.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        # Use the new method to get visible content
        visible_content = PageContent.get_visible_content('terms').first()
        context['page_content'] = visible_content
        return context 


    
class AppraisalListView(LoginRequiredMixin, ListView):
    template_name = 'core/appraisal_list.html'
    context_object_name = 'reports'
    
    def get_queryset(self):
        return AppraisalReport.objects.filter(
            appraiser=self.request.user.name
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        return context

class ProfileView(TemplateView):
    template_name = 'core/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_auth0_user(self.request)
        
        print("\n=== DEBUG USER INFO ===")
        print("User object:", user)
        print("Is admin check paths:")
        print("- Direct is_admin:", user.get('is_admin'))
        print("- app_metadata:", user.get('app_metadata'))
        print("- /app_metadata:", user.get('/app_metadata'))
        print("- user_metadata:", user.get('user_metadata'))
        print("- /user_metadata:", user.get('/user_metadata'))
        print("======================\n")

        # Simplified admin check
        is_admin = bool(
            user.get('is_admin') or
            (user.get('app_metadata', {}) or {}).get('is_admin') or
            (user.get('/app_metadata', {}) or {}).get('is_admin') or
            (user.get('user_metadata', {}) or {}).get('is_admin') or
            (user.get('/user_metadata', {}) or {}).get('is_admin')
        )

        context['user'] = user
        context['debug_info'] = {
            'is_admin': is_admin,
            'app_metadata': user.get('app_metadata', {}),
            'user_metadata': user.get('user_metadata', {}),
            'raw_user': user
        }
        
        return context
    
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
    
# class DashboardView(TemplateView):
#     template_name = 'core/dashboard.html'

#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user = get_auth0_user(self.request)
#         profile = UserProfile.objects(user_id=user['sub']).first()

#         # For now, we'll use placeholder data
#         # Later, we'll replace these with real data from the database
#         context.update({
#             'user': user,
#             'profile': profile,
#             'statistics': {
#                 'total_requests': 0,
#                 'pending_requests': 0,
#                 'completed_requests': 0,
#                 'in_progress': 0
#             },
#             'recent_requests': [],
#             'upcoming_appointments': [],
#             'notifications': [
#                 {
#                     'type': 'info',
#                     'message': 'Welcome to your dashboard! Start by creating your first appraisal request.',
#                     'date': datetime.now()
#                 }
#             ]
#         })
#         return context
    

        
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
        return super().dispatch(self, *args, **kwargs)

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

class AppraisalRequestView(FormView):
    template_name = 'core/appraisal_request.html'
    form_class = AppraisalRequestForm
    success_url = '/dashboard/'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        """Pre-populate form with user profile data if available"""
        user = get_auth0_user(self.request)
        profile = UserProfile.objects(user_id=user['sub']).first()
        
        initial = {}
        if profile:
            initial.update({
                'contact_name': f"{profile.first_name} {profile.last_name}",
                'contact_phone': profile.phone,
                'contact_email': profile.email,
            })
        return initial

    def generate_request_id(self):
        current_year = datetime.now().year
        year_str = str(current_year)[2:]  # Get last 2 digits of year
        
        # Get start and end of current year
        year_start = datetime(current_year, 1, 1)
        year_end = datetime(current_year + 1, 1, 1)
        
        # Count requests between start and end of year
        count = AppraisalRequest.objects(
            created_at__gte=year_start,
            created_at__lt=year_end
        ).count() + 1
        
        return f'APR{year_str}-{count:04d}'  # Format: APR23-0001


    def form_valid(self, form):
        user = get_auth0_user(self.request)
        
        try:
            now = timezone.now()
            request_id = self.generate_request_id()
            
            appraisal_request = AppraisalRequest(
                request_id=request_id,
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
                created_at=now
            )

            # Handle appointment scheduling if provided
            appointment_date = form.cleaned_data.get('appointment_date')
            time_slot = form.cleaned_data.get('time_slot')
            
            if appointment_date and time_slot:
                appraisal_request.status = 'scheduled'
                appraisal_request.scheduled_date = appointment_date
                appraisal_request.time_slot = time_slot

            # Save the request
            appraisal_request.save()

            # Send email notifications
            try:
                # Email to admin
                admin_context = {
                    'request': appraisal_request,
                    'user': user,
                }
                admin_email_body = render_to_string('core/emails/new_appraisal_request_admin.txt', admin_context)
                send_mail(
                    subject=f'New Appraisal Request #{appraisal_request.request_id}',
                    message=admin_email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=True,
                )
                
                # Confirmation email to user
                user_context = {
                    'request': appraisal_request,
                    'user': user,
                }
                user_email_body = render_to_string('core/emails/appraisal_request_confirmation.txt', user_context)
                send_mail(
                    subject=f'Appraisal Request Confirmation #{appraisal_request.request_id}',
                    message=user_email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.get('email')],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"Error sending appraisal request emails: {str(e)}")
                # Continue processing even if email fails

            # Success message
            messages.success(
                self.request,
                f'Your appraisal request #{appraisal_request.request_id} has been submitted successfully! '
                'We will contact you shortly to confirm the details.'
            )
            
            # Log the request
            logger.info(
                f"New appraisal request created - ID: {appraisal_request.request_id}, "
                f"User: {user['sub']}, Property: {appraisal_request.property_address}"
            )
            
            return super().form_valid(form)

        except Exception as e:
            logger.error(f"Error creating appraisal request: {str(e)}")
            messages.error(
                self.request,
                'There was an error processing your request. Please try again or contact support.'
            )
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        context['min_date'] = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        context['max_date'] = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        
        # Get user profile
        context['profile'] = UserProfile.objects(user_id=context['user']['sub']).first()
        
        # Get user's recent requests
        context['recent_requests'] = AppraisalRequest.objects(
            user_id=context['user']['sub']
        ).order_by('-created_at')[:3]
        
        return context  

class AppraisalRequestDetailView(View):
    template_name = 'core/appraisal_request_detail.html'

    @method_decorator(login_required)
    def get(self, request, request_id):
        user = get_auth0_user(request)
        try:
            # Get the appraisal request
            appraisal_request = AppraisalRequest.objects.get(request_id=request_id)
            
            # Check if user owns this request or is admin
            if appraisal_request.user_id != user['sub'] and not user.get('app_metadata', {}).get('is_admin'):
                messages.error(request, "You don't have permission to view this request.")
                return redirect('core:dashboard')
            
            # Get associated appointment if it exists
            appointment = Appointment.objects(appraisal_request=appraisal_request).first()
            
            # Debug output
            print(f"Debug: Request ID: {request_id}")
            print(f"Debug: Has appointment: {bool(appointment)}")
            print(f"Debug: Request status: {appraisal_request.status}")
            
            context = {
                'user': user,
                'request': appraisal_request,
                'appointment': appointment
            }
            
            return render(request, self.template_name, context)
            
        except AppraisalRequest.DoesNotExist:
            messages.error(request, 'Appraisal request not found.')
            return redirect('core:dashboard')


# class AppraisalRequestDetailView(View):
#     template_name = 'core/appraisal_request_detail.html'

#     @method_decorator(login_required)
#     def get(self, request, request_id):
#         user = get_auth0_user(request)
#         try:
#             appraisal_request = AppraisalRequest.objects.get(request_id=request_id)
#             context = {
#                 'user': user,  # Add user to context
#                 'request': appraisal_request,
#                 'profile': UserProfile.objects(user_id=user['sub']).first()  # Add profile if needed
#             }
#             return render(request, self.template_name, context)
#         except AppraisalRequest.DoesNotExist:
#             messages.error(request, 'Appraisal request not found.')
#             return redirect('core:dashboard')    

# class AppraisalRequestDetailView(View):
#     template_name = 'core/appraisal_request_detail.html'

#     @method_decorator(login_required)
#     def get(self, request, request_id):
#         try:
#             appraisal_request = AppraisalRequest.objects.get(request_id=request_id)
#             context = {
#                 'request': appraisal_request
#             }
#             return render(request, self.template_name, context)
#         except AppraisalRequest.DoesNotExist:
#             messages.error(request, 'Appraisal request not found.')
#             return redirect('core:dashboard')

# class AppraisalRequestDetailView(View):
#     template_name = 'core/appraisal_request_detail.html'

#     @method_decorator(login_required)
#     def get(self, request, request_id):
#         user = get_auth0_user(request)
        
#         try:
#             appraisal_request = AppraisalRequest.objects.get(request_id=request_id)
            
#             # Check if user owns this request or is admin
#             if appraisal_request.user_id != user['sub'] and not user.get('app_metadata', {}).get('is_admin'):
#                 messages.error(request, "You don't have permission to view this request.")
#                 return redirect('core:dashboard')
            
#             context = {
#                 'user': user,
#                 'request': appraisal_request,
#                 'status_history': appraisal_request.get_status_history() if hasattr(appraisal_request, 'get_status_history') else None,
#             }
            
#             return render(request, self.template_name, context)
            
#         except AppraisalRequest.DoesNotExist:
#             messages.error(request, 'Appraisal request not found.')
#             return redirect('core:dashboard')


class AppointmentScheduleView(View):
    template_name = 'core/appointment_schedule.html'

    @method_decorator(login_required)
    def get(self, request, request_id):
        user = get_auth0_user(request)
        try:
            appraisal_request = AppraisalRequest.objects.get(request_id=request_id)
            
            # Check if user owns this request or is admin
            if appraisal_request.user_id != user['sub'] and not user.get('app_metadata', {}).get('is_admin'):
                messages.error(request, "You don't have permission to schedule appointments for this request.")
                return redirect('core:dashboard')
            
            # Check if appointment already exists
            existing_appointment = Appointment.objects(appraisal_request=appraisal_request).first()
            if existing_appointment:
                messages.warning(request, "An appointment already exists for this request.")
                return redirect('core:appraisal_request_detail', request_id=request_id)
            
            form = AppointmentScheduleForm()
            context = {
                'user': user,
                'appraisal_request': appraisal_request,
                'form': form
            }
            return render(request, self.template_name, context)
            
        except AppraisalRequest.DoesNotExist:
            messages.error(request, 'Appraisal request not found.')
            return redirect('core:dashboard')

    @method_decorator(login_required)
    def post(self, request, request_id):
        try:
            appraisal_request = AppraisalRequest.objects.get(request_id=request_id)
            form = AppointmentScheduleForm(request.POST)
            
            if form.is_valid():
                appointment = Appointment(
                    appraisal_request=appraisal_request,
                    scheduled_date=form.cleaned_data['date'],
                    notes=form.cleaned_data.get('notes', '')
                )
                appointment.save()
                
                # Update appraisal request status
                appraisal_request.status = 'scheduled'
                appraisal_request.save()
                
                messages.success(request, 'Appointment scheduled successfully!')
                return redirect('core:appraisal_request_detail', request_id=request_id)
            
            context = {
                'user': get_auth0_user(request),
                'appraisal_request': appraisal_request,
                'form': form
            }
            return render(request, self.template_name, context)
            
        except AppraisalRequest.DoesNotExist:
            messages.error(request, 'Appraisal request not found.')
            return redirect('core:dashboard')
        
class AppointmentRescheduleView(View):
    @method_decorator(login_required)
    def post(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Check permissions
            appraisal_request = appointment.appraisal_request
            user = get_auth0_user(request)
            if appraisal_request.user_id != user['sub'] and not user.get('app_metadata', {}).get('is_admin'):
                messages.error(request, "You don't have permission to reschedule this appointment.")
                return redirect('core:appointments')
            
            # Get and validate new date
            try:
                new_date = datetime.strptime(request.POST['new_date'], '%Y-%m-%dT%H:%M')
                new_date = timezone.make_aware(new_date)
                
                # Validate business hours
                if new_date.hour < 9 or new_date.hour >= 17:
                    messages.error(request, "Appointments must be scheduled between 9 AM and 5 PM")
                    return redirect('core:appointments')
                
                # Validate weekends
                if new_date.weekday() >= 5:
                    messages.error(request, "Appointments cannot be scheduled on weekends")
                    return redirect('core:appointments')
                
                # Validate minimum notice
                if new_date < timezone.now() + timedelta(days=1):
                    messages.error(request, "Appointments must be rescheduled at least 24 hours in advance")
                    return redirect('core:appointments')
                
            except (ValueError, TypeError):
                messages.error(request, "Invalid date format")
                return redirect('core:appointments')
            
            # Store old date for notification
            old_date = appointment.scheduled_date
            
            # Update appointment
            appointment.scheduled_date = new_date
            appointment.status = 'rescheduled'
            appointment.notes = f"{appointment.notes}\n\nRescheduled from {old_date.strftime('%Y-%m-%d %H:%M')} to {new_date.strftime('%Y-%m-%d %H:%M')}\nReason: {request.POST.get('reason', 'No reason provided')}"
            appointment.save()
            
            messages.success(request, 'Appointment rescheduled successfully!')
            
        except Appointment.DoesNotExist:
            messages.error(request, "Appointment not found.")
            
        return redirect('core:appointments')        

# class AppointmentScheduleView(View):
#     template_name = 'core/appointment_schedule.html'

#     @method_decorator(login_required)
#     def get(self, request, request_id):
#         user = get_auth0_user(request)
#         try:
#             appraisal_request = AppraisalRequest.objects.get(request_id=request_id)
#             form = AppointmentScheduleForm()
            
#             context = {
#                 'user': user,
#                 'appraisal_request': appraisal_request,
#                 'form': form
#             }
#             return render(request, self.template_name, context)
#         except AppraisalRequest.DoesNotExist:
#             messages.error(request, 'Appraisal request not found.')
#             return redirect('core:dashboard')

#     @method_decorator(login_required)
#     def post(self, request, request_id):
#         form = AppointmentScheduleForm(request.POST)
#         if form.is_valid():
#             try:
#                 appraisal_request = AppraisalRequest.objects.get(request_id=request_id)
                
#                 appointment = Appointment(
#                     appraisal_request=appraisal_request,
#                     scheduled_date=form.cleaned_data['date'],
#                     notes=form.cleaned_data.get('notes', '')
#                 )
#                 appointment.save()

#                 messages.success(request, 'Appointment scheduled successfully!')
#                 return redirect('core:appraisal_request_detail', request_id=request_id)
                
#             except AppraisalRequest.DoesNotExist:
#                 messages.error(request, 'Appraisal request not found.')
#                 return redirect('core:dashboard')
        
#         context = {
#             'user': get_auth0_user(request),
#             'form': form,
#             'appraisal_request': AppraisalRequest.objects.get(request_id=request_id)
#         }
#         return render(request, self.template_name, context)
    
# class AppointmentListView(ListView):
#     template_name = 'core/appointments.html'
#     context_object_name = 'appointments'

#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)

#     def get_queryset(self):
#         user = get_auth0_user(self.request)
#         requests = AppraisalRequest.objects(user_id=user['sub'])
#         return Appointment.objects(appraisal_request__in=requests).order_by('scheduled_date')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['user'] = get_auth0_user(self.request)
#         return context    
    

class AppointmentListView(ListView):
    template_name = 'core/appointments.html'
    context_object_name = 'appointments'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = get_auth0_user(self.request)
        # Get all appraisal requests for this user
        requests = AppraisalRequest.objects(user_id=user['sub'])
        # Get all appointments for these requests, sorted by date
        return Appointment.objects(appraisal_request__in=requests).order_by('-scheduled_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        now = datetime.now()
        
        appointments = self.get_queryset()
        context['upcoming_appointments'] = appointments.filter(scheduled_date__gte=now)
        context['past_appointments'] = appointments.filter(scheduled_date__lt=now)
        
        return context
    
class PrivacyPolicyView(TemplateView):
    template_name = 'core/privacy_policy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        return context



    
def test_openai(request):
    try:
        communicator = AICommunicator()
        response = communicator.get_response("Hello, are you working?")
        return JsonResponse({
            'status': 'success',
            'response': response
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        })

class ChatView(View):
    def post(self, request):
        try:
            logger.debug("Received chat request")
            data = json.loads(request.body)
            user_message = data.get('message')
            
            logger.debug(f"User message: {user_message}")

            # Get or create session ID
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key

            # Store chat history in session
            chat_history = request.session.get('chat_history', [])
            
            # Initialize communicator with existing conversation
            communicator = AICommunicator()
            response = communicator.get_response(
                user_message, 
                session_id=session_id
            )
            
            # Update chat history
            chat_history.append({
                'user_message': user_message,
                'bot_response': response
            })
            request.session['chat_history'] = chat_history[-10:]  # Keep last 10 messages
            
            logger.debug(f"AI response: {response}")
            
            return JsonResponse({
                'status': 'success',
                'response': response
            })

        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            logger.error(traceback.format_exc())
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

class LeadListView(View):
    template_name = 'leads/lead_list.html'

    @method_decorator(login_required)
    def get(self, request):
        user = get_auth0_user(request)
        
        # Debug prints for admin check
        print("\n=== Debug User Info ===")
        print(f"User: {user}")
        print(f"App metadata: {user.get('/app_metadata', {})}")
        
        # Check admin status
        is_admin = (
            user.get('is_admin') or 
            user.get('/app_metadata', {}).get('is_admin') or 
            user.get('app_metadata', {}).get('is_admin')
        )
        
        if not is_admin:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('core:home')
        
        try:
            leads = Lead.objects.all().order_by('-created_at')
            print(f"Found {leads.count()} leads")
        except Exception as e:
            print(f"Error fetching leads: {e}")
            leads = []
        
        context = {
            'user': user,
            'leads': leads
        }
        return render(request, self.template_name, context)

class LeadDetailView(DetailView):
    template_name = 'leads/lead_detail.html'
    context_object_name = 'lead'
    
    def get_object(self):
        # Convert the string ID to ObjectId and get the lead
        lead_id = self.kwargs.get('id')
        print(f"Looking for lead with ID: {lead_id}")  # Debug print
        return Lead.objects.get(id=lead_id)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        return context


class LeadDeleteView(DeleteView):
    model = Lead
    success_url = reverse_lazy('core:lead_list')
    
    def get_object(self):
        return Lead.objects.get(id=self.kwargs['id'])
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Lead deleted successfully.')
        return super().delete(request, *args, **kwargs)

class FAQView(TemplateView):
    template_name = 'core/faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        context['faqs'] = [
            {
                'question': 'What is an appraisal?',
                'answer': 'An appraisal is a professional opinion of value.'
            },
            {
                'question': 'How long does an appraisal take?',
                'answer': 'Typically 3-5 business days after the property inspection.'
            },
            {
                'question': 'What documents do I need?',
                'answer': 'Property deed, recent tax assessments, and any recent improvements documentation.'
            }
        ]
        return context
    

class LeadStatusUpdateView(View):
    @method_decorator(login_required)
    def post(self, request, id):
        try:
            lead = Lead.objects.get(id=id)
            new_status = request.POST.get('status')
            
            if new_status and new_status in [status[0] for status in lead.STATUS_CHOICES]:
                lead.status = new_status
                lead.save()
                messages.success(request, 'Lead status updated successfully.')
            else:
                messages.error(request, 'Invalid status value provided.')
                
            return redirect('core:lead_detail', id=id)
            
        except Lead.DoesNotExist:
            messages.error(request, 'Lead not found.')
            return redirect('core:lead_list')