from django import template
from django.urls import reverse
from spec.utils.relative_url import get_relative_url

register = template.Library()

def relative_url(context, view_name, *args):
    url_string = reverse(view_name, args=args)
    return get_relative_url(context['request'].path, url_string)
register.simple_tag(takes_context=True)(relative_url)

def relative_url_string(context, url_string):
    return get_relative_url(context['request'].path, url_string)
register.simple_tag(takes_context=True)(relative_url_string)
