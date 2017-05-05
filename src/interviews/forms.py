from django.forms import ModelForm, formset_factory, BaseFormSet
from django import forms
from django.core.exceptions import ValidationError
from timezone_field import TimeZoneFormField

from api import models
from clients.models import Client, PLAN_CHOICES, Card
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django.forms.widgets import Input
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, Submit, HTML, Column, Row

## ABSTRACT FORMS
#-----------------
class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms[1:]:
            form.empty_permitted = True


class HorizontalModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(HorizontalModelForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.wrapper_class = 'row'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-6'
        self.helper.form_tag = False

class HorizontalForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(HorizontalForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.wrapper_class = 'row'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-6'
        self.helper.form_tag = False


## FORMS
#-------------
class CompanyEditForm(ModelForm):
    class Meta:
        model = Client
        exclude = ()

class OfficeEditForm(HorizontalModelForm):
    class Meta:
        model = models.Office
        exclude = ('created_by',)
        widgets = {
            'company': forms.HiddenInput(),
        }

class RoomEditForm(HorizontalModelForm):        
    class Meta:
        model = models.Room
        exclude = ('created_by',)
        widgets = {
            'office': forms.HiddenInput(),
        }

class UserEditForm(HorizontalModelForm):
    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
        )

class EmployeeEditForm(HorizontalModelForm):        
    class Meta:
        model = models.Employee
        exclude = ('user', 'agenda_view', 'created_by',)
        widgets = {
            'office': forms.HiddenInput(),
        }
 
class Html5TimeInput(Input): 
    input_type = 'time'

class Html5DateInput(Input): 
    input_type = 'date'

class Html5DatetimeInput(Input): 
    input_type = 'datetime-local'

class ProfileForm(HorizontalModelForm):
    class Meta:
        model = User
        exclude = ('password','groups','user_permissions','is_staff','is_active','date_joined','is_superuser','last_login')

class SettingsForm(HorizontalForm):

    agenda_view = forms.ChoiceField(choices=models.AGENDA_VIEW_CHOICES)
    timezone = TimeZoneFormField()

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)

        if 'initial' in kwargs:
            initial = kwargs.pop('initial')
            agenda_view = initial['agenda_view']
            timezone = initial['timezone']
            self.fields['agenda_view'].default = agenda_view
            self.fields['timezone'].default = timezone
 
class CandidateForm(ModelForm):

    email = forms.EmailField(required=True, max_length=100)
    first_name = forms.CharField(required=True, max_length=50)
    last_name = forms.CharField(required=True, max_length=50)

    def __init__(self, *args, **kwargs):
        super(CandidateForm, self).__init__(*args, **kwargs)

        if 'initial' in kwargs:
            initial = kwargs.pop('initial')
            self.fields['timezone'].default = initial['timezone']
            self.fields['country'].default = initial['country']

    class Meta:
        model = models.Candidate
        fields = ('email', 'first_name', 'last_name','cv', 'phone', 'address', 'city', 'country', 'timezone')

class CandidateMultipleFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(CandidateMultipleFormSetHelper, self).__init__(*args, **kwargs)

        self.form_method = 'post'
        self.wrapper_class = 'row'
        self.label_class = 'col-md-2'
        self.field_class = 'col-md-6'
        self.form_tag = False
        self.layout = Layout(
            HTML("""
                <div id="candidate-{{ forloop.counter0 }}" class="card 
                {% if not forloop.first %}
                    {% for f in form.forms %}
                        {% if forloop.counter == forloop.parentloop.counter and 'email' not in f.changed_data %}
                            hide
                        {% endif %}
                    {% endfor %}
                {% endif %}
                ">
                <div class="card-header" role="tab">
                  <h5 class="mb-0">
                    <a class="candidate-toggler" data-toggle="collapse" href="#collapse_candidate-{{ forloop.counter0 }}" data-toggle="collapse" id="text_candidate-{{ forloop.counter0 }}">
                      New Candidate <i class="icon ion-chevron-down"></i>
                    </a>
                  </h5>
                </div>

                <div id="collapse_candidate-{{ forloop.counter0 }}" class="collapse show" role="tabpanel" aria-labelledby="headingOne">
                  <div class="card-block">"""),
            'first_name',
            'last_name',
            'email',
            'cv',
            'phone',
            'address',
            'city',
            'country',
            'timezone',
            HTML("""</div></div></div>
                {% if forloop.revcounter == 1 %}
                <div id="addAnother" class="card">
                    <div class="card-header"  role="tab" >
                        <button type="button" class="btn btn-success">
                            <i class="icon ion-plus"></i>
                            Add another
                        </button>
                    </div>
                </div>
                {% endif %}"""),

            HTML("""
                {% if forloop.revcounter == 1 %}
                <div class="container">
                    <hr>
                    <a href="#" class="btn btn-default" data-toggle="modal" data-target="#confirmModal">Cancel</a>
                    <input type="submit" class="btn btn-primary" value="Next"/>
                </div>
                {% endif %}"""),
        ) 

