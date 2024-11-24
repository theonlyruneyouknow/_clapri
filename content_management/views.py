# File: content_management/views.py
# Location: C:\git\_clapri\content_management\views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import View, ListView
from django.http import JsonResponse, Http404
from django.utils.decorators import method_decorator
from utils.auth import login_required, get_auth0_user
from .models import PageContent, Theme
from .forms import PageContentForm, ThemeForm
from datetime import datetime
import logging
from mongoengine.errors import DoesNotExist

logger = logging.getLogger(__name__)

class BaseContentView(View):
    def get_context_data(self, **kwargs):
        context = kwargs
        context['user'] = get_auth0_user(self.request)
        return context

    def render_to_response(self, template, context):
        return render(self.request, template, self.get_context_data(**context))


class ContentCreateView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = PageContentForm()
        return render(request, 'content_management/content_form.html', {
            'form': form,
            'themes': Theme.objects.all(),
            'user': get_auth0_user(request)
        })

    @method_decorator(login_required)
    def post(self, request):
        form = PageContentForm(request.POST)
        if form.is_valid():
            content = PageContent(
                title=form.cleaned_data['title'],
                content=form.cleaned_data['content'],
                page_type=form.cleaned_data['page_type'],
                theme=Theme.objects.get(id=form.cleaned_data['theme']) if form.cleaned_data['theme'] else None,
                active=form.cleaned_data['active'],
                display_from=form.cleaned_data['display_from'],
                display_until=form.cleaned_data['display_until']
            )
            content.save()
            messages.success(request, 'Content created successfully!')
            return redirect('content_management:content_list')
        return render(request, 'content_management/content_form.html', {
            'form': form,
            'themes': Theme.objects.all(),
            'user': get_auth0_user(request)
        })

class ContentEditView(View):
    @method_decorator(login_required)
    def get(self, request, content_id):
        try:
            content = PageContent.objects.get(id=content_id)
        except (DoesNotExist, ValueError):
            raise Http404("Content does not exist")

        form = PageContentForm(initial={
            'title': content.title,
            'content': content.content,
            'page_type': content.page_type,
            'theme': str(content.theme.id) if content.theme else '',
            'active': content.active,
            'display_from': content.display_from,
            'display_until': content.display_until
        })
        
        return render(request, 'content_management/content_form.html', {
            'form': form,
            'content': content,
            'themes': Theme.objects.all(),
            'user': get_auth0_user(request)
        })

    @method_decorator(login_required)
    def post(self, request, content_id):
        try:
            content = PageContent.objects.get(id=content_id)
        except (DoesNotExist, ValueError):
            raise Http404("Content does not exist")

        form = PageContentForm(request.POST)
        if form.is_valid():
            content.title = form.cleaned_data['title']
            content.content = form.cleaned_data['content']
            content.page_type = form.cleaned_data['page_type']
            content.theme = Theme.objects.get(id=form.cleaned_data['theme']) if form.cleaned_data['theme'] else None
            content.active = form.cleaned_data['active']
            content.display_from = form.cleaned_data['display_from']
            content.display_until = form.cleaned_data['display_until']
            content.save()
            messages.success(request, 'Content updated successfully!')
            return redirect('content_management:content_list')
            
        return render(request, 'content_management/content_form.html', {
            'form': form,
            'content': content,
            'themes': Theme.objects.all(),
            'user': get_auth0_user(request)
        })

class ContentListView(ListView):
    template_name = 'content_management/content_list.html'
    context_object_name = 'contents'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        context['themes'] = Theme.objects.all()
        context['selected_page_type'] = self.request.GET.get('page_type', 'all')
        context['selected_theme'] = self.request.GET.get('theme', 'all')
        return context

    def get_queryset(self):
        queryset = PageContent.objects()
        
        page_type = self.request.GET.get('page_type')
        theme = self.request.GET.get('theme')
        
        if page_type and page_type != 'all':
            queryset = queryset.filter(page_type=page_type)
        if theme and theme != 'all':
            queryset = queryset.filter(theme=theme)
        
        return queryset.order_by('-created_at')

class ContentDuplicateView(BaseContentView, View):
    @method_decorator(login_required)
    def post(self, request, content_id):
        try:
            content = PageContent.objects.get(id=content_id)
            new_content = content.duplicate()
            messages.success(request, 'Content duplicated successfully!')
            return redirect('content_management:content_edit', content_id=new_content.id)
        except (DoesNotExist, ValueError):
            raise Http404("Content does not exist")
        

class ContentArchiveView(BaseContentView, View):
    @method_decorator(login_required)
    def post(self, request, content_id):
        try:
            content = PageContent.objects.get(id=content_id)
            content.archived = True
            content.active = False
            content.save()
            messages.success(request, 'Content archived successfully!')
            return redirect('content_management:content_list')
        except (DoesNotExist, ValueError):
            raise Http404("Content does not exist")

class ContentInlineEditView(BaseContentView, View):
    @method_decorator(login_required)
    def post(self, request, content_id):
        try:
            content = PageContent.objects.get(id=content_id)
            new_content = request.POST.get('content')
            if new_content:
                content.content = new_content
                content.save()
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'No content provided'}, status=400)
        except (DoesNotExist, ValueError):
            return JsonResponse({'status': 'error', 'message': 'Content not found'}, status=404)

class ThemeListView(ListView):
    template_name = 'content_management/theme_list.html'
    context_object_name = 'themes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        return context

    def get_queryset(self):
        return Theme.objects.all().order_by('name')
    
class ThemeCreateView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = ThemeForm()
        return render(request, 'content_management/theme_form.html', {
            'form': form,
            'user': get_auth0_user(request)
        })

    @method_decorator(login_required)
    def post(self, request):
        form = ThemeForm(request.POST)
        if form.is_valid():
            theme = Theme(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                css_variables=form.cleaned_data.get('css_variables', '')
            )
            theme.save()
            messages.success(request, 'Theme created successfully!')
            return redirect('content_management:content_list')
        return render(request, 'content_management/theme_form.html', {
            'form': form,
            'user': get_auth0_user(request)
        })
