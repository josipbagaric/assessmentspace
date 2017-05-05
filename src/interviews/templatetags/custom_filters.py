from django import template
from api.models import AssessmentInterviewResult

register = template.Library()

@register.filter
def abbrev(string):
    return ". ".join([ word[0] for word in string.split() ]) + '.'

@register.filter
def get_bootstrap_column(interview_type):
    
    num_competencies = len(interview_type.competencies.all())
    
    return int(12/num_competencies)


def get_score_for_results(results):
    """
    Returns the score from the list of results,
    together with the maximum possible score.
    """

    max_score = 0
    for r in results:
        for c in r.interview.interview_type.competencies.all():
            max_score += c.max_points

    score_sum = sum(r.score for r in results)

    return {
        'score': score_sum,
        'max': max_score
    }


@register.filter
def candidate_final_score(candidate, assessment):
    
    results = AssessmentInterviewResult.objects.filter(
        interview__candidate=candidate, 
        interview__timeslot__assessment_day__schedule__assessment=assessment
    )

    score = get_score_for_results(results)
    
    return "{}/{}".format(score['score'], score['max'])

@register.filter
def competency_score_for_interview_type(competency, interview_type):
    
    results = AssessmentInterviewResult.objects.filter(
        competency=competency, 
        interview__interview_type=interview_type
    )

    score = get_score_for_results(results)
    
    if score['score'] != 0:
        return "{0}/{1} - {2:.1f}%".format(score['score'], score['max'], (score['score']/score['max'])*100)
    else:
        return "0/{0} - 0%".format(score['max'])

@register.filter
def competency_total_score(competency):
    
    results = AssessmentInterviewResult.objects.filter(
        competency=competency
    )

    score = get_score_for_results(results)

    if score['score'] != 0:
        return "{0}/{1} - {2:.1f}%".format(score['score'], score['max'], (score['score']/score['max'])*100)
    else:
        return "0/{0} - 0%".format(score['max'])


@register.filter
def interview_type_total_success(interview_type):
    
    results = AssessmentInterviewResult.objects.filter(
        interview__interview_type=interview_type
    )

    score = get_score_for_results(results)
    
    if score['score'] != 0:
        return "{0:.1f}%".format((score['score']/score['max'])*100)
    else:
        return "0%"

@register.filter
def assessment_total_success(assessment):
    
    results = AssessmentInterviewResult.objects.filter(
        interview__timeslot__assessment_day__schedule__assessment=assessment
    )

    score = get_score_for_results(results)

    if score['score'] != 0:
        return "{0:.1f}%".format((score['score']/score['max'])*100)
    else:
        return "0%"