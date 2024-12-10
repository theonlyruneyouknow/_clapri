# File: leads/views.py
# Location: C:\git\_clapri\leads\views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import View, ListView
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.db.models import Q
from utils.auth import login_required
from .models import Lead, LeadInteraction
from .forms import LeadForm, LeadNoteForm, LeadSearchForm
from .email_handler import LeadEmailHandler
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
    @method_decorator(login_required)
    def get(self, request):
        form = LeadForm()
        return render(request, 'leads/lead_form.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = Lead(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                company=form.cleaned_data['company'],
                property_type=form.cleaned_data['property_type'],
                property_address=form.cleaned_data['property_address'],
                source=form.cleaned_data['source'],
                assigned_to=request.user
            )
            
            if form.cleaned_data.get('notes'):
                lead.add_note(form.cleaned_data['notes'], request.user.get_full_name())
            
            lead.save()
            
            # Send welcome email
            email_handler = LeadEmailHandler()
            if email_handler.send_welcome_email(lead, request.user):
                messages.success(request, 'Lead created and welcome email sent successfully.')
            else:
                messages.warning(request, 'Lead created but there was an issue sending the welcome email.')
            
            return redirect('leads:lead_detail', lead_id=lead.id)
        
        return render(request, 'leads/lead_form.html', {'form': form})

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