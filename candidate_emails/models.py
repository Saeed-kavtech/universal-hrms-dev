from django.db import models
from organizations.models import Organization, ProcedureTypes
from profiles_api.models import HrmsUsers
from candidates.models import Candidates, CandidateJobs
from stages.models import Stages, StageTypeTemplates
from email_templates.models import EmailTemplates
from helpers.image_uploads import upload_candidate_attachments
import uuid

email_statuses = (
	(1, 'To be set'),
	(2, 'Email Set'),
	(3, 'Email Save.'),
	(4, 'Sent'),
	(5, 'Cancel')
)


#Email Templates Models for candidate
class CandidateEmails(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
	candidate = models.ForeignKey(Candidates, on_delete=models.CASCADE)
	candidate_job = models.ForeignKey(CandidateJobs, on_delete=models.CASCADE, blank=True, null=True)
	stage = models.ForeignKey(Stages, on_delete=models.CASCADE, blank=True, null=True, related_name="candidate_stages_emails") 
	stage_type = models.ForeignKey(StageTypeTemplates, on_delete=models.CASCADE, blank=True, null=True, related_name="candidate_stage_type_emails") 
	email_template = models.ForeignKey(EmailTemplates, on_delete=models.CASCADE)
	status = models.IntegerField(choices=email_statuses, default=1)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class CandidateEmailAttachments(models.Model):
	candidate_email = models.ForeignKey(CandidateEmails, on_delete=models.CASCADE)
	attachment = models.FileField(upload_to=upload_candidate_attachments, null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class CandidateEmailBody(models.Model):
	candidate_email = models.ForeignKey(CandidateEmails, on_delete=models.CASCADE)
	subject = models.CharField(max_length=200, null=True, blank=True)
	body = models.TextField(blank=True, null=True)
	footer = models.TextField(blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class CandidateEmailLogs(models.Model):
	candidate_email = models.ForeignKey(CandidateEmails, on_delete=models.CASCADE)
	action = models.CharField(max_length=100) # it may be a status or any action
	action_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)