import os, string, random

from django.shortcuts import render, render_to_response, redirect

from django.contrib.auth.decorators import login_required
from guardian.shortcuts import get_objects_for_user

from api.models import Assessment, Interview, AssessmentInterview, AssessmentInterviewType, Candidate, Schedule, Employee, Competency, AssessmentDay, Timeslot, AssessmentInterviewResult, AssessmentLogEvent, Result, Office, Room
from clients.models import Client, Card

from .forms import ScheduleInterviewForm, AssessmentEditForm, TimeslotForm, AddCandidateForm, InterviewTypeEditForm, CandidateEditForm, CandidateForm, InterviewForm, CompetencyForm, CompanyEditForm, ProfileForm, OfficeEditForm, RoomEditForm, EmployeeEditForm, CompetencyMultipleFormSetHelper, InterviewTypeMultipleFormSetHelper, CandidateMultipleFormSetHelper, SettingsForm, UserEditForm
from .util import interview_is_completed, interview_status, assessment_status, assessment_progress
from django.contrib.auth.models import User, Group
from django.urls import reverse

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from django.forms import MultipleChoiceField, ChoiceField, modelformset_factory, ModelChoiceField

from formtools.wizard.views import NamedUrlSessionWizardView
from django.conf import settings as project_settings
from django.core.files.storage import FileSystemStorage

from tenant_schemas.utils import schema_context


COMPANY_TEMPLATES = {
    'plan': 'company_registration/wizard/plan.html', 
    'details': 'company_registration/wizard/company.html', 
    'admin': 'company_registration/wizard/admin.html', 
    'payment': 'company_registration/wizard/payment.html', 
}

INTERVIEW_TEMPLATES = {
    'details': 'app/individual/new/details.html', 
    'competencies': 'app/individual/new/competencies.html', 
    'candidate':'app/individual/new/candidate.html',
    'assessors': 'app/individual/new/assessors.html',
}

ASSESSMENT_TEMPLATES = {
    'details': 'app/assessments/new/details.html',
    'competencies': 'app/assessments/new/competencies.html', 
    'interview_types': 'app/assessments/new/interview_types.html', 
    'candidates':'app/assessments/new/candidates.html',
}

class CompanyWizard(NamedUrlSessionWizardView):

    file_storage = FileSystemStorage(location=os.path.join(project_settings.MEDIA_ROOT, 'files'))

    def get_template_names(self):
        return COMPANY_TEMPLATES[self.steps.current]

    def done(self, form_list, **kwargs):
        """
        This is called once the wizard is finished.
        """
        plan_form = self.get_cleaned_data_for_step('plan')
        details_form = self.get_cleaned_data_for_step('details')
        admin_form = self.get_cleaned_data_for_step('admin')
        payment_form = self.get_cleaned_data_for_step('payment')

        if plan_form['plan'] == 'Yearly':
            paid_until = date.today() + relativedelta(months=+12)
        else:
            paid_until = date.today() + relativedelta(months=+1)

        company = Client(
            domain_url=details_form['domain_url'] + '.' + project_settings.DOMAIN,
            schema_name=details_form['domain_url'],
            name=details_form['name'], 
            description=details_form['description'],
            plan=plan_form['plan'],
            paid_until=paid_until,
            on_trial=True if plan_form['plan'] == 'Trial' else False
        )
        company.save()

        with schema_context(details_form['domain_url']):

            user = User(
                email=admin_form['email'],
                first_name=admin_form['first_name'],
                last_name=admin_form['last_name'],
                is_staff=True,
                is_superuser=True,
            )
            user.username = user.email
            user.set_password(admin_form['password1'])
            user.save()

            employee = Employee(user=user)
            employee.save()

            card = Card(
                client=self.request.tenant,
                card_number=payment_form['card_number'],
                card_cvv=payment_form['card_cvv'],
                card_expiry_month=payment_form['card_expiry_month'],
                card_expiry_year=payment_form['card_expiry_year'],
            )
            card.save()

        return render(self.request, 'company_registration/wizard/company_created.html', context={'company': company})



class InterviewWizard(NamedUrlSessionWizardView):

    file_storage = FileSystemStorage(location=os.path.join(project_settings.MEDIA_ROOT, 'files'))

    def get_template_names(self):
        return INTERVIEW_TEMPLATES[self.steps.current]

    def get_context_data(self, form, **kwargs):

        context = super(InterviewWizard, self).get_context_data(form=form, **kwargs)

        if self.steps.current == 'competencies':
            context.update({'helper': CompetencyMultipleFormSetHelper()})

        return context

    def done(self, form_list, **kwargs):
        """
        This is called once the wizard is finished.
        """
        details_form = self.get_cleaned_data_for_step('details')
        competencies_form = self.get_cleaned_data_for_step('competencies')
        candidate_form = self.get_cleaned_data_for_step('candidate')
        assessors_form = filter(None, self.get_cleaned_data_for_step('assessors'))

        interview = self._create_interview(details_form)
        interview.candidate = self._create_candidate(candidate_form)
        for assessor in assessors_form:
            interview.assessors.add(assessor)
        interview.save()

        for competency in competencies_form:
            interview.competencies.add(self._create_competency(competency))

        return render(self.request, 'app/individual/new/interview_created.html', context={})

    def _create_interview(self, details_form):
        """
        Creates an Interview object based on the inputs from the forms.
        """
        return Interview(
            name=details_form['name'], 
            description=details_form['description'], 
            assessor_material=details_form['assessor_material'], 
            candidate_material=details_form['candidate_material'], 
            start=details_form['start'], 
            end=details_form['end'],
        )

    def _create_candidate(self, candidate_form):
        """
        Creates a candidate object based on the inputs in the form.
        """
        candidate_user = User(
            username=candidate_form['email'], 
            email=candidate_form['email'], 
            first_name=candidate_form['first_name'], 
            last_name=candidate_form['last_name']
        )
        candidate_user.set_password(
            ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
        )
        candidate_user.save()

        candidate = Candidate(
            user=candidate_user,
            cv=candidate_form['cv'],
            phone=candidate_form['phone'],
            address=candidate_form['address'],
            city=candidate_form['city'],
            country=candidate_form['country'],
            timezone=candidate_form['timezone'],
            #note=candidate_form['note'],
        )
        candidate.save()

        return candidate

    def _create_competency(self, competency_details):
        """
        Creates a competency object based on the inputs in the form.
        """
        competency = Competency(
            name=competency_details['name'], 
            description=competency_details['description'], 
            min_points=competency_details['min_points'], 
            max_points=competency_details['max_points'],
        )
        competency.save()

        return competency



