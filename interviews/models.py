from django.db import models
from organizations.models import Organization
from profiles_api.models import HrmsUsers
from roles.models import Roles
from email_templates.models import EmailTemplates
from organizations.models import ProcedureTypes
from candidates.models import Candidates, CandidateJobs
from stages.models import Stages
from time_intervals.models import TimeSlots
import uuid

interview_statuses = (
	(1, 'To be set'),
	(2, 'Interview Set'),
	(3, 'Interview Start'),
	(4, 'Interview Completed'),
	(5, 'Cancel the Interview')
)


class InterviewMode(models.Model):
	title = models.CharField(max_length=50)
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class InterviewMedium(models.Model):
    title = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CandidateInterviews(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
	candidate = models.ForeignKey(Candidates, on_delete=models.CASCADE)
	candidate_job = models.ForeignKey(CandidateJobs, on_delete=models.CASCADE)
	stage = models.ForeignKey(Stages, on_delete=models.CASCADE)
	interviewer = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, null=True, blank=True)
	interview_date = models.DateField(null=True, blank=True)
	interview_time_slot = models.ForeignKey(TimeSlots, on_delete=models.CASCADE, null=True, blank=True)
	interview_mode = models.ForeignKey(InterviewMode, on_delete=models.CASCADE, null=True, blank=True)
	status = models.IntegerField(choices=interview_statuses, default=1)
	start_date_time = models.DateTimeField(null=True, blank=True)
	is_completed = models.BooleanField(default=False, null=True, blank=True)
	complete_date_time = models.DateTimeField(null=True, blank=True)
	is_cancel = models.BooleanField(default=False, null=True, blank=True)
	interview_url=models.TextField(null=True,blank=True)
	interview_medium=models.ForeignKey(InterviewMedium,on_delete=models.CASCADE,null=True,blank=True)
	comments=models.TextField(null=True,blank=True)
	reason_for_cancel = models.TextField(null=True, blank=True)
	is_reschedule = models.BooleanField(default=False)
	reschedule_date = models.DateTimeField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class CandidateInterviewLogs(models.Model):
	candidate_interview = models.ForeignKey(CandidateInterviews, on_delete=models.CASCADE)
	user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
	action = models.CharField(max_length=100, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
