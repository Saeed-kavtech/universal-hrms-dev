from django.db import models
from employees.models import Employees
# Create your models here.

class ProficiencyLevels(models.Model):
	title = models.CharField(max_length=200)
	level = models.IntegerField(default=1)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class SkillCategories(models.Model):
	title = models.CharField(max_length=200)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class Skills(models.Model):
	category = models.ForeignKey(SkillCategories, on_delete=models.CASCADE)
	title = models.CharField(max_length=100)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class EmployeeSkills(models.Model):
	employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
	skill = models.ForeignKey(Skills, on_delete=models.CASCADE)
	proficiency_level = models.ForeignKey(ProficiencyLevels, on_delete=models.CASCADE)
	comment = models.TextField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)