# File: core/admin_urls.py

from django.urls import path
from . import admin_views

app_name = 'admin'

urlpatterns = [
    path('dashboard/', admin_views.AdminDashboardView.as_view(), name='dashboard'),
    path('testimonials/', admin_views.TestimonialManagementView.as_view(), name='testimonial_management'),
    path('analytics/', admin_views.ContentAnalyticsView.as_view(), name='content_analytics'),
    path('users/', admin_views.UserManagementView.as_view(), name='user_management'),
]