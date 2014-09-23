from django.contrib import admin

from django.utils.translation import ugettext_lazy as _
from questions.models import Question


class AnsweredListFilter(admin.SimpleListFilter):
    title = _("is answered")

    parameter_name = 'is_answered'

    def lookups(self, request, model_admin):
        return (
            ('true', _("answered")),
            ('false', _("not answered")),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.exclude(answer="")
        elif self.value() == 'false':
            return queryset.filter(answer="")


def set_question_public(modeladmin, request, queryset):
    queryset.update(public=True)
set_question_public.short_description = _("Make questions public")


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('author', 'problem', 'contest', 'public', 'timestamp', 'title', 'question', 'answer'),
        }),
    )

    list_filter = ('contest__name', AnsweredListFilter,)
    list_display = ('author', 'title', 'problem', 'contest', 'timestamp', 'public', '_is_answered')
    search_fields = ['title', 'author__first_name', 'author__last_name', 'author__username', 'problem__name', 'contest__name']
    actions = [set_question_public, ]

admin.site.register(Question, QuestionAdmin)
