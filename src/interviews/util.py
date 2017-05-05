from api.models import AssessmentInterview, AssessmentInterviewResult, Result
from datetime import datetime, time
import pytz

def interview_is_completed(interview, assessment=False):

    if not assessment:
        results = Result.objects.filter(interview=interview)

        if len(results) >= len(interview.competencies.all()):
            return True
        else:
            return False

    else:
        results = AssessmentInterviewResult.objects.filter(interview=interview)

        if len(results) >= len(interview.interview_type.competencies.all()):
            return True
        else:
            return False


def interview_status(interview, assessment=False):

    start_time = interview.start_time(unformatted=True)
    end_time = interview.end_time(unformatted=True)

    if assessment:
        timezone = interview.timeslot.assessment_day.schedule.assessment.office.timezone
    else:
        timezone = interview.timezone

    if datetime.now(timezone) < start_time:
        return 'Not started yet'
    else:
        if datetime.now(timezone) < end_time and not interview_is_completed(interview, assessment=True if assessment else False):
            return 'In progress'
        else:
            return 'Finished'

def assessment_status(assessment):

    timezone = assessment.office.timezone

    start_time = timezone.localize(datetime.combine(assessment.start_date, time.min))
    end_time = timezone.localize(datetime.combine(assessment.end_date, time.max))

    if datetime.now(timezone) < start_time:
        return 'Not started yet'

    else:
        if datetime.now(timezone) < end_time:

            interviews = AssessmentInterview.objects.filter(timeslot__assessment_day__schedule__assessment=assessment)

            if len(interviews) == 0:
                return 'Not started yet'
            else:
                for interview in interviews:
                    if not interview_is_completed(interview, assessment=True):
                        return 'In progress'
                else:
                    return 'Complete'
        else:
            return 'Complete'

def assessment_progress(assessment, date=None):

    if not date:
        interviews = AssessmentInterview.objects.filter(
            timeslot__assessment_day__schedule__assessment=assessment
        )
        finished_interviews = [ interview for interview in interviews if interview_is_completed(interview, assessment=True) ]

    else:
        interviews = AssessmentInterview.objects.filter(
            timeslot__assessment_day__schedule__assessment=assessment, 
            timeslot__assessment_day__date=date
        )
        finished_interviews = [ interview for interview in interviews if interview_is_completed(interview, assessment=True) ]

    if interviews:
        if date:
            return int((len(finished_interviews)/len(interviews)*100)/len(assessment.schedule.days.all()))
        else:
            return int((len(finished_interviews)/len(interviews)*100))
    else:
        return 0
    