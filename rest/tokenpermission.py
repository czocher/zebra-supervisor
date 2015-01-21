from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from rest_framework import permissions
from rest.models import Node
import logging


logger = logging.getLogger(__name__)


class TokenPermission(permissions.BasePermission):

    def _is_authorized_node(self, request):
        if not request.is_secure():
            logger.warning(
                "Received an insecure REST request, HTTPS required."
            )

        token = request.META.get('HTTP_X_TOKEN')
        ip = request.META.get('REMOTE_ADDR')

        if token is None:
            return False

        try:
            node = Node.objects.get(ip=ip, token=token)
            if not node.authorized:
                return False
        except MultipleObjectsReturned:
            logger.warning(
                "More than one node with the given key on and same ip."
            )
            return False
        except ObjectDoesNotExist:
            node = Node(ip=ip, token=token, authorized=False)
            node.save()
            return False

        return True

    def _is_authorized_user(self, request, obj):
        if not request.is_secure():
            logger.warning(
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

    def has_permission(self, request, view, *args, **kwargs):
        return (self._is_authorized_node(request)
                or self._is_authorized_user(request, obj=None))

    def has_object_permission(self, request, view, obj):
        return (self._is_authorized_node(request)
                or self._is_authorized_user(request, obj))
