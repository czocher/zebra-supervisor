# -*- coding: utf-8 -*-
from judge.models import Submission, PrintRequest, Result, Tests
from rest_framework import serializers

import logging


LOGGER = logging.getLogger(__name__)


class TestsTimestampsSerializer(serializers.ModelSerializer):
    input = serializers.DateTimeField(source='input.timestamp',
                                      read_only=True)
    output = serializers.DateTimeField(source='output.timestamp',
                                       read_only=True)
    config = serializers.DateTimeField(source='config.timestamp',
                                       read_only=True)

    class Meta:
        model = Tests
        fields = ('input', 'output', 'config')


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ('mark', 'returncode', 'time')


class SubmissionSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_codename',
                                   read_only=True)
    problem = serializers.CharField(source='problem.codename',
                                    read_only=True)
    active = serializers.BooleanField(source='contest._is_active',
                                      read_only=True)
    language = serializers.CharField(source='get_language_display',
                                     read_only=True)
    results = ResultSerializer(many=True, required=False)
    error = serializers.BooleanField(write_only=True)

    def update(self, submission, validated_data):
        error = validated_data.pop('error')
        submission.compilelog = validated_data.get('compilelog', '')
        submission.results.all().delete()

        if error:
            LOGGER.warning(
                "There was an error while judging submission id %s.",
                submission.id
            )
            submission.score = -1
            submission.status = Submission.WAITING_STATUS
        else:
            results = validated_data.pop('results')
            for result in results:
                res = Result(
                    submission=submission,
                    mark=result.get('mark'),
                    returncode=result.get('returncode'),
                    time=result.get('time')
                )
                res.save()

            submission.status = Submission.JUDGED_STATUS

            num_good_results = submission.results.filter(mark=True).count()
            num_results = submission.results.all().count()

            try:
                submission.score = int((float(num_good_results) /
                                        float(num_results)) * 100)
            except ZeroDivisionError:
                submission.score = 0

        submission.save()

        return submission

    class Meta:
        model = Submission
        fields = ('id', 'status', 'problem', 'active', 'language', 'source',
                  'score', 'error', 'results', 'compilelog')
        write_only_fields = ('compilelog', )
        read_only_fields = ('source', 'id', 'score')


class PrintRequestSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_codename',
                                   read_only=True)
    author = serializers.CharField(source='author.username',
                                   read_only=True)
    contest = serializers.CharField(source='contest.name',
                                    read_only=True)
    problem = serializers.CharField(source='problem.codename',
                                    read_only=True)
    language = serializers.CharField(source='get_language_display',
                                     read_only=True)
    error = serializers.BooleanField(write_only=True)

    def update(self, instance, validated_data):
        error = validated_data.pop('error')
        if error:
            LOGGER.warning(
                "There was an error while printing PrintRequest id %s.",
                instance.id
            )
            instance.status = PrintRequest.WAITING_STATUS
        else:
            instance.status = PrintRequest.PRINTED_STATUS
        instance.save()
        return instance

    class Meta:
        model = PrintRequest
        fields = ('id', 'status', 'author', 'contest', 'problem', 'language',
                  'source', 'error',)
        read_only_fields = ('source', 'id',)
