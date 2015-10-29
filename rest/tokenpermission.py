# -*- coding: utf-8 -*-
"""This module contains classes for rest permission management."""
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from rest_framework import permissions
from rest.models import Node
import logging


LOGGER = logging.getLogger(__name__)


def is_authorized_node(request):
    """Return True if the node from the request is authorized."""
    if not request.is_secure():
        LOGGER.warning(
            "Received an insecure REST request, HTTPS required."
        )

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


def is_authorized_user(request, obj):
    """Return True if the object can be accessed by the given user."""
    if not request.is_secure():
        LOGGER.warning(
            "Received an insecure REST request, HTTPS required."
        )

    # If user is staff then give him full access
    if request.user and request.user.is_staff:
        return True
    # If user is authenticated and is the owner of that commit,
    # then give him read access
    elif request.user and request.user.is_authenticated \
            and request.user == getattr(obj, 'author', None) \
            and request.method in permissions.SAFE_METHODS:
        return True
    return False


class TokenPermission(permissions.BasePermission):

    """Class to grant persmissions based on a given HTTP request header."""

    def has_permission(self, request, view):
        return (is_authorized_node(request) or
                is_authorized_user(request, obj=None))

    def has_object_permission(self, request, view, obj):
        return (is_authorized_node(request) or
                is_authorized_user(request, obj))
