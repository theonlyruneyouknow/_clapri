# File: core/urls.py
# Location: C:\git\_clapri\core\urls.py

from django.urls import path, include
from . import views
from . import admin_views
from .views import AppraisalReportView, AppraisalListView

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('appraisal/request/', views.AppraisalRequestView.as_view(), name='appraisal_request'),
    path('testimonials/', views.TestimonialsView.as_view(), name='testimonials'),
    path('testimonials/add/', views.TestimonialCreateView.as_view(), name='testimonial_add'),
    path('testimonials/edit/<str:testimonial_id>/', views.TestimonialEditView.as_view(), name='testimonial_edit'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('callback/', views.callback, name='callback'),
#     path('appraisal/request/', views.AppraisalRequestView.as_view(), name='appraisal_request'),
    path('appraisal/request/<str:request_id>/', views.AppraisalRequestDetailView.as_view(), name='appraisal_request_detail'),
    path('appraisal/<str:request_id>/schedule/', views.AppointmentScheduleView.as_view(), name='appointment_schedule'),
    path('appointments/', views.AppointmentListView.as_view(), name='appointments'),
    path('appraisal/<str:request_id>/schedule/', 
         views.AppointmentScheduleView.as_view(), 
         name='appointment_schedule'),
    path('appraisal/<str:request_id>/schedule/', 
         views.AppointmentScheduleView.as_view(), 
         name='appointment_schedule'),
    path('appointments/', views.AppointmentListView.as_view(), name='appointments'),
    path('appraisal/<str:request_id>/schedule/', views.AppointmentScheduleView.as_view(), name='appointment_schedule'),
    path('appointment/<str:appointment_id>/reschedule/', views.AppointmentRescheduleView.as_view(), name='appointment_reschedule'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy'),
    path('terms-of-service/', views.TermsOfServiceView.as_view(), name='terms'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('chat/', views.ChatView.as_view(), name='chat'),
    path('test-openai/', views.test_openai, name='test_openai'),
    path('chat/', views.ChatView.as_view(), name='chat'),
    path('reports/<str:report_id>/', AppraisalReportView.as_view(), name='report_detail'),
    path('appraisals/', AppraisalListView.as_view(), name='appraisal_list'),
    path('appraisals/<str:report_id>/', AppraisalReportView.as_view(), name='report_detail'),
    path('appraisal/<str:request_id>/schedule/', views.ScheduleSelectionView.as_view(), name='schedule_selection'),
#     path('appraisals/', AppraisalListView.as_view(), name='appraisal_list'),
#     path('appraisals/<str:report_id>/', AppraisalReportView.as_view(), name='report_detail'),
    path('debug/content/<str:page_type>/', views.ContentDebugView.as_view(), name='content_debug'),
    path('leads/', include('leads.urls')),
    path('content/', include('content_management.urls', namespace='content_management')),

    
    # Admin URLs
    path('admin/dashboard/', admin_views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/testimonials/', admin_views.AdminTestimonialsView.as_view(), name='admin_testimonials'),
    path('admin/testimonials/approve/<str:testimonial_id>/', 
         admin_views.AdminTestimonialApproveView.as_view(), 
         name='admin_testimonial_approve'),
    path('admin/testimonials/reject/<str:testimonial_id>/', 
         admin_views.AdminTestimonialRejectView.as_view(), 
         name='admin_testimonial_reject'),
]