from django.conf.urls import url, include
from api import views
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'offices', views.OfficeViewSet)
router.register(r'rooms', views.RoomViewSet)
router.register(r'employees', views.EmployeeViewSet)
router.register(r'candidates', views.CandidateViewSet)
router.register(r'competencies', views.CompetencyViewSet)
router.register(r'interviews', views.InterviewViewSet)
router.register(r'results', views.ResultViewSet)
router.register(r'assessments/interview_types', views.AssessmentInterviewTypeViewSet)
router.register(r'assessments/interviews', views.AssessmentInterviewViewSet)
router.register(r'assessments/results', views.AssessmentInterviewResultViewSet)
router.register(r'assessments/role_affinities', views.RoleAffinityViewSet)
router.register(r'assessments/extra_event_types', views.ExtraEventTypeViewSet)
router.register(r'assessments/extra_events', views.ExtraEventViewSet)
router.register(r'assessments', views.AssessmentViewSet)

schema_view = get_schema_view(title='Assessment Center API')

# API Endpoints
urlpatterns = [

    url('^schema/$', schema_view),

    url(r'', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))

]