class AssessmentWizard(NamedUrlSessionWizardView):

    file_storage = FileSystemStorage(location=os.path.join(project_settings.MEDIA_ROOT, 'files'))

    def get_template_names(self):
        return ASSESSMENT_TEMPLATES[self.steps.current]

    def get_form_initial(self, step):

        if step == 'interview_types':

            form_class = self.form_list[step]
            competencies = [self._create_competency(c) for c in self._remove_empty(self.get_cleaned_data_for_step('competencies'))]

            initial = []
            for i in range(form_class.extra):
                initial.append({
                    'competencies': MultipleChoiceField(choices=[(c, c) for c in competencies])
                })

            return initial

        elif step == 'details':
                        
            return {
                'office': ModelChoiceField(
                    queryset=Office.objects.all(), 
                    empty_label='Choose an office',
                )
            }

        elif step == 'candidates':

            form_class = self.form_list[step]
            office = self.get_cleaned_data_for_step('details')['office']
            
            initial = []
            for i in range(form_class.extra):
                initial.append({
                    'timezone': office.timezone,
                    'country': office.country,
                })

            return initial


    def get_context_data(self, form, **kwargs):

        context = super(AssessmentWizard, self).get_context_data(form=form, **kwargs)

        if self.steps.current == 'competencies':
            context.update({'helper': CompetencyMultipleFormSetHelper()})  
        elif self.steps.current == 'interview_types':
            context.update({'helper': InterviewTypeMultipleFormSetHelper()})
        elif self.steps.current == 'candidates':
            context.update({'helper': CandidateMultipleFormSetHelper()})

        return context

    def done(self, form_list, **kwargs):
        details_form = self.get_cleaned_data_for_step('details')
        competencies_form = self._remove_empty(self.get_cleaned_data_for_step('competencies'))
        interview_types_form = self._remove_empty(self.get_cleaned_data_for_step('interview_types'))
        candidates_form = self._remove_empty(self.get_cleaned_data_for_step('candidates'))
        
        competencies = [ self._create_competency(competency_details) for competency_details in competencies_form ]
        assessment = self._create_assessment(details_form)
        assessment.save()
        assessment.competencies = competencies
        assessment.save()

        for interview_type_details in interview_types_form:
            self._create_interview_type(interview_type_details, competencies, assessment)

        for candidate_details in candidates_form:
            assessment.add_user(self._create_candidate(candidate_details).user, role="candidate")     

        return render(self.request, 'app/assessments/new/assessment_created.html', context={})

    def _remove_empty(self, array_of_dicts):
        return [ d for d in array_of_dicts if d != {} ]

    def _create_assessment(self, details_form):
        """
        Creates an Assessment object based on the inputs in the form.
        """
        return Assessment(
            name=details_form['name'], 
            description=details_form['description'], 
            start_date=details_form['start_date'], 
            end_date=details_form['end_date'], 
            office=details_form['office'], 
            public=details_form['public']
        )

    def _create_competency(self, competency_details):
        """
        Creates a Competency object based on the inputs in the form.
        """
        competency = Competency(
            name=competency_details['name'], 
            description=competency_details['description'], 
            min_points=competency_details['min_points'], 
            max_points=competency_details['max_points']
        )
        competency.save()

        return competency

    def _create_interview_type(self, interview_type_details, competencies, assessment):
        """
        Creates an AssessmentInterviewType object based on the inputs in the form.
        """
        i_t_competencies = []

        for c in competencies:
            if c.name in interview_type_details['competencies_assessed']:
                i_t_competencies.append(c)

        interview_type = AssessmentInterviewType(
            name=interview_type_details['name'],
            description=interview_type_details['description'],
            assessment=assessment,
            color=interview_type_details['color'],
            assessor_material=interview_type_details['assessor_material'],
            candidate_material=interview_type_details['candidate_material'],
        )
        interview_type.save()

        interview_type.competencies = i_t_competencies
        interview_type.save()

        return interview_type

    def _create_candidate(self, candidate_form):
        """
        Creates a candidate object based on the inputs in the form.
        """
        candidate_user = User(
            username=candidate_form['email'],
            email=candidate_form['email'],
            first_name=candidate_form['first_name'],
            last_name=candidate_form['last_name']
        )
        candidate_user.set_password(
            ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
        )
        candidate_user.save()

        candidate = Candidate(
            user=candidate_user,
            cv=candidate_form['cv'],
            phone=candidate_form['phone'],
            address=candidate_form['address'],
            city=candidate_form['city'],
            country=candidate_form['country'],
            timezone=candidate_form['timezone'],
            #note=candidate_form['note'],
        )
        candidate.save()

        return candidate


