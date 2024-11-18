# File: core/admin_urls.py

from django.urls import path
from . import admin_views

app_name = 'admin'

urlpatterns = [
    path('dashboard/', admin_views.AdminDashboardView.as_view(), name='dashboard'),
    path('testimonials/', admin_views.TestimonialManagementView.as_view(), name='testimonial_management'),
    path('analytics/', admin_views.ContentAnalyticsView.as_view(), name='content_analytics'),
    path('users/', admin_views.UserManagementView.as_view(), name='user_management'),
    path('admin/testimonials/', admin_views.AdminTestimonialsView.as_view(), name='admin_testimonials'),
    path('admin/testimonials/approve/<str:testimonial_id>/', admin_views.AdminTestimonialApproveView.as_view(), name='admin_testimonial_approve'),
    path('admin/testimonials/reject/<str:testimonial_id>/', admin_views.AdminTestimonialRejectView.as_view(), name='admin_testimonial_reject'),
]