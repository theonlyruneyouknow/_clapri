# File: core/templatetags/custom_filters.py
# Location: C:\git\_clapri\core\templatetags\custom_filters.py

from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    return dictionary.get(key) if dictionary else None