from django.http import Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotAuthenticated

from judge.models import Submission, Problem
from rest.models import Node

from sendfile import sendfile
from rest.serializers import SubmissionSerializer, TestsTimestampsSerializer

from rest_framework.viewsets import GenericViewSet
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.mixins import ListModelMixin,\
    RetrieveModelMixin, UpdateModelMixin

import logging


logger = logging.getLogger(__name__)


class SubmissionViewSet(ListModelMixin, RetrieveModelMixin,
                        UpdateModelMixin, GenericViewSet):
    queryset = Submission.objects.select_for_update()
    serializer_class = SubmissionSerializer

    def list(self, request, *args, **kwargs):
        """Get a submission for judging."""
        queryset = self.get_queryset()
        token = request.META.get('HTTP_X_TOKEN')

        try:
            node = Node.objects.get(token=token)
        except ObjectDoesNotExist:
            raise NotAuthenticated(detail="Unrecognized node token")

        try:
            instance = queryset.filter(
                status=Submission.WAITING_STATUS
            ).latest('timestamp')
            instance.status = Submission.JUDGING_STATUS
            instance.node = node
            instance.results.all().delete()
            instance.save()
        except ObjectDoesNotExist:
            raise Http404

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def pre_save(self, submission):
        if submission.error:
            logger.warning(
                "There was an error while "
                "judging submission id {}.".format(submission.id)
            )
            submission.score = -1
            submission.status = Submission.WAITING_STATUS
        else:
            submission.status = Submission.JUDGED_STATUS

        super(SubmissionViewSet, self).pre_save(submission)

    def post_save(self, submission, *args, **kwargs):
        if submission.status == Submission.JUDGED_STATUS:

            num_good_results = submission.results.filter(mark=True).count()
            num_results = submission.results.all().count()

            try:
                submission.score = int((float(num_good_results)
                                        / float(num_results)) * 100)
            except ZeroDivisionError:
                submission.score = 0
            submission.save()
        super(SubmissionViewSet, self).post_save(submission, *args, **kwargs)


class ProblemViewSet(GenericViewSet):

    queryset = Problem.objects.all()
    lookup_field = 'codename'

    @detail_route()
    def test_input(self, request, codename, *args, **kwargs):
        problem = self.get_object()
        return sendfile(problem.tests.input.file.path)

    @detail_route()
    def test_output(self, request, codename, *args, **kwargs):
        problem = self.get_object()
        return sendfile(problem.tests.output.file.path)

    @detail_route()
    def test_config(self, request, codename, *args, **kwargs):
        problem = self.get_object()
        return sendfile(problem.tests.config.file.path)

    @detail_route()
    def test_timestamps(self, request, codename, *args, **kwargs):
        problem = self.get_object()
        serializer = TestsTimestampsSerializer(problem.tests)
        return Response(serializer.data)


router = DefaultRouter()
router.register(r'submission', SubmissionViewSet)
router.register(r'problem', ProblemViewSet)
