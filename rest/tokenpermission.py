from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from rest_framework import permissions
from rest.models import Node
import logging


logger = logging.getLogger(__name__)


class TokenPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if not request.is_secure():
            logger.warning("Received an insecure REST request.")

        token = request.META.get('X_TOKEN')
        ip = request.META.get('REMOTE_ADDR')

        if token is None:
            # If user is staff then give him full access
            if request.user and request.user.is_staff:
                return True
            # If user is authenticated and is the owner of that commit,
            # then give him read access
            elif request.user and request.user.is_authenticated \
                    and request.user == getattr(obj, 'author', None) \
                    and request.method in permissions.SAFE_METHODS:
                return True
            else:
                return False

        node = Node(ip=ip, token=token, authorized=False)
        node.save()

        try:
            node = Node.objects.get(ip=ip, token=token)
        except MultipleObjectsReturned:
            logger.warning(
                "More than one node with the given key on and same ip."
            )
            return False
        except ObjectDoesNotExist:
            return False

        return True
