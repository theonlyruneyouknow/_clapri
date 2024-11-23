# File: content_management/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import View, ListView
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from utils.auth import login_required
from .models import PageContent, Theme
from .forms import PageContentForm, ThemeForm
from datetime import datetime

class ContentListView(ListView):
    template_name = 'content_management/content_list.html'
    context_object_name = 'contents'

    def get_queryset(self):
        queryset = PageContent.objects.filter(archived=False)
        page_type = self.request.GET.get('page_type')
        theme = self.request.GET.get('theme')
        
        if page_type:
            queryset = queryset.filter(page_type=page_type)
        if theme:
            queryset = queryset.filter(theme=theme)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['themes'] = Theme.objects.all()
        return context

class ContentCreateView(View):
    @login_required
    def get(self, request):
        form = PageContentForm()
        return render(request, 'content_management/content_form.html', {'form': form})

    @login_required
    def post(self, request):
        form = PageContentForm(request.POST)
        if form.is_valid():
            content = PageContent(
                title=form.cleaned_data['title'],
                content=form.cleaned_data['content'],
                page_type=form.cleaned_data['page_type'],
                theme=form.cleaned_data['theme'],
                active=form.cleaned_data['active'],
                display_from=form.cleaned_data['display_from'],
                display_until=form.cleaned_data['display_until']
            )
            content.save()
            messages.success(request, 'Content created successfully!')
            return redirect('content_management:content_list')
        return render(request, 'content_management/content_form.html', {'form': form})

class ContentInlineEditView(View):
    @login_required
    def post(self, request, content_id):
        content = get_object_or_404(PageContent, id=content_id)
        new_content = request.POST.get('content')
        if new_content:
            content.content = new_content
            content.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error'}, status=400)

class ContentDuplicateView(View):
    @login_required
    def post(self, request, content_id):
        content = get_object_or_404(PageContent, id=content_id)
        new_content = content.duplicate()
        messages.success(request, 'Content duplicated successfully!')
        return redirect('content_management:content_edit', content_id=new_content.id)