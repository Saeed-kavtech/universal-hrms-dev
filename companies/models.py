from django.db import models
from employees.models import Employees
from helpers.image_uploads import upload_employee_experience

# Create your models here.
class Companies(models.Model):
	name = models.CharField(max_length=200)
	company_type = models.CharField(max_length=100, null=True, blank=True)
	established_date = models.DateField(null=True, blank=True)
	vision = models.TextField(null=True, blank=True)
	mission = models.TextField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class EmployeeWorkExperience(models.Model):
	employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
	company = models.ForeignKey(Companies, on_delete=models.CASCADE, null=True, blank=True)
	company_name = models.CharField(max_length=200, null=True, blank=True)
	designation = models.CharField(max_length=200)
	joining_date = models.DateField()
	leaving_date = models.DateField(null=True, blank=True)
	leaving_reason = models.TextField(null=True, blank=True)
	is_currently_employed=models.BooleanField(default=False)
	experience_letter = models.FileField(upload_to=upload_employee_experience, null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
