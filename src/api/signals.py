from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from guardian.shortcuts import assign_perm, remove_perm
from api.models import Assessment, Schedule, AssessmentDay
from django.core.exceptions import ObjectDoesNotExist

from datetime import datetime, timedelta

def create_assessment_group(instance, group_type="candidate"):
    """
    Call this from a signal when an obj requiring permission groups is created.
    *Currently, only new Assessment need groups created.*
    in:
        instance: Assessment instance
        admin: bool
    out:
        Group instance
    """
    group = Group(name=instance.group_name(group_type))
    group.save()
    return group

@receiver(post_save, sender=Assessment)
def create_assessment_perm_groups(sender, **kwargs):

    # Called when the assessment is created
    if kwargs.pop('created'):
        instance = kwargs.pop('instance')

        # create permission groups with their global permissions
        assessment_candidate_group = create_assessment_group(instance)
        assessment_assessor_group = create_assessment_group(instance, group_type="assessor")
        assessment_admin_group = create_assessment_group(instance, group_type="admin")

        view_permission = Permission.objects.get(codename="view_assessment")
        edit_permission = Permission.objects.get(codename="edit_assessment")

        assessment_candidate_group.permissions.add(view_permission)
        assessment_assessor_group.permissions.add(view_permission)
        assessment_admin_group.permissions.add(edit_permission)

        # Create schedule and assessment days
        schedule = Schedule(assessment=instance)
        schedule.save()

        num_days = (instance.end_date - instance.start_date).days + 1
        date_list = [instance.start_date + timedelta(days=x) for x in range(0, num_days)]

        for date in date_list:
            day = AssessmentDay(schedule=schedule, date=date)
            day.save()

    # Called when the assessment is updated
    else:
        instance = kwargs.pop('instance')
        
        schedule = Schedule.objects.get(assessment=instance)
        assessment_days = AssessmentDay.objects.filter(schedule=schedule)

        current_date_list = [ day.date for day in assessment_days]

        num_days = (instance.end_date - instance.start_date).days + 1
        target_date_list = [ instance.start_date + timedelta(days=x) for x in range(0, num_days) ]

        # If the dates of the assessment have changed
        if target_date_list != current_date_list:

            # Create new assessment days
            for date in target_date_list:
                if date not in current_date_list:
                    day = AssessmentDay(schedule=schedule, date=date)
                    day.save()

            # Delete any assessment days that have been removed
            for day in assessment_days:
                if day.date not in target_date_list:
                    day.delete()


@receiver(pre_delete, sender=Assessment)
def delete_assessment_perm_groups(sender, **kwargs):
    instance = kwargs.pop('instance')
    try:
        Group.objects.get(name=instance.group_name()).delete()
        Group.objects.get(name=instance.group_name(group_type="assessor")).delete()
        Group.objects.get(name=instance.group_name(group_type="admin")).delete()
    except ObjectDoesNotExist:
        pass


