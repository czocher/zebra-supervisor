# -*- coding: utf-8 -*-
"""This module contains classes for rest permission management."""
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from rest_framework import permissions
from rest.models import Node
import logging


LOGGER = logging.getLogger(__name__)


def is_authorized_node(request):
    """Return True if the node from the request is authorized."""
    token = request.META.get('HTTP_X_TOKEN')
    ipaddr = request.META.get('REMOTE_ADDR')

    if token is None:
        return False

    try:
        node = Node.objects.get(ipaddr=ipaddr, token=token)
        if not node.authorized:
            return False
    except MultipleObjectsReturned:
        LOGGER.warning(
            "More than one node with the given key on and same ip address."
        )
        return False
    except ObjectDoesNotExist:
        node = Node(ipaddr=ipaddr, token=token, authorized=False)
        node.save()
        return False

    return True


def is_authorized_user(request):
    """Return True if the object can be accessed by the given user."""
    # If user is staff then give him full access
    return request.user.is_staff or request.user.is_authenticated

def is_author(request, obj):
    """Return True if the user is the author of the given object
    and wants to read."""
    return request.user == getattr(obj, 'author', None) \
        and request.method in permissions.SAFE_METHODS


class TokenPermission(permissions.BasePermission):

    """Class to grant persmissions based on a given HTTP request header."""

    def has_permission(self, request, view):
        if not request.is_secure():
            LOGGER.warning(
                    "Received an insecure REST request, HTTPS required.")
        # has_permission is always called before has_object_permission
        # it has to return True if has_object_permission is meant to be called
        # therefore return True if a user is not a node but is authenticated
        # and asks for a concrete submission

        if is_authorized_node(request):
            return True

        if request.user.is_staff:
            return True

        view_name = request.resolver_match.url_name
        if request.user.is_authenticated and view_name == 'submission-detail':
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if not request.is_secure():
            LOGGER.warning(
                    "Received an insecure REST request, HTTPS required.")
        return (is_authorized_node(request) or
                (is_authorized_user(request)
                    and is_author(request, obj)))