@login_required
def dashboard(request):

    interviews = get_objects_for_user(request.user, 'api.view_interview')
    assessment_interviews = get_objects_for_user(request.user, 'api.view_assessment_interview') 
    assessments = get_objects_for_user(request.user, 'api.view_assessment')
    offices = get_objects_for_user(request.user, 'api.view_office')

    employee = Employee.objects.get(user=request.user)

    context = {
        "company": request.tenant,
        "offices": offices,
        "interviews": interviews,
        "assessment_interviews": assessment_interviews,
        "assessments": assessments,
        "todays_date": datetime.now().strftime('%Y-%m-%d'),
        "deleted": request.GET.get('deleted'),
        "agenda_view": employee.agenda_view
    }

    return render(
        request,
        'app/dashboard.html',
        context=context
    )


@login_required
def interview(request, interview_id):

    interview = Interview.objects.get(pk=interview_id)

    context = {
        'assessment': False,
        'interview': interview,
        'finished': request.GET.get('finished'),
        'unauthorized': request.GET.get('unauthorized'),
        'completed': interview_is_completed(interview),
        'status': interview_status(interview),
        'can_start': datetime.now(interview.timezone) >= interview.timezone.localize(interview.start),
        'results': '',
    }    

    if context['completed']:
        results = Result.objects.filter(interview=interview)
        context['results'] = results

    return render(
        request,
        'app/interview/interview.html',
        context=context
    )


@login_required
def edit_interview(request, interview_id):

    interview = Interview.objects.get(pk=interview_id)

    context = {
        'interview': interview,
        'title': 'Edit interview',
        'saved': False,
        'success_msg': 'Changes saved successfully.'
    }

    interview_form = InterviewForm(instance=interview)
    CompetenciesFormSet = modelformset_factory(Competency, form=CompetencyForm)
    competencies_formset = CompetenciesFormSet(queryset=interview.competencies.all())
    candidate_form = CandidateForm(instance=interview.candidate) 
    AssessorFormSet = modelformset_factory(Employee, form=AssessorForm)
    assessor_formset = AssessorFormSet(queryset=interview.assessors.all())

    if request.method == "POST":

        if interview_form.is_valid():
            interview_form.save()
            context['saved'] = True
        else:
            context['errors'] = interview_form.errors
    
    context['interview_form'] = interview_form
    context['competencies_formset'] = competencies_formset
    context['candidate_form'] = candidate_form
    context['assessor_formset'] = assessor_formset

    return render(
        request,
        'app/individual/edit/edit_interview.html',
        context=context
    )

@login_required
def start_interview(request, interview_id):

    interview = Interview.objects.get(pk=interview_id)

    if not interview_is_completed(interview) and \
      interview_status(interview) != 'Finished':

        competencies = interview.competencies.all()
        competencies_with_choices = [ 
            { 
                'id': c.pk,
                'name': c.name, 
                'choices': list(range(c.min_points, c.max_points+1))
            } for c in competencies 
        ]

        context = {
            'interview': interview,
            'competencies': competencies_with_choices,
            'assessment': False,
        }


        return render(
            request,
            'app/interview/start_interview.html',
            context=context
        )

    else:
        return redirect(reverse('interviews:interview', interview_id), permanent=True)

@login_required
def assess_interview(request, interview_id):

    interview = Interview.objects.get(pk=interview_id)

    context = {
        'interview': interview,
        'title': 'Edit interview',
        'saved': False,
        'success_msg': 'Changes saved successfully.'
    }

    interview_form = InterviewForm(instance=interview)
    candidate_form = CandidateForm(instance=interview.candidate) 
    AssessorFormSet = modelformset_factory(Assessor, form=AssessorForm)
    assessor_formset = AssessorFormSet(queryset=interview.assessors.all())

    if request.method == "POST":

        if interview_form.is_valid():
            interview_form.save()
            context['saved'] = True
        else:
            context['errors'] = interview_form.errors
    
    context['interview_form'] = interview_form
    context['candidate_form'] = candidate_form
    context['assessor_formset'] = assessor_formset

    return render(
        request,
        'app/individual/edit/edit_interview.html',
        context=context
    )

@login_required
def delete_interview(request, interview_id):

    if request.method == "POST":
        interview = Interview.objects.get(pk=interview_id)
        interview.delete()

        return redirect(reverse('interviews:dashboard') + '?deleted=True', permanent=True)


@login_required
def assessments(request):

    assessments = get_objects_for_user(request.user, 'api.view_assessment').order_by("-start_date")

    context = {
        "assessments": assessments,
        "deleted": request.GET.get('deleted'),
    }

    return render(
        request,
        'app/assessments/assessments.html',
        context=context
    )


