# File: core/models.py
# Location: C:\git\_clapri\core\models.py

from mongoengine import Document, StringField, DateTimeField, BooleanField, EmailField
from datetime import datetime
from django.views.generic import FormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import AppraisalRequestForm, AppraisalRequest
from django.contrib.auth import get_auth0_user
# from .models import AppraisalRequest

class UserProfile(Document):
    user_id = StringField(required=True, unique=True)  # Auth0 user ID
    email = EmailField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    phone = StringField(max_length=20)
    company = StringField(max_length=100)
    address = StringField(max_length=200)
    city = StringField(max_length=100)
    state = StringField(max_length=50)
    zip_code = StringField(max_length=10)
    is_verified = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'user_profiles',
        'indexes': [
            'user_id',
            'email'
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(UserProfile, self).save(*args, **kwargs)

    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return "Anonymous"

    @property
    def full_address(self):
        address_parts = [
            self.address,
            self.city,
            self.state,
            self.zip_code
        ]
        return ', '.join(filter(None, address_parts))
    

# File: core/views.py
# Location: C:\git\_clapri\core\views.py



# Add this to your views.py

class AppraisalRequestView(FormView):
    template_name = 'core/appraisal_request.html'
    form_class = AppraisalRequestForm
    success_url = '/dashboard/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        user = get_auth0_user(self.request)
        
        appraisal_request = AppraisalRequest(
            user_id=user['sub'],
            property_address=form.cleaned_data['property_address'],
            property_city=form.cleaned_data['property_city'],
            property_state=form.cleaned_data['property_state'],
            property_zip=form.cleaned_data['property_zip'],
            property_type=form.cleaned_data['property_type'],
            square_footage=form.cleaned_data['square_footage'],
            year_built=form.cleaned_data['year_built'],
            bedrooms=form.cleaned_data['bedrooms'],
            bathrooms=form.cleaned_data['bathrooms'],
            lot_size=form.cleaned_data['lot_size'],
            purpose=form.cleaned_data['purpose'],
            preferred_date=form.cleaned_data['preferred_date'],
            alternate_date=form.cleaned_data['alternate_date'],
            notes=form.cleaned_data['notes']
        )
        appraisal_request.save()
        
        messages.success(self.request, 'Your appraisal request has been submitted successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        return context