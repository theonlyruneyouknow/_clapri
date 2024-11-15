# File: core/views.py

from django.shortcuts import render
from django.views.generic import FormView
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .forms import ContactForm

class ContactView(FormView):
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = '/contact/'

    def form_valid(self, form):
        # Send email
        try:
            # Email to admin
            send_mail(
                subject=f"New Contact Form Submission from {form.cleaned_data['name']}",
                message=f"""
                Name: {form.cleaned_data['name']}
                Email: {form.cleaned_data['email']}
                Message: {form.cleaned_data['message']}
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )

            # Confirmation email to user
            send_mail(
                subject="Thank you for contacting us",
                message="""
                Thank you for reaching out to us. We have received your message and will get back to you shortly.

                Best regards,
                Your Appraisal Team
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[form.cleaned_data['email']],
                fail_silently=False,
            )

            messages.success(self.request, "Your message has been sent successfully!")
        except Exception as e:
            messages.error(self.request, "There was an error sending your message. Please try again later.")
            
        return super().form_valid(form)