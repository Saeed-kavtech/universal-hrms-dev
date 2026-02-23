from django.db import models
from organizations.models import Organization
from profiles_api.models import HrmsUsers
from roles.models import Roles
from candidates.models import Candidates, CandidateJobs
from organizations.models import ProcedureTypes
from stages.models import Stages

from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

EVALUATION_REMARKS = (
	(1, "Hire"),
	(2, "Don't Hire"),
	(3, "Discussion")
)


class RoleProcedureAccess(models.Model):
	role = models.ForeignKey(Roles, on_delete=models.CASCADE)
	procedure = models.ForeignKey(ProcedureTypes, on_delete=models.CASCADE)
	is_allow = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class Evaluations(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
	title = models.CharField(max_length=250)
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
	user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
	procedure = models.ForeignKey(ProcedureTypes, on_delete=models.CASCADE)
	description = models.TextField(blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class EvaluationProcedureQuestions(models.Model):
	evaluation = models.ForeignKey(Evaluations, on_delete=models.CASCADE)
	procedure = models.ForeignKey(ProcedureTypes, on_delete=models.CASCADE, blank=True, null=True)
	role = models.ForeignKey(Roles, on_delete=models.CASCADE, blank=True, null=True)
	role_procedure = models.ForeignKey(RoleProcedureAccess, on_delete=models.CASCADE, blank=True, null=True)
	question = models.TextField()
	complexity_level = models.IntegerField(default=1)
	score = models.CharField(max_length=20, null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class EvaluationProcedureRoleQuestions(models.Model):
	evaluation_procedure_question = models.ForeignKey(EvaluationProcedureQuestions, on_delete=models.CASCADE)
	role = models.ForeignKey(Roles, on_delete=models.CASCADE)
	complexity_level = models.IntegerField(blank=True, null=True)
	score = models.CharField(max_length=20, null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class CandidateEvaluations(models.Model):
	candidate = models.ForeignKey(Candidates, on_delete=models.CASCADE)
	candidate_job = models.ForeignKey(CandidateJobs, on_delete=models.CASCADE)
	# stage = models.ForeignKey(Stages, on_delete=models.CASCADE)
	stage = models.ForeignKey(Stages, on_delete=models.CASCADE, blank=True, null=True)
	evaluation = models.ForeignKey(Evaluations, on_delete=models.CASCADE)
	evaluated_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, blank=True, null=True)
	comment = models.TextField(blank=True, null=True)
	is_start = models.BooleanField(default=False)
	start_date_time = models.DateTimeField(blank=True, null=True)
	is_completed = models.BooleanField(default=False, null=True, blank=True)
	total_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
	total_marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
	recommendation = models.CharField(max_length=50, null=True, blank=True)
	evaluation_remarks = models.IntegerField(choices=EVALUATION_REMARKS, null=True, blank=True)
	is_rechecked = models.BooleanField(default=False)
	is_mark_done = models.BooleanField(default=False)
	is_cancel = models.BooleanField(default=False)
	cancel_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, related_name="evaluation_cancel_by", blank=True, null=True)
	cancel_date_time = models.DateTimeField(null=True, blank=True)
	reason_for_cancel = models.TextField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class CandidateEvaluationQuestionRemarks(models.Model):
	candidate_evaluation = models.ForeignKey(CandidateEvaluations, on_delete=models.CASCADE)
	evaluation_procedure_question = models.ForeignKey(EvaluationProcedureQuestions, on_delete=models.CASCADE)
	complexity_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)], null=True, blank=True)
	score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
	comment = models.TextField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
class CandidateJobActionLogs(models.Model):
	candidate_job = models.ForeignKey(CandidateJobs, on_delete=models.CASCADE,null=True,blank=True)
	candidate_evaluation = models.ForeignKey(CandidateEvaluations, on_delete=models.CASCADE,null=True,blank=True)
	title=models.TextField(null=True, blank=True)
	action_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE,null=True,blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)