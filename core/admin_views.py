# File: core/admin_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import View, ListView
from utils.auth import login_required
from content_management.models import PageContent, Theme
from profiles.models import Profile, Testimonial
from datetime import datetime, timedelta

class AdminDashboardView(View):
    @login_required
    def get(self, request):
        # Get statistics
        total_users = Profile.objects.count()
        total_testimonials = Testimonial.objects.count()
        pending_testimonials = Testimonial.objects.filter(approved=False).count()
        total_content = PageContent.objects.count()
        
        # Get recent content
        recent_content = PageContent.objects.order_by('-updated_at')[:5]
        
        # Get pending testimonials
        pending_testimonials_list = Testimonial.objects.filter(
            approved=False
        ).order_by('-created_at')[:5]
        
        # Get content statistics by page type
        content_by_page = {
            'home': PageContent.objects.filter(page_type='home').count(),
            'about': PageContent.objects.filter(page_type='about').count(),
            'services': PageContent.objects.filter(page_type='services').count()
        }
        
        # Get active vs inactive content
        active_content = PageContent.objects.filter(active=True).count()
        inactive_content = PageContent.objects.filter(active=False).count()
        
        context = {
            'total_users': total_users,
            'total_testimonials': total_testimonials,
            'pending_testimonials': pending_testimonials,
            'total_content': total_content,
            'recent_content': recent_content,
            'pending_testimonials_list': pending_testimonials_list,
            'content_by_page': content_by_page,
            'active_content': active_content,
            'inactive_content': inactive_content,
        }
        
        return render(request, 'admin/dashboard.html', context)

class TestimonialManagementView(ListView):
    template_name = 'admin/testimonial_management.html'
    context_object_name = 'testimonials'
    paginate_by = 10

    def get_queryset(self):
        queryset = Testimonial.objects.all().order_by('-created_at')
        status = self.request.GET.get('status')
        if status == 'pending':
            queryset = queryset.filter(approved=False)
        elif status == 'approved':
            queryset = queryset.filter(approved=True)
        return queryset

    def post(self, request):
        action = request.POST.get('action')
        testimonial_id = request.POST.get('testimonial_id')
        
        if not testimonial_id:
            messages.error(request, 'Invalid testimonial ID')
            return redirect('admin:testimonial_management')
            
        testimonial = Testimonial.objects.get(id=testimonial_id)
        
        if action == 'approve':
            testimonial.approved = True
            testimonial.save()
            messages.success(request, 'Testimonial approved successfully')
        elif action == 'reject':
            testimonial.delete()
            messages.success(request, 'Testimonial rejected and deleted')
            
        return redirect('admin:testimonial_management')

class ContentAnalyticsView(View):
    @login_required
    def get(self, request):
        # Get content creation trends
        today = datetime.now()
        last_month = today - timedelta(days=30)
        
        content_trend = PageContent.objects\
            .filter(created_at__gte=last_month)\
            .order_by('created_at')
        
        # Get content by theme
        themes = Theme.objects.all()
        content_by_theme = {}
        for theme in themes:
            content_by_theme[theme.name] = PageContent.objects.filter(theme=theme).count()
        
        # Get active content schedule
        scheduled_content = PageContent.objects\
            .filter(display_from__gte=today)\
            .order_by('display_from')[:10]
        
        context = {
            'content_trend': content_trend,
            'content_by_theme': content_by_theme,
            'scheduled_content': scheduled_content,
        }
        
        return render(request, 'admin/content_analytics.html', context)

class UserManagementView(ListView):
    template_name = 'admin/user_management.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        return Profile.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = Profile.objects.count()
        context['active_users'] = Profile.objects.filter(
            last_login__gte=datetime.now() - timedelta(days=30)
        ).count()
        return context