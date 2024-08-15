from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
from spectools.utils.relative_url import get_relative_url
import re

register = template.Library()

def relative_url(context, view_name, *args):
    url_string = reverse(view_name, args=args)
    return get_relative_url(context['request'].path, url_string or '')
register.simple_tag(takes_context=True)(relative_url)

def relative_url_string(context, url_string):
    return get_relative_url(context['request'].path, url_string or '')
register.simple_tag(takes_context=True)(relative_url_string)

def make_urls_relative_callback(path, match):
    return get_relative_url(path, match.group(0))

def make_urls_relative(context, html):
    path = context['request'].path
    html = re.sub(
        r'(?<=href=")[^"]+',
        lambda match: make_urls_relative_callback(path, match),
        html
    )
    html = re.sub(
        r'(?<=src=")[^"]+',
        lambda match: make_urls_relative_callback(path, match),
        html
    )
    return mark_safe(html)
register.simple_tag(takes_context=True)(make_urls_relative)
