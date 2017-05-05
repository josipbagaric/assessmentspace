from django.db import models
from django_countries.fields import CountryField
from django.core.validators import MaxValueValidator, MinValueValidator
from colorfield.fields import ColorField
from uuid import uuid4
from tinymce.models import HTMLField
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import User, Group
from datetime import datetime
from timezone_field import TimeZoneField
from django_markdown.models import MarkdownField
from phonenumber_field.modelfields import PhoneNumberField
from .validators import validate_pdf

import pytz

ROOM_SIZE_CHOICES = (
    ('S', 'Small'),
    ('M', 'Medium'),
    ('L', 'Large')
)

ACTION_CHOICES = (
    ('J', 'joined an interview'),
    ('A', 'assessed a candidate')
)

AGENDA_VIEW_CHOICES = (
    ('agendaDay', 'Day'),
    ('agendaWeek', 'Week'),
    ('month', 'Month'),
    ('listWeek', 'List')
)

class UUIDModel(models.Model):
    class Meta:
        abstract = True

    def short_id(self):
        return str(self.pk).split('-')[-1]

    def string_id(self):
        return str(self.pk)

    def __str__(self):
        return self.string_id()

    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    created = models.DateTimeField(auto_now_add=True, verbose_name='Created on')
    updated = models.DateTimeField(auto_now=True, verbose_name='Last updated')


class Office(UUIDModel):
    """
    Each assessment center has to be conducted on a certain office.
    """

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-name',)
        permissions = (
            ('view_office', 'Can view Office'),
            ('edit_office', 'Can edit Office'),
        )

    name = models.CharField(null=False, unique=True, max_length=100)
    address_line_1 = models.CharField(max_length=100, blank=True, null=True, verbose_name='Address')
    address_line_2 = models.CharField(max_length=100, blank=True, null=True, verbose_name='Apt/Suite')
    zip_code = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = CountryField()

    timezone = TimeZoneField(default='Europe/London')

    created_by = models.ForeignKey(User, null=True, related_name='offices', on_delete=models.CASCADE)


class Room(UUIDModel):
    """
    The room in which the interviews are conducted.
    """

    def __str__(self):
        return self.name + ' - ' + str(self.office)

    class Meta:
        ordering = ('-name',)
        permissions = (
            ('view_room', 'Can view Room'),
            ('edit_room', 'Can edit Room'),
        )

    name = models.CharField(max_length=100, null=False)
    building = models.CharField(max_length=100, null=True, blank=True)
    floor = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(
        max_length=20,
        null=False,
        choices=ROOM_SIZE_CHOICES,
        default='M',
        verbose_name='Room size',
    )
    note = HTMLField(blank=True, verbose_name='Note')

    office = models.ForeignKey(Office, null=False, related_name='rooms')

    created_by = models.ForeignKey(User, null=True, related_name='rooms', on_delete=models.CASCADE)

class Employee(UUIDModel):

    def __str__(self):
        return self.user.username

    def full_name(self):
        return ' '.join([self.user.first_name, self.user.last_name])

    class Meta:
        ordering = ('-user__date_joined',)
        permissions = (
            ('view_employee', 'Can view Employee'),
            ('edit_employee', 'Can edit Employee'),
        )

    user = models.OneToOneField(User, verbose_name='User')
    office = models.ForeignKey(Office, null=True, related_name='employees', on_delete=models.CASCADE) 
    timezone = TimeZoneField(default='Europe/London')

    agenda_view = models.CharField(
        max_length=100,
        null=False,
        choices=AGENDA_VIEW_CHOICES,
        default='listWeek',
        verbose_name='Default agenda view',
    )

class Candidate(UUIDModel):
    """
    Candidate is a person that has applied for a job interview and
    is a participant of an interview.
    """

    def __str__(self):
        return self.user.username

    def full_name(self):
        return ' '.join([self.user.first_name, self.user.last_name])

    class Meta:
        ordering = ('-user__date_joined',)
        permissions = (
            ('view_candidate', 'Can view Candidate'),
            ('edit_candidate', 'Can edit Candidate'),
        )

    user = models.OneToOneField(User, verbose_name='User')
    phone = PhoneNumberField(blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True, verbose_name='Address')
    city = models.CharField(max_length=1000, blank=True, null=True, verbose_name='City')
    country = CountryField()

    timezone = TimeZoneField(default='Europe/London')

    cv = models.FileField(upload_to="cv/", validators=[validate_pdf], default=None, blank=True, null=True, verbose_name="CV")
    note = HTMLField(blank=True, verbose_name='Note')

