# File: leads/views.py
# Location: C:\git\_clapri\leads\views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import View, ListView
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.db.models import Q
from utils.auth import login_required, get_auth0_user
from .models import Lead, LeadInteraction
from .forms import LeadForm, LeadNoteForm, LeadSearchForm
from .email_handler import LeadEmailHandler
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LeadListView(ListView):
    template_name = 'leads/lead_list.html'
    context_object_name = 'leads'
    paginate_by = 20

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = Lead.objects.all().order_by('-created_at')
        form = LeadSearchForm(self.request.GET)
        
        if form.is_valid():
            if form.cleaned_data.get('search'):
                search = form.cleaned_data['search']
                queryset = queryset.filter(
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(company__icontains=search)
                )
            
            if form.cleaned_data.get('status'):
                queryset = queryset.filter(status=form.cleaned_data['status'])
            
            if form.cleaned_data.get('source'):
                queryset = queryset.filter(source=form.cleaned_data['source'])
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = LeadSearchForm(self.request.GET)
        return context

class LeadCreateView(View):
    template_name = 'leads/lead_create.html'
    
    @method_decorator(login_required)
    def get(self, request):
        # Check if user is admin
        user = get_auth0_user(request)
        if not user.get('app_metadata', {}).get('is_admin'):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('core:home')
            
        context = {
            'form': LeadForm(),
            'user': user
        }
        return render(request, self.template_name, context)
    
    @method_decorator(login_required)
    def post(self, request):
        user = get_auth0_user(request)
        if not user.get('app_metadata', {}).get('is_admin'):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('core:home')
            
        form = LeadForm(request.POST)
        if form.is_valid():
            try:
                lead = Lead(
                    name=f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}", # Combine names
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data.get('phone', ''),
                    property_type=form.cleaned_data.get('property_type'),
                    message=form.cleaned_data.get('notes', ''),  # Use notes as message
                    created_at=datetime.now()
                )
                lead.save()
                messages.success(request, 'Lead created successfully!')
                return redirect('core:lead_list')
            except Exception as e:
                messages.error(request, f'Error creating lead: {str(e)}')
                print(f"Error saving lead: {str(e)}")  # Add debug print
        
        context = {
            'form': form,
            'user': user
        }
        return render(request, self.template_name, context)        

class LeadDetailView(View):
    @method_decorator(login_required)
    def get(self, request, lead_id):
        lead = get_object_or_404(Lead, id=lead_id)
        interactions = LeadInteraction.objects.filter(lead=lead).order_by('-timestamp')
        note_form = LeadNoteForm()
        
        context = {
            'lead': lead,
            'interactions': interactions,
            'note_form': note_form
        }
        return render(request, 'leads/lead_detail.html', context)

class LeadNoteView(View):
    @method_decorator(login_required)
    def post(self, request, lead_id):
        lead = get_object_or_404(Lead, id=lead_id)
        form = LeadNoteForm(request.POST)
        
        if form.is_valid():
            lead.add_note(form.cleaned_data['content'], request.user.get_full_name())
            messages.success(request, 'Note added successfully.')
        else:
            messages.error(request, 'Error adding note.')
            
        return redirect('leads:lead_detail', lead_id=lead_id)

class LeadStatusUpdateView(View):
    @method_decorator(login_required)
    def post(self, request, lead_id):
        lead = get_object_or_404(Lead, id=lead_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Lead.STATUS_CHOICES):
            lead.status = new_status
            lead.save()
            lead.add_note(f"Status updated to: {new_status}", request.user.get_full_name())
            messages.success(request, 'Lead status updated successfully.')
        else:
            messages.error(request, 'Invalid status.')
            
        return redirect('leads:lead_detail', lead_id=lead_id)