@login_required
def assessment(request, assessment_id):
        
    assessment = Assessment.objects.get(pk=assessment_id)
    interview_types = AssessmentInterviewType.objects.filter(assessment=assessment)
    candidates = Candidate.objects.filter(user__groups__name=assessment.group_name(group_type="candidate"))
    interviews = AssessmentInterview.objects.filter(timeslot__assessment_day__schedule__assessment=assessment)

    schedule = Schedule.objects.get(assessment=assessment)

    progress_per_day = [
        { 
            'value': assessment_progress(assessment, day.date),
            'date': day.date
        } for day in schedule.days.all()
    ]

    context = {
        'assessment': assessment,
        'interview_types': interview_types,
        'candidates': candidates,
        'interviews': interviews,
        'schedule': schedule,
        'status': assessment_status(assessment),
        'progress': assessment_progress(assessment),
        'progress_per_day': progress_per_day,
        'today': datetime.now().date(),
    }

    return render(
        request,
        'app/assessments/assessment.html',
        context=context
    )


@login_required
def edit_assessment(request, assessment_id):

    assessment = Assessment.objects.get(pk=assessment_id)
    competencies = assessment.competencies.all()
    interview_types = AssessmentInterviewType.objects.filter(assessment=assessment)
    candidates = Candidate.objects.filter(user__groups__name=assessment.group_name(group_type="candidate"))
    admins = Employee.objects.filter(user__groups__name=assessment.group_name(group_type="admin"))
    assessment_days = Schedule.objects.get(assessment=assessment).days.all()
    company = request.tenant

    context = {
        'assessment': assessment,
        'competencies': competencies,
        'interview_types': interview_types,
        'candidates': candidates,
        'admins': admins,
        'assessment_days': assessment_days,
        'changed': request.GET.get('changed'),
    }        

    form = AssessmentEditForm(
        instance=assessment,
        initial={
            'office': Office.objects.all(),
            'selected_office': assessment.office,
        }
    )

    if request.method == "POST":
        form = AssessmentEditForm(
            request.POST, 
            instance=assessment,
            initial={
                'office': Office.objects.all(),
                'selected_office': assessment.office,
            }
        )

        if form.is_valid():
            form.save()
            context['changed'] = True
        else:
            context['errors'] = form.errors
    
    context['form'] = form

    return render(
        request,
        'app/assessments/edit/edit_assessment.html',
        context=context
    )

@login_required
def delete_assessment(request, assessment_id):
    if request.method == "POST":
        assessment = Assessment.objects.get(pk=assessment_id)
        assessment.delete()

        return redirect(reverse('interviews:assessments') + '?deleted=True', permanent=True)


@login_required
def new_competency(request, assessment_id):

    assessment = Assessment.objects.get(pk=assessment_id)
    competency = Competency()

    context = {
        'assessment': assessment,
        'competency': competency,
    }

    form = CompetencyForm(instance=competency)

    if request.method == "POST":
        form = CompetencyForm(request.POST, instance=competency)

        if form.is_valid():
            competency = form.save()
            assessment.competencies.add(competency)
            return redirect(
                reverse(
                    'interviews:edit_assessment', 
                    kwargs={'assessment_id': assessment.pk}
                ) + '?changed=True', 
                permanent=True
            )
        else:
            context['errors'] = form.errors
    
    context['form'] = form

    return render(
        request,
        'app/assessments/edit/competency/competency.html',
        context=context
    )

@login_required
def edit_competency(request, assessment_id, competency_id):

    assessment = Assessment.objects.get(pk=assessment_id)
    competency = Competency.objects.get(pk=competency_id)

    context = {
        'assessment': assessment,
        'competency': competency,
    }

    form = CompetencyForm(
        instance=competency,
    )

    if request.method == "POST":
        form = CompetencyForm(request.POST, instance=competency)

        if form.is_valid():
            form.save()
            context['saved'] = True
            return redirect(
                reverse(
                    'interviews:edit_assessment', 
                    kwargs={'assessment_id': assessment.pk}
                ) + '?changed=True', 
                permanent=True
            )
        else:
            context['errors'] = form.errors
    
    context['form'] = form

    return render(
        request,
        'app/assessments/edit/competency/competency.html',
        context=context
    )

@login_required
def delete_competency(request, assessment_id, competency_id):

    if request.method == "POST":
        competency = Competency.objects.get(pk=competency_id)
        competency.delete()

        return redirect(
            reverse(
                'interviews:edit_assessment', 
                kwargs={'assessment_id': assessment_id}
            ) + '#competencies?changed=True', 
            permanent=True
        )

@login_required
def new_interview_type(request, assessment_id):

    assessment = Assessment.objects.get(pk=assessment_id)
    interview_type = AssessmentInterviewType(assessment=assessment)

    context = {
        'assessment': assessment,
        'interview_type': interview_type,
    }

    form = InterviewTypeEditForm(
        instance=interview_type,
        initial={
            'assessment': assessment
        }
    )

    if request.method == "POST":
        form = InterviewTypeEditForm(
            request.POST,
            request.FILES, 
            instance=interview_type,
            initial={
                'assessment': assessment
            }
        )

        if form.is_valid():
            form.save()
            context['saved'] = True
            return redirect(
                reverse(
                    'interviews:edit_assessment', 
                    kwargs={'assessment_id': assessment.pk}
                ) + '#interview_types?changed=True', 
                permanent=True
            )
        else:
            context['errors'] = form.errors
    
    context['form'] = form

    return render(
        request,
        'app/assessments/edit/interview_type/interview_type.html',
        context=context
    )

