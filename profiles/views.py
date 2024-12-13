# File: profiles/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import View
from utils.auth import login_required, get_auth0_user
from .models import Profile, Testimonial
from .forms import ProfileForm, TestimonialForm
from django.utils.decorators import method_decorator

class DashboardView(View):
    @login_required
    def get(self, request):
        auth0_user = get_auth0_user(request)
        profile = Profile.objects.filter(user_id=auth0_user['sub']).first()
        testimonials = Testimonial.objects.filter(profile=profile) if profile else []
        
        context = {
            'profile': profile,
            'testimonials': testimonials
        }
        return render(request, 'profiles/dashboard.html', context)

class ProfileView(View):
    template_name = 'core/profile.html'

    @method_decorator(login_required)
    def get(self, request):
        user = get_auth0_user(request)
        
        # Get stored profile from database
        profile = Profile.objects.filter(user_id=user['sub']).first()
        
        # Merge Auth0 metadata with stored profile
        profile_data = {
            'first_name': profile.first_name if profile else user.get('given_name', ''),
            'last_name': profile.last_name if profile else user.get('family_name', ''),
            'email': user.get('email', ''),
            'phone': profile.phone if profile else '',
            'company': profile.company if profile else user.get('company', ''),
            'address': profile.address if profile else '',
            'city': profile.city if profile else '',
            'state': profile.state if profile else '',
            'zip_code': profile.zip_code if profile else '',
            'picture': user.get('picture', ''),
            'created_at': profile.created_at if profile else None,
            'is_verified': profile.is_verified if profile else False
        }

        context = {
            'user': user,
            'profile': profile_data,
            'is_admin': user.get('is_admin') or user.get('/app_metadata', {}).get('is_admin', False)
        }
        
        return render(request, self.template_name, context)

    @login_required
    def post(self, request):
        form = ProfileForm(request.POST)
        if form.is_valid():
            auth0_user = get_auth0_user(request)
            profile, created = Profile.objects.get_or_create(
                user_id=auth0_user['sub'],
                defaults={'email': auth0_user['email']}
            )
            
            profile.first_name = form.cleaned_data['first_name']
            profile.last_name = form.cleaned_data['last_name']
            profile.company = form.cleaned_data['company']
            profile.phone = form.cleaned_data['phone']
            profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('profiles:dashboard')
        
        return render(request, 'profiles/profile_form.html', {'form': form})

class TestimonialCreateView(View):
    @login_required
    def get(self, request):
        form = TestimonialForm()
        return render(request, 'profiles/testimonial_form.html', {'form': form})

    @login_required
    def post(self, request):
        form = TestimonialForm(request.POST)
        if form.is_valid():
            auth0_user = get_auth0_user(request)
            profile = Profile.objects.get(user_id=auth0_user['sub'])
            
            testimonial = Testimonial(
                profile=profile,
                title=form.cleaned_data['title'],
                content=form.cleaned_data['content'],
                rating=form.cleaned_data['rating']
            )
            testimonial.save()
            
            messages.success(request, 'Testimonial submitted successfully! It will be visible after approval.')
            return redirect('profiles:dashboard')
        
        return render(request, 'profiles/testimonial_form.html', {'form': form})

class TestimonialEditView(View):
    @login_required
    def get(self, request, testimonial_id):
        testimonial = get_object_or_404(Testimonial, id=testimonial_id)
        auth0_user = get_auth0_user(request)
        profile = Profile.objects.get(user_id=auth0_user['sub'])
        
        if testimonial.profile != profile:
            messages.error(request, "You don't have permission to edit this testimonial.")
            return redirect('profiles:dashboard')
        
        form = TestimonialForm(initial={
            'title': testimonial.title,
            'content': testimonial.content,
            'rating': testimonial.rating
        })
        return render(request, 'profiles/testimonial_form.html', {
            'form': form,
            'testimonial': testimonial
        })

    @login_required
    def post(self, request, testimonial_id):
        testimonial = get_object_or_404(Testimonial, id=testimonial_id)
        auth0_user = get_auth0_user(request)
        profile = Profile.objects.get(user_id=auth0_user['sub'])
        
        if testimonial.profile != profile:
            messages.error(request, "You don't have permission to edit this testimonial.")
            return redirect('profiles:dashboard')
        
        form = TestimonialForm(request.POST)
        if form.is_valid():
            testimonial.title = form.cleaned_data['title']
            testimonial.content = form.cleaned_data['content']
            testimonial.rating = form.cleaned_data['rating']
            testimonial.approved = False  # Reset approval status on edit
            testimonial.save()
            
            messages.success(request, 'Testimonial updated successfully! It will need to be re-approved.')
            return redirect('profiles:dashboard')
        
        return render(request, 'profiles/testimonial_form.html', {
            'form': form,
            'testimonial': testimonial
        })