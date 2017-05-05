from django.shortcuts import render
from django.contrib.auth.models import User

from api import models
from api import serializers
from rest_framework import generics, permissions, viewsets

from rest_framework.decorators import api_view, detail_route
from rest_framework.response import Response
from rest_framework.reverse import reverse


class OfficeViewSet(viewsets.ModelViewSet):
    """
    This endpoint allows you to fetch information about offices.

    Use this API explorer to test the requests.
    """
    queryset = models.Office.objects.all()
    serializer_class = serializers.OfficeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class RoomViewSet(viewsets.ModelViewSet):
    """
    This endpoint allows you to fetch information about rooms.

    Use this API explorer to test the requests.
    """
    queryset = models.Room.objects.all()
    serializer_class = serializers.RoomSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    This endpoint allows you to fetch information about assessors.

    Use this API explorer to test the requests.
    """
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer
    permission_classes = (permissions.IsAuthenticated,)

class CandidateViewSet(viewsets.ModelViewSet):
    """
    This endpoint allows you to fetch information about candidates.

    Use this API explorer to test the requests.
    """
    queryset = models.Candidate.objects.all()
    serializer_class = serializers.CandidateSerializer
    permission_classes = (permissions.IsAuthenticated,)

class CompetencyViewSet(viewsets.ModelViewSet):
    """
    This endpoint allows you to fetch information about competencies.

    Use this API explorer to test the requests.
    """
    queryset = models.Competency.objects.all()
    serializer_class = serializers.CompetencySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class InterviewViewSet(viewsets.ModelViewSet):
    """
    This endpoint allows you to fetch information about interviews.

    Use this API explorer to test the requests.
    """
    queryset = models.Interview.objects.all()
    serializer_class = serializers.InterviewSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ResultViewSet(viewsets.ModelViewSet):
    """
    This endpoint allows you to fetch information about results of individual interviews.

    Use this API explorer to test the requests.
    """
    queryset = models.Result.objects.all()
    serializer_class = serializers.ResultSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class AssessmentViewSet(viewsets.ModelViewSet):
    """
    This endpoint allows you to fetch information about assessments.

    Use this API explorer to test the requests.
    """
    queryset = models.Assessment.objects.all()
    serializer_class = serializers.AssessmentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class RoleAffinityViewSet(viewsets.ModelViewSet):
    """
    This endpoint allows you to fetch information about role affinities in an assessment.

    Use this API explorer to test the requests.
    """
    queryset = models.RoleAffinity.objects.all()
    serializer_class = serializers.RoleAffinitySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class AssessmentInterviewTypeViewSet(viewsets.ModelViewSet):
    """
    This endpoint allows you to fetch information about interview types in an assessment.

    Use this API explorer to test the requests.
    """
    queryset = models.AssessmentInterviewType.objects.all()
    serializer_class = serializers.AssessmentInterviewTypeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class AssessmentInterviewViewSet(viewsets.ModelViewSet):
    """
    This endpoint allows you to fetch information about interviews in an assessment.

    Use this API explorer to test the requests.
    """
    queryset = models.AssessmentInterview.objects.all()
    serializer_class = serializers.AssessmentInterviewSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class AssessmentInterviewResultViewSet(viewsets.ModelViewSet):
    """
    This endpoint allows you to fetch information about interview results in an assessment.

    Use this API explorer to test the requests.
    """
    queryset = models.AssessmentInterviewResult.objects.all()
    serializer_class = serializers.AssessmentInterviewResultSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ExtraEventTypeViewSet(viewsets.ModelViewSet):
    """
    This endpoint allows you to fetch information about extra event types in an assessment.

    Use this API explorer to test the requests.
    """
    queryset = models.ExtraEventType.objects.all()
    serializer_class = serializers.ExtraEventTypeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ExtraEventViewSet(viewsets.ModelViewSet):
    """
    This endpoint allows you to fetch information about interview extra events in an assessment.

    Use this API explorer to test the requests.
    """
    queryset = models.ExtraEvent.objects.all()
    serializer_class = serializers.ExtraEventSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)