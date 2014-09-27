from django.contrib import admin

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from guardian.admin import GuardedModelAdmin
from judge.models import Submission, Tests, SampleIO, Result, InputTest, \
    OutputTest, ConfigTest, Problem, Contest


class ActiveListFilter(admin.SimpleListFilter):

    """Filters the query, so it shows only active or inactive contests."""
    title = _("active")

    parameter_name = 'active'

    def lookups(self, request, model_admin):
        return (
            ('true', _("is active")),
            ('false', _("is inactive")),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(start_time__lte=timezone.now(),
                                   end_time__gte=timezone.now())
        elif self.value() == 'false':
            return queryset.exclude(start_time__lte=timezone.now(),
                                    end_time__gte=timezone.now())


def set_waiting_status(modeladmin, request, queryset):
    queryset.update(status=Submission.WAITING_STATUS, score=0)
    for submission in queryset:
        submission.results.all().delete()
set_waiting_status.short_description = _(
    "Set selected submissions as waiting for judging")


def rejudge_last_submissions(modeladmin, request, queryset):
    for contest in queryset:
        dummy, users = contest.getProblemsAndLastUsersSubmissions(
            includeFreezing=False)
        for dummy, user in users.items():
            for submission in user.currentSubmissions:
                submission.remove_results()
                submission.score = -1
                submission.status = Submission.WAITING_STATUS
                submission.save()
rejudge_last_submissions.short_description = _(
    "Rejudge last submission for each user and task")


def rejudge_all_submissions(modeladmin, requset, queryset):
    for contest in queryset:
        submissions = Submission.objects.filter(contest=contest)
        for submission in submissions:
            submission.remove_results()
            submission.score = -1
            submission.status = Submission.WAITING_STATUS
            submission.save()
rejudge_all_submissions.short_description = _(
    "Rejudge all submission for this contest")


class ContestAdmin(GuardedModelAdmin):
    list_filter = (ActiveListFilter,)
    list_display = ('name', 'start_time', 'end_time', 'team', '_is_active')
    search_fields = ['name']
    actions = [rejudge_all_submissions, rejudge_last_submissions, ]


class TestAdmin(admin.ModelAdmin):
    list_display = ('name', 'timestamp', 'problem')


class TestsInline(admin.StackedInline):
    model = Tests


class SampleIOInline(admin.StackedInline):
    model = SampleIO
    extra = 1


class ProblemAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('codename', 'name', 'content'),
        }),
    )
    inlines = [SampleIOInline, TestsInline, ]
    search_fields = ['codename', 'name']
    list_display = ('codename', 'name')
    list_display_links = ('codename', 'name')
    prepopulated_fields = {'codename': ('name',)}


class ResultInline(admin.StackedInline):
    model = Result


class SubmissionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('author', 'problem', 'contest', 'language', 'timestamp',
                       'status', 'score'),
        }),
        (_("Source"), {
            'classes': ('collapse',),
            'fields': ('source', 'compilelog',),
        }),
        (_("Node"), {
            'classes': ('collapse',),
            'fields': ('node',)
        }),
    )
    inlines = [ResultInline, ]
    list_display = ('author', 'problem', 'contest', 'language', 'timestamp',
                    'score', 'status', 'node')
    list_filter = ('status',)
    search_fields = ['author__first_name', 'author__last_name',
                     'author__username', 'problem__name', 'contest__name']
    actions = [set_waiting_status, ]


admin.site.register(InputTest, TestAdmin)
admin.site.register(OutputTest, TestAdmin)
admin.site.register(ConfigTest, TestAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(Contest, ContestAdmin)
admin.site.register(Submission, SubmissionAdmin)
