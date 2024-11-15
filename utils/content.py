# File: utils/content.py

from content_management.models import PageContent
from datetime import datetime

def get_active_content(page_type):
    """
    Get all active and visible content for a specific page type,
    taking into account display dates and archive status
    """
    now = datetime.now()
    return PageContent.objects.filter(
        page_type=page_type,
        active=True,
        archived=False
    ).filter(
        display_from__lte=now,
        display_until__gt=now
    ).order_by('-created_at')

def get_content_by_theme(page_type, theme_id):
    """
    Get content for a specific page and theme
    """
    return get_active_content(page_type).filter(theme=theme_id)