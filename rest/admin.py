from models import *
from django.contrib import admin

from django.utils.translation import ugettext_lazy as _


def set_authorized(modeladmin, request, queryset):
    queryset.update(authorized=True)
set_authorized.short_description = _("Set selected nodes as authorized")


def set_unauthorized(modeladmin, request, queryset):
    queryset.update(authorized=False)
set_unauthorized.short_description = _("Set selected nodes as unauthorized")


class AuthorizedListFilter(admin.SimpleListFilter):
    """Filters the query, so it shows only authorized or unauthorized nodes"""
    title = _("authorized")

    parameter_name = 'authorized'

    def lookups(self, request, model_admin):
        return (
            ('true', _("is authorized")),
            ('false', _("is unauthorized")),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(authorized=True)
        elif self.value() == 'false':
            return queryset.filter(authorized=False)


def set_active(modeladmin, request, queryset):
    queryset.update(active=True)
set_active.short_description = _("Activate selected sessions")


def set_inactive(modeladmin, request, queryset):
    queryset.update(active=False)
set_inactive.short_description = _("Deactivate selected sessions")


class ExpiredSessionListFilter(admin.SimpleListFilter):
    """Filters the query, so it shows only expired or unexpired sessions."""
    title = _("expired")

    parameter_name = 'expired'

    def lookups(self, request, model_admin):
        return (
            ('true', _("is expired")),
            ('false', _("is unexpired")),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(expiration_time__lt=timezone.now())
        elif self.value() == 'false':
            return queryset.filter(expiration_time__gte=timezone.now())


class ActiveSessionListFilter(admin.SimpleListFilter):
    """Filters the query, so it shows only active sessions."""
    title = _("active")

    parameter_name = 'active'

    def lookups(self, request, model_admin):
        return (
            ('true', _("is active")),
            ('false', _("is inactive")),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(active=True)
        elif self.value() == 'false':
            return queryset.filter(active=False)


class LanguageAdmin(admin.ModelAdmin):
    pass


class NodeInfoInline(admin.StackedInline):
    model = NodeInfo


class NodeAdmin(admin.ModelAdmin):
    list_filter = (AuthorizedListFilter, )
    list_display = ('name', 'key', 'authorized')
    search_fields = ['name', 'version']
    actions = [set_authorized, set_unauthorized, ]
    inlines = [NodeInfoInline, ]


class NodeSessionAdmin(admin.ModelAdmin):
    list_filter = (ActiveSessionListFilter, ExpiredSessionListFilter)
    actions = [set_active, set_inactive, ]
    list_display = ('id', '_is_expired', 'active')

admin.site.register(Node, NodeAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(NodeSession, NodeSessionAdmin)