@login_required
def edit_interview_type(request, assessment_id, interview_type_id):

    assessment = Assessment.objects.get(pk=assessment_id)
    interview_type = AssessmentInterviewType.objects.get(pk=interview_type_id)

    context = {
        'assessment': assessment,
        'interview_type': interview_type,
    }

    form = InterviewTypeEditForm(
        instance=interview_type,
        initial={
            'competencies': assessment.competencies.all(),
        }
    )

    if request.method == "POST":
        form = InterviewTypeEditForm(
            request.POST,
            request.FILES,
            instance=interview_type,
            initial={
                'competencies': assessment.competencies.all(),
            }
        )

        if form.is_valid():
            form.save()
            context['saved'] = True
            return redirect(
                reverse(
                    'interviews:edit_assessment',
                    kwargs={'assessment_id': assessment.pk}
                ) + '#interview_types?changed=True',
                permanent=True
            )
        else:
            context['errors'] = form.errors
    
    context['form'] = form

    return render(
        request,
        'app/assessments/edit/interview_type/interview_type.html',
        context=context
    )

@login_required
def delete_interview_type(request, assessment_id, interview_type_id):

    if request.method == "POST":
        interview_type = AssessmentInterviewType.objects.get(pk=interview_type_id)
        interview_type.delete()

        return redirect(
            reverse(
                'interviews:edit_assessment',
                kwargs={'assessment_id': assessment_id}
            ) + '#interview_types?changed=True',
            permanent=True
        )

@login_required
def new_candidate(request, assessment_id):

    assessment = Assessment.objects.get(pk=assessment_id)
    candidate = Candidate()

    context = {
        'assessment': assessment,
        'candidate': candidate,
    }

    form = CandidateEditForm(instance=candidate)

    if request.method == "POST":
        form = CandidateEditForm(request.POST, instance=candidate)

        if form.is_valid():
            form.save()

            assessment.add_user(candidate, role="candidate")
            context['saved'] = True

            return redirect(
                reverse(
                    'interviews:edit_assessment', 
                    kwargs={'assessment_id': assessment.pk}
                ) + '#participants?changed=True',
                permanent=True
            )
        else:
            context['errors'] = form.errors
    
    context['form'] = form

    return render(
        request,
        'app/assessments/edit/candidate/candidate.html',
        context=context
    )

@login_required
def edit_candidate(request, assessment_id, candidate_id):

    assessment = Assessment.objects.get(pk=assessment_id)
    candidate = Candidate.objects.get(pk=candidate_id)

    context = {
        'assessment': assessment,
        'candidate': candidate,
    }

    form = CandidateEditForm(instance=candidate)

    if request.method == "POST":
        form = CandidateEditForm(request.POST, instance=candidate)

        if form.is_valid():
            form.save()
            return redirect(
                reverse(
                    'interviews:edit_assessment',
                    kwargs={'assessment_id': assessment.pk}
                ) + '#participants?changed=True',
                permanent=True
            )
        else:
            context['errors'] = form.errors
    
    context['form'] = form

    return render(
        request,
        'app/assessments/edit/candidate/candidate.html',
        context=context
    )

@login_required
def delete_candidate(request, assessment_id, candidate_id):

    if request.method == "POST":
        candidate = Candidate.objects.get(pk=candidate_id)
        candidate.delete()

        return redirect(
            reverse(
                'interviews:edit_assessment', 
                kwargs={'assessment_id': assessment_id}
            ) + '#participants?changed=True',
            permanent=True
        )

@login_required
def logs_assessment(request, assessment_id):

    assessment = Assessment.objects.get(pk=assessment_id)
    logs = AssessmentLogEvent.objects.filter(interview__timeslot__assessment_day__schedule__assessment=assessment)

    context = {
        'assessment': assessment,
        'logs': logs,
    }

    return render(
        request,
        'app/assessments/logs/logs.html',
        context=context
    )

@login_required
def results_assessment(request, assessment_id):

    assessment = Assessment.objects.get(pk=assessment_id)
    results = AssessmentInterviewResult.objects.filter(interview__timeslot__assessment_day__schedule__assessment=assessment)

    interview_types = assessment.interview_types.all()
    competencies = []
    for it in interview_types:
        for c in it.competencies.all():
            if c not in competencies:
                competencies.append(c)

    context = {
        'assessment': assessment,
        'results': results,
        'competencies': competencies,
        'interview_types': interview_types,
    }

    return render(
        request,
        'app/assessments/results/results.html',
        context=context
    )

@login_required
def edit_schedule(request, assessment_day_id):

    assessment_day = AssessmentDay.objects.get(pk=assessment_day_id)
    interviews = AssessmentInterview.objects.filter(timeslot__assessment_day=assessment_day)

    context = {
        'assessment_day': assessment_day,
        'interviews': interviews,
        'changed': request.GET.get('changed'),
    }

    return render(
        request,
        'app/assessments/edit/schedule/edit_schedule.html',
        context=context
    )

@login_required
def schedule_add_timeslot(request, assessment_day_id):

    assessment_day = AssessmentDay.objects.get(pk=assessment_day_id)

    context = {
        'title': 'Add a timeslot',
        'assessment_day': assessment_day,
    }

    timeslot = Timeslot(assessment_day=assessment_day)
    form = TimeslotForm(instance=timeslot)

    if request.method == "POST":
        form = TimeslotForm(request.POST, instance=timeslot)

        if form.is_valid():
            form.save()
            return redirect(
                reverse(
                    'interviews:edit_schedule', 
                    kwargs={'assessment_day_id':assessment_day.pk}
                ) + '?changed=True',
                permanent=True
            )
        else:
            context['errors'] = form.errors
    
    context['form'] = form

    return render(
        request,
        'app/assessments/edit/schedule/timeslot.html',
        context=context
    )

