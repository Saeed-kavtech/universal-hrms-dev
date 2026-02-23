from django.db import models
from employees.models import Employees
from helpers.image_uploads import upload_employee_degrees

# Create your models here.
class DegreeTypes(models.Model):
	title = models.CharField(max_length=100)
	duration = models.IntegerField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class Institutes(models.Model):
	name = models.CharField(max_length=200)
	short_form = models.CharField(max_length=100, null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class EmployeeEducations(models.Model):
	employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
	degree_type = models.ForeignKey(DegreeTypes, on_delete=models.CASCADE)
	institutes =  models.ForeignKey(Institutes, on_delete=models.CASCADE, null=True, blank=True)
	degree_title = models.CharField(max_length=100)
	duration = models.IntegerField()
	institute_name = models.CharField(max_length=200, null=True, blank=True)
	year_of_completion = models.DateField()
	degree_certificate = models.FileField(upload_to=upload_employee_degrees, null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
