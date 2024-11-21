# File: core/admin_views.py
# Location: C:\git\_clapri\core\admin_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import View, ListView, TemplateView
from django.utils.decorators import method_decorator
from utils.auth import login_required, get_auth0_user
from .models import AppraisalRequest, Profile, Testimonial
from datetime import datetime, timedelta

class AdminDashboardView(TemplateView):
    template_name = 'core/admin/dashboard.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Verify admin status
        user = get_auth0_user(self.request)
        if not user.get('app_metadata', {}).get('is_admin', False):
            messages.error(self.request, "You don't have permission to access the admin dashboard.")
            return redirect('core:home')
        return super().dispatch(*args, **kwargs)

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
        
        # Get recent users
        context['recent_users'] = Profile.objects.order_by('-created_at')[:5]
        
        # Monthly trends (last 6 months)
        six_months_ago = today - timedelta(days=180)
        monthly_requests = AppraisalRequest.objects.filter(
            created_at__gte=six_months_ago
        ).order_by('-created_at')
        
        # Process monthly trends
        monthly_stats = {}
        for request in monthly_requests:
            month_key = request.created_at.strftime('%Y-%m')
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {
                    'count': 0,
                    'month_name': request.created_at.strftime('%b %Y')
                }
            monthly_stats[month_key]['count'] += 1
        
        context['monthly_trends'] = [
            {
                'month': stats['month_name'],
                'count': stats['count']
            }
            for month, stats in sorted(monthly_stats.items(), reverse=True)[:6]
        ]
        
        # Add user to context
        context['user'] = user
        
        return context

class AdminTestimonialsView(ListView):
    template_name = 'core/admin/testimonials.html'
    context_object_name = 'testimonials'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Verify admin status
        user = get_auth0_user(self.request)
        if not user.get('app_metadata', {}).get('is_admin', False):
            messages.error(self.request, "You don't have permission to access this page.")
            return redirect('core:home')
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return Testimonial.objects.filter(is_approved=False).order_by('-created_at')

class AdminTestimonialApproveView(View):
    @method_decorator(login_required)
    def post(self, request, testimonial_id):
        # Verify admin status
        user = get_auth0_user(request)
        if not user.get('app_metadata', {}).get('is_admin', False):
            messages.error(request, "You don't have permission to perform this action.")
            return redirect('core:home')
        
        testimonial = get_object_or_404(Testimonial, id=testimonial_id)
        testimonial.is_approved = True
        testimonial.save()
        
        messages.success(request, "Testimonial approved successfully.")
        return redirect('core:admin_testimonials')

class AdminTestimonialRejectView(View):
    @method_decorator(login_required)
    def post(self, request, testimonial_id):
        # Verify admin status
        user = get_auth0_user(request)
        if not user.get('app_metadata', {}).get('is_admin', False):
            messages.error(request, "You don't have permission to perform this action.")
            return redirect('core:home')
        
        testimonial = get_object_or_404(Testimonial, id=testimonial_id)
        testimonial.delete()
        
        messages.success(request, "Testimonial rejected and deleted.")
        return redirect('core:admin_testimonials')