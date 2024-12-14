# File: core/urls.py
# Location: C:\git\_clapri\core\urls.py

from django.urls import path, include
from . import views
from . import admin_views
from .views import AppraisalReportView, AppraisalListView

app_name = 'core'

urlpatterns = [
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    
    # User Management
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Authentication
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('callback/', views.callback, name='callback'),
    
    # Appraisal & Appointment Management
    path('appraisal/request/', views.AppraisalRequestView.as_view(), name='appraisal_request'),
    path('appraisal/request/<str:request_id>/', views.AppraisalRequestDetailView.as_view(), name='appraisal_request_detail'),
    path('appraisal/<str:request_id>/schedule/', views.AppointmentScheduleView.as_view(), name='appointment_schedule'),
    path('appointments/', views.AppointmentListView.as_view(), name='appointments'),
    
    # Testimonials
    path('testimonials/', views.TestimonialsView.as_view(), name='testimonials'),
    path('testimonials/add/', views.TestimonialCreateView.as_view(), name='testimonial_add'),
    path('testimonials/edit/<str:testimonial_id>/', views.TestimonialEditView.as_view(), name='testimonial_edit'),
    
    # Lead Management URLs
    path('leads/', views.LeadListView.as_view(), name='lead_list'),
    path('leads/create/', views.LeadCreateView.as_view(), name='lead_create'),
    path('leads/<str:id>/', views.LeadDetailView.as_view(), name='lead_detail'),
    path('leads/<str:id>/edit/', views.LeadEditView.as_view(), name='lead_edit'),
    path('leads/<str:id>/delete/', views.LeadDeleteView.as_view(), name='lead_delete'),
    path('leads/<str:id>/status/', views.LeadStatusUpdateView.as_view(), name='lead_status'),

    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('calendar/<int:year>/<int:month>/', views.CalendarView.as_view(), name='calendar'),
    
    path('services/residential/', views.ResidentialServicesView.as_view(), name='residential_services'),
    path('services/commercial/', views.CommercialServicesView.as_view(), name='commercial_services'),
    path('services/consulting/', views.ConsultingServicesView.as_view(), name='consulting_services'),
    path('services/residential/', views.ResidentialServicesView.as_view(), name='residential_services'),
    path('services/commercial/', views.CommercialServicesView.as_view(), name='commercial_services'),
    path('services/consulting/', views.ConsultingServicesView.as_view(), name='consulting_services'),
    
    # Legal & Info Pages
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy'),
    path('terms/', views.TermsOfServiceView.as_view(), name='terms'),
]