@login_required
def edit_timeslot(request, timeslot_id):

    timeslot = Timeslot.objects.get(pk=timeslot_id)

    context = {
        'title': 'Edit timeslot',
        'assessment_day': timeslot.assessment_day
    }

    form = TimeslotForm(instance=timeslot)

    if request.method == "POST":
        form = TimeslotForm(request.POST, instance=timeslot)

        if form.is_valid():
            form.save()
            return redirect(
                reverse(
                    'interviews:edit_schedule', 
                    kwargs={'assessment_day_id': timeslot.assessment_day.pk}
                ) + '/?changed=True',
                permanent=True
            )
        else:
            context['errors'] = form.errors
    
    context['form'] = form

    return render(
        request,
        'app/assessments/edit/schedule/timeslot.html',
        context=context
    )

@login_required
def schedule_remove_timeslot(request, timeslot_id):
    if request.method == "POST":
        timeslot = Timeslot.objects.get(pk=timeslot_id)
        a_d_id = timeslot.assessment_day.pk
        timeslot.delete()

        return redirect(
            reverse(
                'interviews:edit_schedule',
                kwargs={'assessment_day_id': a_d_id}
            ) + '/?changed=True',
            permanent=True
        )

@login_required
def schedule_add_candidate(request, assessment_day_id):

    assessment_day = AssessmentDay.objects.get(pk=assessment_day_id)
    candidates = Candidate.objects.filter(user__groups__name=assessment_day.schedule.assessment.group_name())

    for day in assessment_day.schedule.days.all():
        candidates = [ c for c in candidates if c not in day.candidates.all() ]

    context = {
        'title': 'Add candidate',
        'assessment_day': assessment_day
    }

    form = AddCandidateForm(initial={'candidates': candidates})

    if request.method == "POST":
        form = AddCandidateForm(request.POST, initial={'candidates': candidates})

        if form.is_valid():
            assessment_day.candidates.add(Candidate.objects.get(user__username=request.POST['candidates']))
            return redirect(
                reverse(
                    'interviews:edit_schedule',
                    kwargs={'assessment_day_id': assessment_day.pk}
                    ) + '/?changed=True',
                permanent=True
            )
        else:
            context['errors'] = form.errors
    
    context['form'] = form

    return render(
        request,
        'app/assessments/edit/schedule/add_candidate.html',
        context=context
    )

@login_required
def schedule_remove_candidate(request, assessment_day_id, candidate_id):
    if request.method == "POST":
        assessment_day = AssessmentDay.objects.get(pk=assessment_day_id)
        candidate = Candidate.objects.get(pk=candidate_id)

        assessment_day.candidates.remove(candidate)
        return redirect(
            reverse(
                'interviews:edit_schedule',
                kwargs={'assessment_day_id': assessment_day_id}
                ) + '/?changed=True',
            permanent=True
        )

@login_required
def schedule_add_interview(request, candidate_id, timeslot_id):

    timeslot = Timeslot.objects.get(pk=timeslot_id)
    candidate = Candidate.objects.get(pk=candidate_id)

    context = {
        'title': 'Add interview',
        'assessment_day': timeslot.assessment_day,
        'candidate': candidate,
        'timeslot': timeslot,
        'new': True,
    }

    form = ScheduleInterviewForm(
        initial={
            'candidate': candidate,
            'timeslot': timeslot,
        }
    )


    if request.method == "POST":
        form = ScheduleInterviewForm(
            request.POST,
            initial={
                'candidate': candidate,
                'timeslot': timeslot
            })

        if form.is_valid():
            form.save()
            return redirect(
                reverse(
                    'interviews:edit_schedule',
                    kwargs={'assessment_day_id': timeslot.assessment_day.pk}
                    ) + '/?changed=True',
                permanent=True
            )
        else:
            context['errors'] = form.errors
    
    # Remove all the interview types that have already been assigned to the candidate
    form.fields['interview_type'].queryset = AssessmentInterviewType.objects.filter(
        assessment=timeslot.assessment_day.schedule.assessment
    ).exclude(interviews__candidate=candidate)

    context['form'] = form

    return render(
        request,
        'app/assessments/edit/schedule/interview.html',
        context=context
    )

@login_required
def schedule_edit_interview(request, interview_id):

    interview = AssessmentInterview.objects.get(pk=interview_id)

    context = {
        'title': 'Edit interview',
        'assessment_day': interview.timeslot.assessment_day,
        'interview': interview,
    }

    form = ScheduleInterviewForm(instance=interview)

    if request.method == "POST":
        form = ScheduleInterviewForm(request.POST, instance=interview)

        if form.is_valid():
            form.save()
            return redirect(
                reverse(
                    'interviews:edit_schedule',
                    kwargs={'assessment_day_id': interview.timeslot.assessment_day.pk}
                    ) + '/?changed=True',
                permanent=True
            )
        else:
            context['errors'] = form.errors
    
    context['form'] = form

    return render(
        request,
        'app/assessments/edit/schedule/interview.html',
        context=context
    )

@login_required
def schedule_remove_interview(request, interview_id):

    interview = AssessmentInterview.objects.get(pk=interview_id)
    a_d_id = interview.timeslot.assessment_day.pk
    interview.delete()
    return redirect(
        reverse(
            'interviews:edit_schedule',
            kwargs={'assessment_day_id': a_d_id}
            ) + '/?changed=True',
        permanent=True
    )


