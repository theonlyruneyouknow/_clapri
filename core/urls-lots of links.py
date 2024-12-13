# File: core/urls.py
# Location: C:\git\_clapri\core\urls.py

from django.urls import path, include
from . import views
from . import admin_views
from .views import AppraisalReportView, AppraisalListView

app_name = 'core'

urlpatterns = [
    # Main URLs
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Appraisal & Appointment URLs
    path('appraisal/request/', views.AppraisalRequestView.as_view(), name='appraisal_request'),
    path('appraisal/request/<str:request_id>/', views.AppraisalRequestDetailView.as_view(), name='appraisal_request_detail'),
    path('appraisal/<str:request_id>/schedule/', views.AppointmentScheduleView.as_view(), name='appointment_schedule'),
    path('appointments/', views.AppointmentListView.as_view(), name='appointments'),
    
    # Testimonial URLs
    path('testimonials/', views.TestimonialsView.as_view(), name='testimonials'),
    path('testimonials/add/', views.TestimonialCreateView.as_view(), name='testimonial_add'),
    path('testimonials/edit/<str:testimonial_id>/', views.TestimonialEditView.as_view(), name='testimonial_edit'),
    
    # Auth URLs
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('callback/', views.callback, name='callback'),
    
    # Lead Management
    path('leads/', views.LeadListView.as_view(), name='lead_list'),
    path('leads/create/', views.LeadCreateView.as_view(), name='lead_create'),
    path('leads/<str:id>/', views.LeadDetailView.as_view(), name='lead_detail'),
    path('leads/<str:id>/delete/', views.LeadDeleteView.as_view(), name='lead_delete'),
    
    # Include other apps
    # path('leads/', include('leads.urls', namespace='leads')),
    
    # Privacy Policy URL
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy'),
    path('terms/', views.TermsOfServiceView.as_view(), name='terms'),
    
    # FAQ URL
    path('faq/', views.FAQView.as_view(), name='faq'),
]