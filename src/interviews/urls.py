from django.conf.urls import url
from django.views.generic import RedirectView
from . import views

from .forms import COMPANY_WIZARD_FORMS, ASSESSMENT_WIZARD_FORMS, INTERVIEW_WIZARD_FORMS

app_name = 'interviews'

company_wizard = views.CompanyWizard.as_view(COMPANY_WIZARD_FORMS, url_name='interviews:new_company_step', done_step_name='complete')
assessment_wizard = views.AssessmentWizard.as_view(ASSESSMENT_WIZARD_FORMS, url_name='interviews:new_assessment_step', done_step_name='complete')
interview_wizard = views.InterviewWizard.as_view(INTERVIEW_WIZARD_FORMS, url_name='interviews:new_interview_step', done_step_name='complete')

urlpatterns = [

    #### DASHBOARD
    url(r'^$', RedirectView.as_view(url='dashboard/'), name='interviews'),
    url(r'^dashboard/', views.dashboard, name='dashboard'),

    #### COMPANY CREATION
    # Wizard
    url(r'^company/new/(?P<step>.+)/$', company_wizard, name='new_company_step'),
    url(r'^company/new/$', company_wizard, name='new_company'),
    # Company
    url(r'^company/office/(?P<office_id>[\w\-]+)/employee/new/', views.new_employee, name='new_employee'),
    url(r'^company/office/(?P<office_id>[\w\-]+)/employee/(?P<employee_id>[\w\-]+)/edit/', views.edit_employee, name='edit_employee'),
    url(r'^company/office/(?P<office_id>[\w\-]+)/room/new/', views.new_room, name='new_room'),
    url(r'^company/office/(?P<office_id>[\w\-]+)/room/(?P<room_id>[\w\-]+)/edit/', views.edit_room, name='edit_room'),
    url(r'^company/office/new/', views.new_office, name='new_office'),
    url(r'^company/office/(?P<office_id>[\w\-]+)/edit/', views.edit_office, name='edit_office'),
    url(r'^company/office/(?P<office_id>[\w\-]+)/', views.office, name='office'),
    url(r'^company/edit/', views.edit_company, name='edit_company'),
    url(r'^company/', views.company, name='company'),
    
    #### INDIVIDUAL INTERVIEW
    # Wizard
    url(r'^interview/new/(?P<step>.+)/$', interview_wizard, name='new_interview_step'),
    url(r'^interview/new/$', interview_wizard, name='new_interview'),
    # Interview
    url(r'^interview/(?P<interview_id>[\w\-]+)/assess/', views.assess_interview, name='assess_interview'),
    url(r'^interview/(?P<interview_id>[\w\-]+)/start/', views.start_interview, name='start_interview'),
    url(r'^interview/(?P<interview_id>[\w\-]+)/edit/', views.edit_interview, name='edit_interview'),
    url(r'^interview/(?P<interview_id>[\w\-]+)/rm/', views.delete_interview, name='delete_interview'),
    url(r'^interview/(?P<interview_id>[\w\-]+)/', views.interview, name='interview'),

    #### ASSESSMENT VIEWS
    # Wizard
    url(r'^assessments/new/(?P<step>.+)/$', assessment_wizard, name='new_assessment_step'),
    url(r'^assessments/new/$', assessment_wizard, name='new_assessment'),
    # Assessment interview
    url(r'^assessments/interview/(?P<assessment_interview_id>[\w\-]+)/assess/', views.assess_assessment_interview, name='assess_assessment_interview'),
    url(r'^assessments/interview/(?P<assessment_interview_id>[\w\-]+)/start/', views.start_assessment_interview, name='start_assessment_interview'),
    url(r'^assessments/interview/(?P<assessment_interview_id>[\w\-]+)/', views.assessment_interview, name='assessment_interview'),
    # Assessment schedule creation and editing
    url(r'^assessments/schedule/timeslot/(?P<timeslot_id>[\w\-]+)/rm/', views.schedule_remove_timeslot, name='schedule_remove_timeslot'),
    url(r'^assessments/schedule/timeslot/(?P<timeslot_id>[\w\-]+)/', views.edit_timeslot, name='edit_timeslot'),
    url(r'^assessments/schedule/interview/(?P<interview_id>[\w\-]+)/rm/', views.schedule_remove_interview, name='schedule_remove_interview'),
    url(r'^assessments/schedule/interview/(?P<interview_id>[\w\-]+)/edit/', views.schedule_edit_interview, name='schedule_edit_interview'),
    url(r'^assessments/schedule/interview/(?P<candidate_id>[\w\-]+)/(?P<timeslot_id>[\w\-]+)/', views.schedule_add_interview, name='schedule_add_interview'),
    url(r'^assessments/schedule/(?P<assessment_day_id>[\w\-]+)/candidate/rm/(?P<candidate_id>[\w\-]+)/', views.schedule_remove_candidate, name='schedule_remove_candidate'),
    url(r'^assessments/schedule/(?P<assessment_day_id>[\w\-]+)/candidate/', views.schedule_add_candidate, name='schedule_add_candidate'),
    url(r'^assessments/schedule/(?P<assessment_day_id>[\w\-]+)/timeslot/', views.schedule_add_timeslot, name='schedule_add_timeslot'),
    url(r'^assessments/schedule/(?P<assessment_day_id>[\w\-]+)/edit/', views.edit_schedule, name='edit_schedule'),
    # Assessment information
    url(r'^assessments/(?P<assessment_id>[\w\-]+)/results/', views.results_assessment, name='results_assessment'),
    url(r'^assessments/(?P<assessment_id>[\w\-]+)/logs/', views.logs_assessment, name='logs_assessment'),
    url(r'^assessments/(?P<assessment_id>[\w\-]+)/edit/competency/new/', views.new_competency, name='new_competency'),
    url(r'^assessments/(?P<assessment_id>[\w\-]+)/edit/competency/(?P<competency_id>[\w\-]+)/rm/', views.delete_competency, name='delete_competency'),
    url(r'^assessments/(?P<assessment_id>[\w\-]+)/edit/competency/(?P<competency_id>[\w\-]+)/', views.edit_competency, name='edit_competency'),
    url(r'^assessments/(?P<assessment_id>[\w\-]+)/edit/interview_type/new/', views.new_interview_type, name='new_interview_type'),
    url(r'^assessments/(?P<assessment_id>[\w\-]+)/edit/interview_type/(?P<interview_type_id>[\w\-]+)/rm/', views.delete_interview_type, name='delete_interview_type'),
    url(r'^assessments/(?P<assessment_id>[\w\-]+)/edit/interview_type/(?P<interview_type_id>[\w\-]+)/', views.edit_interview_type, name='edit_interview_type'),
    url(r'^assessments/(?P<assessment_id>[\w\-]+)/edit/candidate/new/', views.new_candidate, name='new_candidate'),
    url(r'^assessments/(?P<assessment_id>[\w\-]+)/edit/candidate/(?P<candidate_id>[\w\-]+)/rm/', views.delete_candidate, name='delete_candidate'),
    url(r'^assessments/(?P<assessment_id>[\w\-]+)/edit/candidate/(?P<candidate_id>[\w\-]+)/', views.edit_candidate, name='edit_candidate'),
    url(r'^assessments/(?P<assessment_id>[\w\-]+)/edit/', views.edit_assessment, name='edit_assessment'),
    url(r'^assessments/(?P<assessment_id>[\w\-]+)/delete/', views.delete_assessment, name='delete_assessment'),
    url(r'^assessments/(?P<assessment_id>[\w\-]+)/', views.assessment, name='assessment'),
    url(r'^assessments/', views.assessments, name='assessments'),

    # Profile
    url(r'^profile/', views.profile, name='profile'),
    url(r'^settings/', views.settings, name='settings'),

]