@login_required
def assessment_interview(request, assessment_interview_id):

    interview = AssessmentInterview.objects.get(pk=assessment_interview_id)
    timezone = interview.timeslot.assessment_day.schedule.assessment.office.timezone

    context = {
        'assessment': True,
        'interview': interview,
        'finished': request.GET.get('finished'),
        'unauthorized': request.GET.get('unauthorized'),
        'completed': interview_is_completed(interview, assessment=True),
        'status': interview_status(interview, assessment=True),
        'can_start': datetime.now(timezone) >= interview.start_time(unformatted=True),
        'results': '',
    }

    if context['completed']:
        results = AssessmentInterviewResult.objects.filter(interview=interview)
        context['results'] = results

    return render(
        request,
        'app/interview/interview.html',
        context=context
    )

@login_required
def start_assessment_interview(request, assessment_interview_id):

    assessment_interview = AssessmentInterview.objects.get(pk=assessment_interview_id)

    if not interview_is_completed(assessment_interview, assessment=True) and \
      interview_status(assessment_interview, assessment=True) != 'Finished':

        competencies = assessment_interview.interview_type.competencies.all()
        competencies_with_choices = [ 
            { 
                'id': c.pk,
                'name': c.name, 
                'choices': list(range(c.min_points, c.max_points+1))
            } for c in competencies 
        ]

        context = {
            'interview': assessment_interview,
            'competencies': competencies_with_choices,
            'assessment': True,
            'interview_end': assessment_interview.end_time(unformatted=True).strftime('%b %d, %Y %H:%M:%s')
        }

        log_event = AssessmentLogEvent(
            by=request.user, 
            action='joined an interview',
            interview=assessment_interview
        )
        log_event.save()

        return render(
            request,
            'app/interview/start_interview.html',
            context=context
        )

    else:
        return redirect(
            reverse(
                'interviews:assessment_interview',
                kwargs={'assessment_interview_id': assessment_interview_id}
            ) + '?unauthorized=True',
            permanent=True
        )

@login_required
def assess_assessment_interview(request, assessment_interview_id):

    assessment_interview = AssessmentInterview.objects.get(pk=assessment_interview_id)
    assessor = Employee.objects.get(user=request.user)

    if request.method == "POST" and \
      assessor in assessment_interview.assessors.all() and \
      not interview_is_completed(assessment_interview):

        # For each parameter of the POST request
        for key, value in request.POST.items():

            # Check if the length matches
            # Competency IDs have a length of 36
            # If not 36, then is probably some junk or comment
            if len(key) == 36:

                try:
                    competency = Competency.objects.get(pk=key)
                except:
                    continue
                    
                result = AssessmentInterviewResult(
                    interview=assessment_interview,
                    assessor=assessor,
                    competency=competency,
                    score=value,
                    note=request.POST[key + '-note'],
                    created_by=request.user
                )
                result.save()

                log_event = AssessmentLogEvent(
                    by=request.user,
                    action='assessed a candidate',
                    interview=assessment_interview
                )
                log_event.save()

        return redirect(
            reverse(
                'interviews:assessment_interview',
                kwargs={'assessment_interview_id': assessment_interview_id}
            ) + '?finished=True',
            permanent=True
        )
    else:
        return redirect(
            reverse(
                'interviews:assessment_interview',
                kwargs={'assessment_interview_id': assessment_interview_id}
            ) + '?unauthorized=True',
            permanent=True
        )


@login_required
def company(request):

    offices = get_objects_for_user(request.user, 'api.view_office')

    context = {
        'company': request.tenant,
        'offices': offices,
        'changed': request.GET.get('changed'),
    }

    return render(
        request,
        'app/settings/company/company.html',
        context=context
    )

@login_required
def edit_company(request):

    context = {
        'company': request.tenant,
    }

    form = CompanyEditForm(instance=request.tenant)

    if request.method == "POST":
        form = CompanyEditForm(request.POST, request.FILES, instance=request.tenant)

        if form.is_valid():
            form.save()
            context['saved'] = True
            return redirect(
                reverse(
                    'interviews:company'
                ) + '?changed=True', 
                permanent=True
            )
        else:
            context['errors'] = form.errors
    
    context['form'] = form

    return render(
        request,
        'app/settings/company/edit_company.html',
        context=context
    )

@login_required
def office(request, office_id):

    office = Office.objects.get(pk=office_id)

    context = {
        'office': office,
        'company': request.tenant,
        'changed': request.GET.get('changed'),
    }

    return render(
        request,
        'app/settings/company/office/office.html',
        context=context
    )

@login_required
def new_office(request):

    context = {
        'company': request.tenant,
        'new': True,
        'next': request.GET.get('next')
    }

    office = Office()
    form = OfficeEditForm(
        instance=office,
        initial={
            'company': request.tenant
        }
    )

    if request.method == "POST":
        form = OfficeEditForm(
            request.POST,
            instance=office,
            initial={
                'company': request.tenant
            }
        )

        if form.is_valid():
            form.save()
            if context['next']:
                return redirect(context['next'], permanent=True)
            else:
                return redirect(
                    reverse(
                        'interviews:office',
                        kwargs={'office_id': office.pk}
                    ) + '?changed=True',
                    permanent=True
                )
        else:
            context['errors'] = form.errors
    
    context['form'] = form

    return render(
        request,
        'app/settings/company/office/edit_office.html',
        context=context
    )

