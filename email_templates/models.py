from django.db import models
from employees.models import Employees
from organizations.models import Organization, ProcedureTypes
from profiles_api.models import HrmsUsers

import uuid

email_statuses = (
	(1, 'To be set'),
	(2, 'Email Set'),
	(3, 'Email Save.'),
	(4, 'Sent'),
	(5, 'Cancel')
)

TEMPLATES_TYPES = (
	(1, 'Recruitment & Hiring'),
	(2, 'Learning & Development'),
	(3, 'Employee'),
	(4, 'Custom')
)

def get_rh_type(type):
	return TEMPLATES_TYPES[0][0]

class TemplateVariables(models.Model):
	title = models.CharField(max_length=100)
	code = models.CharField(max_length=50)
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
	template_type = models.IntegerField(choices=TEMPLATES_TYPES, default=1)
	short_code = models.CharField(max_length=25, null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	is_email = models.BooleanField(default=False)
	is_certificate = models.BooleanField(default=False)
	is_interview = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class EmailTemplates(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
	title = models.CharField(max_length=250)
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
	procedure_type = models.ForeignKey(ProcedureTypes, on_delete=models.CASCADE, blank=True, null=True)
	template_type = models.IntegerField(choices=TEMPLATES_TYPES, default=1)
	user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
	subject_line = models.CharField(max_length=250, null=True, blank=True)
	body= models.TextField(null=True, blank=True)
	footer = models.TextField(null=True, blank=True)
	has_attachments = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class EmailRecipients(models.Model):
    title = models.CharField(max_length=200)
    level = models.IntegerField(null=True,blank=True)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, blank=True, null=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE,blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    




