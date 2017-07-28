"""A module of small useful functions for helpers."""
from django.shortcuts import redirect as django_redir
import urllib


def redirect(url, *args, **kwargs):
    """Substitute for django's inbuilt redirect, but add get perameters to the uri."""
    params = kwargs.pop('params', {})
    response = django_redir(url, *args, **kwargs)
    if len(params) > 0:
        response['Location'] += '?' + urllib.parse.urlencode(params)
    return response