@login_required
def edit_office(request, office_id):

    office = Office.objects.get(pk=office_id)

    context = {
        'office': office,
        'company': request.tenant,
    }

    form = OfficeEditForm(instance=office)

    if request.method == "POST":
        form = OfficeEditForm(request.POST, request.FILES, instance=office)

        if form.is_valid():
            form.save()
            context['saved'] = True
            return redirect(
                reverse(
                    'interviews:office',
                    kwargs={'office_id': office.pk}
                ) + '?changed=True',
                permanent=True
            )
        else:
            context['errors'] = form.errors
    
    context['form'] = form

    return render(
        request,
        'app/settings/company/office/edit_office.html',
        context=context
    )

@login_required
def new_room(request, office_id):

    office = Office.objects.get(pk=office_id)

    context = {
        'company': request.tenant,
        'office': office,
        'new': True,
    }

    room = Room()
    form = RoomEditForm(
        instance=room,
        initial={
            'office': office
        }
    )

    if request.method == "POST":
        form = RoomEditForm(
            request.POST,
            instance=room,
            initial={
                'office': office
            }
        )

        if form.is_valid():
            form.save()
            return redirect(
                reverse(
                    'interviews:office',
                    kwargs={'office_id': office.pk}
                ) + '?changed=True',
                permanent=True
            )
        else:
            context['errors'] = form.errors
    
    context['form'] = form

    return render(
        request,
        'app/settings/company/office/room/edit_room.html',
        context=context
    )

@login_required
def edit_room(request, office_id, room_id):

    room = Room.objects.get(pk=room_id)
    office = room.office
    company = request.tenant

    context = {
        'office': office,
        'company': company,
        'room': room,
    }

    form = RoomEditForm(instance=room)

    if request.method == "POST":
        form = RoomEditForm(request.POST, request.FILES, instance=room)

        if form.is_valid():
            form.save()
            context['saved'] = True
            return redirect(
                reverse(
                    'interviews:office',
                    kwargs={'company_id': company.pk, 'office_id': office.pk}
                ) + '?changed=True',
                permanent=True
            )
        else:
            context['errors'] = form.errors

    context['form'] = form

    return render(
        request,
        'app/settings/company/office/room/edit_room.html',
        context=context
    )

@login_required
def new_employee(request, office_id):

    office = Office.objects.get(pk=office_id)

    context = {
        'company': request.tenant,
        'office': office,
        'new': True,
    }

    employee = Employee(user=User())

    user_form = UserEditForm(instance=employee.user)
    employee_form = EmployeeEditForm(
        instance=employee, 
        initial={
            'office': office
        }
    )

    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=employee.user)
        employee_form = EmployeeEditForm(
            request.POST,
            instance=employee, 
            initial={
                'office': office
            }
        )

        if user_form.is_valid():
            if employee_form.is_valid():
                user = user_form.save(commit=False)
                user.username = user.email
                user.save()

                employee = employee_form.save(commit=False)
                employee.user = user
                employee.save()

                return redirect(
                    reverse(
                        'interviews:office',
                        kwargs={'office_id': office.pk}
                    ) + '?changed=True',
                    permanent=True
                )
            else:
                context['errors'] = employee_form.errors 
        else:
            context['errors'] = user_form.errors

    context['user_form'] = user_form
    context['employee_form'] = employee_form

    return render(
        request,
        'app/settings/company/office/employee/edit_employee.html',
        context=context
    )

@login_required
def edit_employee(request, office_id, employee_id):

    employee = Employee.objects.get(pk=employee_id)
    office = employee.office
    company = request.tenant

    context = {
        'office': office,
        'company': company,
        'employee': employee,
    }

    user_form = UserEditForm(instance=employee.user)
    employee_form = EmployeeEditForm(instance=employee)

    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=employee.user)
        employee_form = EmployeeEditForm(request.POST, instance=employee)

        if user_form.is_valid():
            if employee_form.is_valid():
                user_form.save()
                employee_form.save()

                return redirect(
                    reverse(
                        'interviews:office',
                        kwargs={'office_id': office.pk}
                    ) + '?changed=True',
                    permanent=True
                )
            else:
                context['errors'] = employee_form.errors 
        else:
            context['errors'] = user_form.errors

    context['user_form'] = user_form
    context['employee_form'] = employee_form

    return render(
        request,
        'app/settings/company/office/employee/edit_employee.html',
        context=context
    )

@login_required
def profile(request):

    context = {}

    form = ProfileForm(instance=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('interviews:dashboard') + '?changed=True', permanent=True)
        else:
            context['errors'] = form.errors

    context['form'] = form

    return render(
        request,
        'app/settings/profile.html',
        context=context
    )

@login_required
def settings(request):

    context = {}

    employee = Employee.objects.get(user=request.user)

    form = SettingsForm(initial={
        'agenda_view': employee.agenda_view,
        'timezone': employee.timezone
    })

    if request.method == 'POST':
        form = SettingsForm(
            request.POST,
            initial={
                'agenda_view': employee.agenda_view,
                'timezone': employee.timezone
            }
        )
        if form.is_valid():
            employee.timezone = form.cleaned_data['timezone']
            employee.agenda_view = form.cleaned_data['agenda_view']
            employee.save()
            return redirect(reverse('interviews:dashboard') + '?changed=True', permanent=True)
        else:
            context['errors'] = form.errors

    context['form'] = form

    return render(
        request,
        'app/settings/settings.html',
        context=context
    )
