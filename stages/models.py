from django.db import models
from organizations.models import Organization
from profiles_api.models import HrmsUsers
from roles.models import Roles
from email_templates.models import EmailTemplates
from organizations.models import ProcedureTypes
import uuid

Stage_Types = (
    (1, 'Dis-qualified'),
    (2, 'Job-Close'),
    (3, 'Job-Start')
)

class Stages(models.Model):
	title = models.CharField(max_length=200)
	procedure = models.ForeignKey(ProcedureTypes, on_delete=models.CASCADE)
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
	level = models.IntegerField(default=1, null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	is_email = models.BooleanField(default=True, null=True, blank=True)
	is_interview = models.BooleanField(default=False, null=True, blank=True)
	is_evaluation = models.BooleanField(default=False, null=True, blank=True)
	is_auto_sent_email = models.BooleanField(default=False, null=True, blank=True)
	email_template = models.ForeignKey(EmailTemplates, on_delete=models.CASCADE, blank=True, null=True)
	notify_to_admin=models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)



class StageTypeTemplates(models.Model):
	title = models.CharField(max_length=200)
	stage_type = models.IntegerField(choices=Stage_Types)
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
	level = models.IntegerField(default=1, null=True, blank=True)
	is_email = models.BooleanField(default=True, null=True, blank=True)
	is_auto_sent_email = models.BooleanField(default=False, null=True, blank=True)
	email_template = models.ForeignKey(EmailTemplates, on_delete=models.CASCADE, blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)