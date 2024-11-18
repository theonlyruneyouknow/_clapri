# File: core/urls.py
# Location: C:\git\_clapri\core\urls.py

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),  # Add this line
    path('appraisal/request/', views.AppraisalRequestView.as_view(), name='appraisal_request'),
    path('testimonials/', views.TestimonialsView.as_view(), name='testimonials'),
    path('testimonials/add/', views.TestimonialCreateView.as_view(), name='testimonial_add'),
    path('testimonials/edit/<str:testimonial_id>/', views.TestimonialEditView.as_view(), name='testimonial_edit'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('callback/', views.callback, name='callback'),
# Admin URLs
    path('admin/testimonials/', views.AdminTestimonialsView.as_view(), name='admin_testimonials'),
    path('admin/testimonials/approve/<str:testimonial_id>/', views.AdminTestimonialApproveView.as_view(), name='admin_testimonial_approve'),
    path('admin/testimonials/reject/<str:testimonial_id>/', views.AdminTestimonialRejectView.as_view(), name='admin_testimonial_reject'),

]