from rest_framework import serializers
from api import models

from django.contrib.auth.models import User

class OfficeSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = models.Office
        fields = ('uuid', 'name', 'address_line_1', 'address_line_2', 'zip_code', 'state', 'city', 'country', 'created_by')


class RoomSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = models.Room
        fields = ('uuid', 'name', 'office', 'building', 'floor', 'size', 'note', 'created_by')


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Employee
        fields = ('uuid', 'user')

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Candidate
        fields = ('uuid', 'user', 'phone', 'country', 'cv', 'note')

class CompetencySerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = models.Competency
        fields = ('uuid', 'name', 'description', 'min_points', 'max_points', 'created_by')

class InterviewSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = models.Interview
        fields = ('uuid', 'name', 'assessors', 'room', 'assessor_material', 'candidate', 'candidate_room', 'candidate_material', 'competencies', 'start_time', 'end_time', 'created_by')

class ResultSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = models.Result
        fields = ('uuid', 'assesor', 'interview', 'competency', 'score', 'note', 'created_by')

class AssessmentSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = models.Assessment
        fields = ('uuid', 'name', 'description', 'office', 'start_date', 'end_date', 'created_by')

class RoleAffinitySerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = models.RoleAffinity
        fields = ('uuid', 'name', 'description', 'assessment', 'created_by')

class AssessmentInterviewTypeSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = models.AssessmentInterviewType
        fields = ('uuid', 'name', 'description', 'assessment', 'competencies', 'color', 'assessor_material', 'candidate_material', 'created_by')

class AssessmentInterviewSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = models.AssessmentInterview
        fields = ('uuid', 'assessors', 'room', 'candidate', 'candidate_room', 'assessment', 'interview_type', 'start_time', 'end_time', 'note', 'created_by')

class AssessmentInterviewResultSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = models.AssessmentInterviewResult
        fields = ('uuid', 'assesor', 'interview', 'competency', 'score', 'note', 'created_by')

class ExtraEventTypeSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = models.ExtraEventType
        fields = ('uuid', 'name', 'description', 'assessment', 'color', 'created_by')

class ExtraEventSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = models.ExtraEvent
        fields = ('uuid', 'assessment', 'extra_event_type', 'description', 'candidate', 'room', 'start_time', 'end_time', 'created_by')