class Competency(UUIDModel):
    """
    Competency is best described as a virtue that will be rated on a candidate.

    On every interview, the Employee assesses a Candidate on a number of Competencies.
    """

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Competencies"

    name = models.CharField(null=False, unique=False, max_length=100)
    description = HTMLField(blank=True, verbose_name='Description')

    min_points = models.IntegerField(default=1, validators=[MaxValueValidator(10), MinValueValidator(1)])
    max_points = models.IntegerField(default=10, validators=[MaxValueValidator(10), MinValueValidator(1)])

    created_by = models.ForeignKey(User, null=True, related_name='competencies', on_delete=models.CASCADE)

class Interview(UUIDModel):
    """
    A Interview contains a candidate, and a number of assessors (Employees).
    A Interview is not a part of any interview campaign, but is an isolated occurence.
    """

    def __str__(self):
        return self.name

    def start_time(self, unformatted=False):
        start_time = self.timezone.localize(self.start)
        return start_time if unformatted else start_time.strftime('%Y-%m-%d %H:%M')

    def end_time(self, unformatted=False):
        end_time = self.timezone.localize(self.end)
        return end_time if unformatted else end_time.strftime('%Y-%m-%d %H:%M')

    def duration(self):
        return self.end_time(unformatted=True) - self.start_time(unformatted=True)

    class Meta:
        ordering = ('-start',)
        permissions = (
           ('view_interview', 'Can view Interview'),
           ('edit_interview', 'Can edit Interview'),
        )

    name = models.CharField(null=False, unique=True, max_length=100)
    description = MarkdownField(verbose_name='Description', blank=True)
    office = models.ForeignKey(Office, null=True, verbose_name='Office')

    assessors = models.ManyToManyField(Employee, verbose_name='Assessors')
    assessor_material = models.FileField(upload_to="material/assessor/", validators=[validate_pdf], default=None, blank=True, null=True)
    candidate = models.ForeignKey(Candidate, null=True, verbose_name='Candidate')
    candidate_material = models.FileField(upload_to="material/candidate/", validators=[validate_pdf], default=None, blank=True, null=True)

    competencies = models.ManyToManyField(Competency, verbose_name='Competencies')

    start = models.TimeField(verbose_name='Start Time')
    end = models.TimeField(verbose_name='End Time')

    date = models.DateTimeField(verbose_name='Date')

    created_by = models.ForeignKey(User, null=True, related_name='interviews', on_delete=models.CASCADE)

class Result(UUIDModel):
    """
    Result contains all the results for a certain Interview.
    """

    def __str__(self):
        return " - ".join([str(self.interview.candidate), str(self.interview), str(self.competency), str(self.score)])

    class Meta:
        ordering = ('-updated',)
        permissions = (
           ('view_result', 'Can view Result'),
           ('edit_result', 'Can edit Result'),
        )

    assesor = models.ForeignKey(Employee, null=False, verbose_name='Assessor')
    interview = models.ForeignKey(Interview, null=False, verbose_name='Interview')
    competency = models.ForeignKey(Competency, null=False, verbose_name='Competency')

    score = models.IntegerField(validators=[MaxValueValidator(10), MinValueValidator(1)])
    note = HTMLField(blank=True, verbose_name='Note')

    created_by = models.ForeignKey(User, null=True, related_name='results', on_delete=models.CASCADE)
    


###################################################################
###                  ASSESSMENT STUFF                          ####
###################################################################

class Assessment(UUIDModel):
    """
    Assessment object contains the information about the assessment.
    """

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-created',)
        permissions = (
            ('view_assessment', 'Can view Assessment'),
            ('edit_assessment', 'Can edit Assessment'),
        )

    def group_name(self, group_type="candidate"):
        """
        Fetches the name of the group.
        """
        qualifier = group_type if group_type in ('admin', 'assessor') else 'candidate'
        return ''.join([qualifier, ':', str(self.pk)])

    def add_user(self, user, role="candidate", admin=False):
        """
        Adds the user to a group in the assessment.
        Possible groups:
            - "candidate"
            - "assessor"
            - "admin"

        Default is "candidate".
        """
        if role == "candidate":
            g = Group.objects.get(name=self.group_name())
        elif role in ("assessor", "admin"):
            g = Group.objects.get(name=self.group_name(group_type="admin" if admin else "assessor"))
            
        user.groups.add(g)

    def remove_user(self, user, group_type):
        """
        Removes the user from a group of type "group_type".
        """
        group = Group.objects.get(name=self.group_name(group_type=group_type))
        try:
            user.groups.remove(group)
        except:
            pass

    name = models.CharField(null=False, unique=True, max_length=100)
    description = HTMLField(blank=True, verbose_name='Description')
    office = models.ForeignKey(Office, null=True, verbose_name='Office')
    start_date = models.DateField(verbose_name='Start Date')
    end_date = models.DateField(verbose_name='End Date')

    competencies = models.ManyToManyField(Competency, verbose_name='Competencies', related_name="assessments")

    public = models.BooleanField(null=False, default=False, verbose_name='Make assessment details visible to everyone in the company?')

    created_by = models.ForeignKey(User, null=True, related_name='assessments', on_delete=models.CASCADE)

