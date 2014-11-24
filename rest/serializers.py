from judge.models import Submission, Result, Tests
from rest_framework import serializers


class TestsTimestampsSerializer(serializers.ModelSerializer):
    input = serializers.CharField(source='input.timestamp')
    output = serializers.CharField(source='output.timestamp')
    config = serializers.CharField(source='config.timestamp')

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
    results = ResultSerializer(many=True)

    class Meta:
        model = Submission
        fields = ('id', 'status', 'problem', 'active',
                  'language', 'source', 'score', 'results')
        write_only_fields = ('compilelog', )
        read_only_fields = ('score', 'source', 'id')
