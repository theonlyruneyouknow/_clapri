# File: core/admin_views.py
# Location: C:\git\_clapri\core\admin_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import View, ListView, TemplateView
from django.utils.decorators import method_decorator
from utils.auth import login_required, get_auth0_user
from .models import AppraisalRequest, Testimonial
from datetime import datetime, timedelta
import logging
from mongoengine.errors import DoesNotExist

logger = logging.getLogger(__name__)

def is_admin(user):
    """Helper function to check if user has admin privileges"""
    return any([
        user.get('is_admin'),
        user.get('/app_metadata', {}).get('is_admin'),
        user.get('app_metadata', {}).get('is_admin'),
        user.get('/user_metadata', {}).get('is_admin'),
        user.get('user_metadata', {}).get('is_admin')
    ])

class AdminDashboardView(TemplateView):
    template_name = 'core/admin/dashboard.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = get_auth0_user(request)
        logger.debug(f"User data in admin view: {user}")
        
        if not is_admin(user):
            messages.error(request, "You don't have permission to access the admin dashboard.")
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_auth0_user(self.request)
        
        # Get basic statistics
        context['statistics'] = {
            'total_requests': AppraisalRequest.objects.count(),
            'pending_requests': AppraisalRequest.objects.filter(status='pending').count(),
            'in_progress': AppraisalRequest.objects.filter(status='in_progress').count(),
            'completed_requests': AppraisalRequest.objects.filter(status='completed').count(),
        }
        
        # Get recent appraisal requests
        context['recent_requests'] = AppraisalRequest.objects.order_by('-created_at')[:5]
        
        # Get upcoming appointments
        today = datetime.now()
        context['upcoming_appointments'] = AppraisalRequest.objects.filter(
            status='scheduled',
            scheduled_date__gte=today
        ).order_by('scheduled_date')[:5]
        
        # Get pending testimonials
        context['pending_testimonials'] = Testimonial.objects.filter(
            is_approved=False
        ).order_by('-created_at')[:5]
        
        # Add user to context
        context['user'] = user
        
        return context

class AdminTestimonialsView(TemplateView):
    template_name = 'core/admin/testimonials.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = get_auth0_user(request)
        
        if not is_admin(user):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add user to context for the navigation
        context['user'] = get_auth0_user(self.request)
        # Add testimonials to context
        context['testimonials'] = Testimonial.objects.filter(is_approved=False).order_by('-created_at')
        return context

class AdminTestimonialApproveView(View):
    @method_decorator(login_required)
    def post(self, request, testimonial_id):
        user = get_auth0_user(request)
        if not is_admin(user):
            messages.error(request, "You don't have permission to perform this action.")
            return redirect('core:home')
        
        try:
            testimonial = Testimonial.objects.get(id=testimonial_id)
            testimonial.is_approved = True
            testimonial.save()
            messages.success(request, "Testimonial approved successfully.")
        except DoesNotExist:
            messages.error(request, "Testimonial not found.")
        
        return redirect('core:admin_testimonials')

class AdminTestimonialRejectView(View):
    @method_decorator(login_required)
    def post(self, request, testimonial_id):
        user = get_auth0_user(request)
        if not is_admin(user):
            messages.error(request, "You don't have permission to perform this action.")
            return redirect('core:home')
        
        try:
            testimonial = Testimonial.objects.get(id=testimonial_id)
            testimonial.delete()
            messages.success(request, "Testimonial rejected and deleted.")
        except DoesNotExist:
            messages.error(request, "Testimonial not found.")
        
        return redirect('core:admin_testimonials')