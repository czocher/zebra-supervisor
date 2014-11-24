from django.http import Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from judge.models import Submission, Problem
from sendfile import sendfile
from rest.serializers import SubmissionSerializer, TestsTimestampsSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.mixins import ListModelMixin,\
    RetrieveModelMixin, UpdateModelMixin


class SubmissionViewSet(ListModelMixin, RetrieveModelMixin,
                        UpdateModelMixin, GenericViewSet):
    queryset = Submission.objects.select_for_update()
    serializer_class = SubmissionSerializer

    def list(self, *args, **kwargs):
        """Get a submission for judging."""
        queryset = self.get_queryset()

        try:
            instance = queryset.filter(
                status=Submission.WAITING_STATUS
            ).latest('timestamp')
            instance.status = Submission.JUDGING_STATUS
            instance.save()
        except ObjectDoesNotExist:
            raise Http404

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def pre_save(self, submission):
        num_good_results = submission.results.all().filter(mark=True).count()
        num_results = submission.results.all().count()
        try:
            submission.score = int((float(num_good_results)
                                    / float(num_results)) * 100)
        except ZeroDivisionError:
            submission.score = 0
        return super(SubmissionViewSet, self).pre_save(submission)


class ProblemViewSet(GenericViewSet):

    queryset = Problem.objects.all()

    @detail_route()
    def test_input(self, request, pk, *args, **kwargs):
        problem = self.get_object()
        return sendfile(problem.tests.input.file.path)

    @detail_route()
    def test_output(self, request, pk, *args, **kwargs):
        problem = self.get_object()
        return sendfile(problem.tests.output.file.path)

    @detail_route()
    def test_config(self, request, pk, *args, **kwargs):
        problem = self.get_object()
        return sendfile(problem.tests.output.file.path)

    @detail_route()
    def test_timestamps(self, request, pk, *args, **kwargs):
        problem = self.get_object()
        serializer = TestsTimestampsSerializer(problem.tests)
        return Response(serializer.data)


router = DefaultRouter()
router.register(r'submission', SubmissionViewSet)
router.register(r'problem', ProblemViewSet)