class Schedule(models.Model):
    """
    Schedule model is used to contain all the information about the
    schedule for one assessment.

    It consists of interviews that are performed during a certain 
    time slot with a certain candidate.
    """

    def __str__(self):
        return "Schedule for " + str(self.assessment)

    assessment = models.OneToOneField(Assessment, null=False, related_name="schedule")

    created_by = models.ForeignKey(User, null=True, related_name='schedule', on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True, verbose_name='Created on')
    updated = models.DateTimeField(auto_now=True, verbose_name='Last updated')

class AssessmentDay(models.Model):
    """
    Assessment day is a part of a Schedule, and is used to contain all the information about that specific
    day of the assessment center.
    """
    def __str__(self):
        return " - ".join([str(self.schedule.assessment), str(self.date)])

    def num_interviews(self):
        counter = 0
        for timeslot in self.timeslots.all():
            counter += len(timeslot.interviews.all())
        return counter

    schedule = models.ForeignKey(Schedule, null=False, related_name='days')
    date = models.DateField()
    candidates = models.ManyToManyField(Candidate, blank=True)

class Timeslot(models.Model):
    """
    Timeslot contains the start and end time of different interviews.
    """

    def __str__(self):
        return " - ".join([str(self.assessment_day.schedule.assessment), str(self.assessment_day.date), str(self.start_time), str(self.end_time)])

    assessment_day = models.ForeignKey(AssessmentDay, null=False, related_name='timeslots')

    start_time = models.TimeField(verbose_name='Start time')
    end_time = models.TimeField(verbose_name='End time')

class RoleAffinity(UUIDModel):
    """
    RoleAffinity allows the interviewer to choose a role that he would
    prefer for the candidate to be placed. 

    Role affinities should only be used in cases there are more roles 
    that need to be filled, but require the same profile of candidate.

    Note: Only used in Assessment Centers.
    """

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Role affinities"

    name = models.CharField(null=False, unique=True, max_length=100)
    description = HTMLField(blank=True, verbose_name='Description')
    assessment = models.ForeignKey(Assessment, null=False , verbose_name='Assessment')

    created_by = models.ForeignKey(User, null=True, related_name='role_affinities', on_delete=models.CASCADE)

class AssessmentInterviewType(UUIDModel):
    """
    Each interview in an assessment has an interview type.
    """

    def __str__(self):
        return self.name

    name = models.CharField(null=False, max_length=100)
    description = HTMLField(blank=True, verbose_name='Description')

    assessment = models.ForeignKey(Assessment, null=False , verbose_name='Assessment', related_name="interview_types")

    competencies = models.ManyToManyField(Competency, verbose_name='Competencies', related_name="interview_types")
    color = ColorField(default='#00FF00')

    assessor_material = models.FileField(upload_to="material/assessor/", validators=[validate_pdf], default=None, blank=True, null=True)
    candidate_material = models.FileField(upload_to="material/candidate/", validators=[validate_pdf], default=None, blank=True, null=True)

    created_by = models.ForeignKey(User, null=True, related_name='assessment_interview_types', on_delete=models.CASCADE)

