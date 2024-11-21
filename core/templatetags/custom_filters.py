# File: core/templatetags/custom_filters.py
# Location: C:\git\_clapri\core\templatetags\custom_filters.py

from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """
    Template filter to get a value from a dictionary using a key.
    Usage: {{ dictionary|get:'key' }}
    """
    return dictionary.get(key) if dictionary else None