class AssessorForm(ModelForm):
    email = forms.EmailField(required=True, max_length=100)
    first_name = forms.CharField(required=False, max_length=50)
    last_name = forms.CharField(required=False, max_length=50)

    class Meta:
        model = models.Employee
        fields = ('email', 'first_name', 'last_name')
        exclude = ('user',)

class InterviewForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(InterviewForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(
                    'name', css_class="col-md-7"
                ),
                Column(
                    'office', css_class="col-md-5"
                )
            ),
            Row(
                Column(
                    'date', css_class="col-md-3"
                ),
                Column(
                    'start', css_class="col-md-3"
                ),
                Column(
                    'end', css_class="col-md-3"
                ),
            ),
            'description',
            'assessor_material',
            'candidate_material',
        )

        self.fields['office'].initial = self.fields['office'].queryset[0]

    class Meta:
        model = models.Interview
        exclude = ('assessors','candidate','competencies','created_by')
        widgets = {
            'start': Html5TimeInput(),
            'end': Html5TimeInput(),
            'date': Html5DateInput(),
        }

class AssessmentEditForm(ModelForm):
    
    start_date = forms.DateField(widget=Html5DateInput())
    end_date = forms.DateField(widget=Html5DateInput())

    def __init__(self, *args, **kwargs):
        super(AssessmentEditForm, self).__init__(*args, **kwargs)

        if 'initial' in kwargs:
            initial = kwargs.pop('initial')

            self.fields['office'].queryset = initial['office']
            self.fields['office'].empty_label = "Choose an office"
            self.fields['office'].initial = initial['selected_office'].pk

    class Meta:
        model = models.Assessment
        exclude = ('competencies','created_by',)

class InterviewTypeEditForm(ModelForm):
    class Meta:
        model = models.AssessmentInterviewType
        exclude = ('assessment', 'created_by',)

class CandidateEditForm(HorizontalModelForm):
    class Meta:
        model = models.Candidate
        exclude = ('created_by',)

class ScheduleInterviewForm(HorizontalModelForm):
    class Meta:
        model = models.AssessmentInterview
        exclude = ('created_by',)
        widgets = {
            'candidate': forms.HiddenInput(),
            'timeslot': forms.HiddenInput(),
        }

class TimeslotForm(HorizontalModelForm):
    start_time = forms.TimeField(widget=Html5TimeInput())
    end_time = forms.TimeField(widget=Html5TimeInput())

    class Meta:
        model = models.Timeslot
        exclude = ('assessment_day',)

class AddCandidateForm(HorizontalForm):
    candidates = forms.ChoiceField(required=True)

    def __init__(self, *args, **kwargs):
        super(AddCandidateForm, self).__init__(*args, **kwargs)

        if 'initial' in kwargs:
            candidates = kwargs.pop('initial')['candidates']
            self.fields['candidates'] = forms.ChoiceField(choices=[(c,c) for c in candidates], required=True)



###### ASSESSMENT CREATION WIZARD ##########

class AssessmentDetailsForm(ModelForm):
    start_date = forms.DateField(widget=Html5DateInput())
    end_date = forms.DateField(widget=Html5DateInput())

    def __init__(self, *args, **kwargs):
        super(AssessmentDetailsForm, self).__init__(*args, **kwargs)

        if 'initial' in kwargs:
            office = kwargs.pop('initial')['office']
            self.fields['office'] = office
        else:
            self.fields['office'].initial = self.fields['office'].queryset[0]

    class Meta:
        model = models.Assessment
        exclude = ('competencies','created_by',)

class CompetencyForm(ModelForm):

    class Meta:
        model = models.Competency
        exclude = ('created_by',)
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Teamwork'}),
            'description': forms.Textarea(attrs={'rows': 2, 'placeholder': '(Optional)'}),
        }

class CompetencyMultipleFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(CompetencyMultipleFormSetHelper, self).__init__(*args, **kwargs)

        self.form_method = 'post'
        self.wrapper_class = 'row'
        self.label_class = 'col-md-2'
        self.field_class = 'col-md-6'
        self.form_tag = False
        self.layout = Layout(
            HTML("""
                <div id="competency-{{ forloop.counter }}" class="
                {% if not forloop.first %}
                    {% for f in form.forms %}
                        {% if forloop.counter == forloop.parentloop.counter and 'name' not in f.changed_data %}
                            hide
                        {% endif %}
                    {% endfor %}
                {% endif %}
                ">"""),
            HTML("<hr>"),
            'name',
            'min_points',
            'max_points',
            'description',
            HTML('</div>'),
            HTML("""
                {% if forloop.revcounter == 1 %}
                <div id="addAnother">
                    <hr>
                    <button type="button" class="btn btn-success">
                        <i class="icon ion-plus"></i>
                        Add another
                    </button>
                </div>
                <hr>
                <a href="#" class="btn btn-default" data-toggle="modal" data-target="#confirmModal">Cancel</a>
                <input type="submit" class="btn btn-primary" value="Next"/>
                {% endif %}"""),
        ) 

class AssessmentInterviewTypeForm(ModelForm):

    def __init__(self, *args, **kwargs):
        """
        Most Form Fields accept a dict argument `initial`, but ModelChoiceField apparently doesn't
        FormWizard makes this assumption when using `get_form_inital`
        """
        super(AssessmentInterviewTypeForm, self).__init__(*args, **kwargs)
        
        if 'initial' in kwargs:
            initial = kwargs.pop('initial')
            if initial:
                self.fields['competencies_assessed'] = initial['competencies']

    # Used instead of 'competencies' for storing competencies that
    # are not saved in the database yet.
    competencies_assessed = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = models.AssessmentInterviewType
        exclude = ('assessment', 'competencies', 'created_by',)
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Technical Interview'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }

class InterviewTypeMultipleFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(InterviewTypeMultipleFormSetHelper, self).__init__(*args, **kwargs)

        self.form_method = 'post'
        self.wrapper_class = 'row'
        self.label_class = 'col-md-2'
        self.field_class = 'col-md-6'
        self.form_tag = False
        self.layout = Layout(
            HTML("""
                <div id="type-{{ forloop.counter }}" class="
                {% if not forloop.first %}
                    {% for f in form.forms %}
                        {% if forloop.counter == forloop.parentloop.counter and 'name' not in f.changed_data %}
                            hide
                        {% endif %}
                    {% endfor %}
                {% endif %}
                ">"""),
            HTML("<hr>"),
            'name',
            'competencies_assessed',
            'color',
            'assessor_material',
            'candidate_material',
            'description',
            HTML('</div>'),
            HTML("""
                {% if forloop.revcounter == 1 %}
                <div id="addAnother">
                    <hr>
                    <button type="button" class="btn btn-success">
                        <i class="icon ion-plus"></i>
                        Add another
                    </button>
                </div>
                <hr>
                <a href="#" class="btn btn-default" data-toggle="modal" data-target="#confirmModal">Cancel</a>
                <input type="submit" class="btn btn-primary" value="Next"/>
                {% endif %}"""),
        ) 


###### COMPANY CREATION WIZARD ##########
class CompanyForm(ModelForm):

    class Meta:
        model = Client
        exclude = ('paid_until', 'on_trial', 'schema_name', 'plan')
        widgets = {
            'domain_url': forms.TextInput(attrs={'placeholder': 'example', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': '(Optional)'}),
        }

class AdminCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
        )

    def clean(self):
        cleaned_data = super(AdminCreationForm, self).clean()
        email = cleaned_data.get('email')
        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            raise ValidationError("User with this email already exists.")

class PlanForm(forms.Form):
    plan = forms.ChoiceField(choices=PLAN_CHOICES)

    def __init__(self, *args, **kwargs):
        super(PlanForm, self).__init__(*args, **kwargs)
        self.empty_permitted = True

    class Meta:
        widgets = {
            'plan': forms.RadioSelect(),
        }

class CardForm(ModelForm):

    class Meta:
        model = Card
        exclude = ('client',)


# used in urls.py FormWizard route
COMPANY_WIZARD_FORMS = [
    ('plan', PlanForm),
    ('details', CompanyForm),
    ('admin', AdminCreationForm),
    ('payment', CardForm),
]

ASSESSMENT_WIZARD_FORMS = [
    ('details', AssessmentDetailsForm),
    ('competencies', formset_factory(CompetencyForm, min_num=1, validate_min=True, extra=20)),
    ('interview_types', formset_factory(AssessmentInterviewTypeForm, formset=RequiredFormSet, min_num=1, validate_min=True, extra=20)),
    ('candidates', formset_factory(CandidateForm, formset=RequiredFormSet, min_num=1, validate_min=True, max_num=20, extra=20)),
]

INTERVIEW_WIZARD_FORMS = [
    ('details', InterviewForm),
    ('competencies', formset_factory(CompetencyForm, min_num=1, validate_min=True, max_num=20)),
    ('candidate', CandidateForm),
    ('assessors', formset_factory(AssessorForm, min_num=1, validate_min=True, max_num=20)),
]