class AssessmentInterview(UUIDModel):
    """
    An AssessmentInterview contains a candidate, and a number of assessors (Employees).
    It is only used in assessment centers, not in individual interviews.
    """

    def __str__(self):
        return " - ".join([str(self.candidate), str(self.interview_type), str(self.timeslot.assessment_day.schedule.assessment)])

    def start_time(self, unformatted=False):
        timezone = self.timeslot.assessment_day.schedule.assessment.office.timezone
        start_time = timezone.localize(datetime.combine(self.timeslot.assessment_day.date, self.timeslot.start_time))
        return start_time if unformatted else start_time.strftime('%Y-%m-%d %H:%M')

    def end_time(self, unformatted=False):
        timezone = self.timeslot.assessment_day.schedule.assessment.office.timezone
        end_time = timezone.localize(datetime.combine(self.timeslot.assessment_day.date, self.timeslot.end_time))
        return end_time if unformatted else end_time.strftime('%Y-%m-%d %H:%M')

    def duration(self):
        return self.end_time(unformatted=True) - self.start_time(unformatted=True)

    class Meta:
        permissions = (
           ('view_assessment_interview', 'Can view AssessmentInterview'),
           ('edit_assessment_interview', 'Can edit AssessmentInterview'),
        )

    assessors = models.ManyToManyField(Employee, verbose_name='Assessors')
    room = models.ForeignKey(Room, null=True, verbose_name='Room', related_name='assessment_room')

    candidate = models.ForeignKey(Candidate, null=False, verbose_name='Candidate')
    candidate_room = models.ForeignKey(Room, null=True, verbose_name='Candidate Room', related_name='assessment_candidate_room')

    interview_type = models.ForeignKey(AssessmentInterviewType, null=False, related_name="interviews")

    timeslot = models.ForeignKey(Timeslot, null=False, related_name='interviews')

    note = HTMLField(blank=True, verbose_name='Note')

    created_by = models.ForeignKey(User, null=True, related_name='assessment_interviews', on_delete=models.CASCADE)

class AssessmentInterviewResult(UUIDModel):
    """
    AssessmentInterviewResult contains all the results for a certain AssessmentInterview.
    """

    def __str__(self):
        return " - ".join([str(self.interview), "Score: " + str(self.score)])

    class Meta:
        ordering = ('-updated',)
        permissions = (
           ('view_assessment_interview_result', 'Can view AssessmentInterviewResult'),
           ('edit_assessment_interview_result', 'Can edit AssessmentInterviewResult'),
        )

    assessor = models.ForeignKey(Employee, null=False, verbose_name='Assessor')
    interview = models.ForeignKey(AssessmentInterview, null=False, verbose_name='Interview')
    competency = models.ForeignKey(Competency, null=False, verbose_name='Competency')

    score = models.IntegerField(validators=[MaxValueValidator(10), MinValueValidator(1)])
    note = HTMLField(blank=True, verbose_name='Note')

    created_by = models.ForeignKey(User, null=True, related_name='assessment_interview_results', on_delete=models.CASCADE)

class ExtraEventType(UUIDModel):
    """
    An Assessment may contain events that are not interviews, such as a Welcome session, 
    Lunch Break or Debrief session.

    In case an assessment administrator wants to input these events into the calendar as well,
    he can create and ExtraEvent.

    ExtraEventType defines the type of the extra event.
    """

    def __str__(self):
        return self.name

    name = models.CharField(null=False, unique=True, max_length=100)
    description = HTMLField(blank=True, verbose_name='Description')

    assessment = models.ForeignKey(Assessment, null=False , verbose_name='Assessment')

    color = ColorField(default='#00FF00')

    created_by = models.ForeignKey(User, null=True, related_name='extra_event_types', on_delete=models.CASCADE)

class ExtraEvent(UUIDModel):
    """
    An ExtraEvent contains the information on when a certain
    candidate has a special event planned, i.e. an event that is not an interview.
    """

    def __str__(self):
        return self.interview_type + " " + self.assessment

    class Meta:
        ordering = ('-start_time',)

    assessment = models.ForeignKey(Assessment, null=False , verbose_name='Assessment')
    extra_event_type = models.ForeignKey(ExtraEventType, null=False, verbose_name='Type')
    description = HTMLField(blank=True, verbose_name='Description')

    candidate = models.ForeignKey(Candidate, null=False, verbose_name='Candidate')
    room = models.ForeignKey(Room, null=True, verbose_name='Room')

    start_time = models.DateTimeField(verbose_name='Start Time')
    end_time = models.DateTimeField(verbose_name='End Time')

    created_by = models.ForeignKey(User, null=True, related_name='extra_events', on_delete=models.CASCADE)


class AssessmentLogEvent(UUIDModel):

    def __str__(self):
        return " ".join([self.by.username, self.action, str(self.interview)])

    class Meta:
        ordering = ('-created',)
        permissions = (
           ('view_assessment_log_event', 'Can view AssessmentLogEvent'),
           ('edit_assessment_log_event', 'Can edit AssessmentLogEvent'),
        )

    by = models.ForeignKey(User, null=False, related_name='log_event', on_delete=models.CASCADE)

    action = models.CharField(
        max_length=100,
        null=False,
        choices=ACTION_CHOICES,
        default='J',
        verbose_name='Action',
    )

    interview = models.ForeignKey(AssessmentInterview, null=False, related_name='log_event')


