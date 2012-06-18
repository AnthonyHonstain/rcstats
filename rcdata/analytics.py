from django.conf import settings
from django.template.loader import render_to_string

def analytics(request):
    """
    Returns analytics code.
    """
    if not settings.DEBUG:
        return { 'analytics_code': render_to_string("analytics.html") }
    else:
        return { 'analytics_code': "" }