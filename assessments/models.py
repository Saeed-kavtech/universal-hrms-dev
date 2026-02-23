from django.db import models
from profiles_api.models import HrmsUsers
from candidates.models import *
from positions.models import Positions
from organizations.models import Organization
from helpers.image_uploads import upload_assessment_tests, upload_assessment_questions

from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

# need the criteria for selecting the assessment test for candidates. 
class AssessmentTypes(models.Model):
	title = models.CharField(max_length=200)  
	level = models.IntegerField(default=1)
	is_technical = models.BooleanField(default=0)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class AssessmentTests(models.Model):
	assessment_type = models.ForeignKey(AssessmentTypes, on_delete=models.CASCADE)
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
	position = models.ForeignKey(Positions, on_delete=models.CASCADE, null=True, blank=True)
	title = models.CharField(max_length=200, blank=True, null=True)
	duration = models.CharField(max_length=10, null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class AssessmentTestFiles(models.Model):
	assessment_test = models.ForeignKey(AssessmentTests, on_delete=models.CASCADE)
	assessment_file = models.FileField(upload_to=upload_assessment_tests)
	uploaded_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, blank=True, null=True)
	approved_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, related_name="assessment_approved_by", blank=True, null=True)
	total_questions = models.IntegerField(null=True, blank=True)
	uploaded_questions = models.IntegerField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class AssessmentFileLogs(models.Model):
	assessment_file = models.ForeignKey(AssessmentTestFiles, on_delete=models.CASCADE)
	action = models.CharField(max_length=100, blank=True, null=True)
	detail = models.TextField(null=True, blank=True)
	user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)



# Questions Models

class Questions(models.Model):
	question = models.TextField()
	assessment_test_file = models.ForeignKey(AssessmentTestFiles, on_delete=models.CASCADE, blank=True, null=True)
	answer_option = models.IntegerField() # the option value belongs to question options.
	answer = models.CharField(max_length=300, null=True, blank=True)
	complexity_level = models.IntegerField(default=1)
	clevel = models.CharField(max_length=10, null=True, blank=True)
	time = models.CharField(max_length=10, null=True, blank=True)
	total_options = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)], default=1)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class QuestionImages(models.Model):
	question = models.ForeignKey(Questions, on_delete=models.CASCADE)
	label = models.CharField(max_length=10)
	image = models.ImageField(upload_to=upload_assessment_questions)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class QuestionOptions(models.Model):
	question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='question_options')
	option = models.IntegerField() # the option number that comes from csv file
	value = models.CharField(max_length=300) # the value of the option
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class QuestionOptionImages(models.Model):
	question_option = models.ForeignKey(QuestionOptions, on_delete=models.CASCADE)
	label = models.CharField(max_length=10)
	image = models.ImageField(upload_to=upload_assessment_questions)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class CandidateAssessmentTest(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
	candidate = models.ForeignKey(Candidates, on_delete=models.CASCADE, related_name="candidate_assessment_tests")
	candidate_job = models.ForeignKey(CandidateJobs, on_delete=models.CASCADE, null=True, blank=True, related_name="candidate_job_assessment_tests")
	assessment_test = models.ForeignKey(AssessmentTests, on_delete=models.CASCADE, null=True, blank=True, related_name="assessment_test_candidate_list")
	assessment_test_file = models.ForeignKey(AssessmentTestFiles, on_delete=models.CASCADE, null=True, blank=True)
	is_email_sent = models.BooleanField(default=False)
	duration = models.CharField(max_length=10, null=True, blank=True)
	start_date_time = models.DateTimeField(null=True, blank=True)
	complete_date_time = models.DateTimeField(null=True, blank=True)
	is_completed = models.BooleanField(default=False)
	total_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
	total_marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
	result = models.CharField(max_length=100, blank=True, null=True)
	is_passed = models.BooleanField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class CandidateAssessmentQuestions(models.Model):
	candidate_assessment_test = models.ForeignKey(CandidateAssessmentTest, on_delete=models.CASCADE)
	question = models.ForeignKey(Questions, on_delete=models.CASCADE)
	answer = models.CharField(max_length=300, null=True, blank=True)
	answer_option = models.IntegerField(null=True, blank=True)
	time = models.CharField(max_length=15, null=True, blank=True)
	is_correct = models.BooleanField(default=0, null=True, blank=True)
	marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
	marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
	start_date_time = models.DateTimeField(null=True, blank=True)
	complete_date_time = models.DateTimeField(null=True, blank=True)




