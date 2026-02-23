from django.db import models
from organizations.models import Organization

# Create your models here.
#evaluation, assessment

class ScoreTypes(models.Model):
	title = models.CharField(max_length=200)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class ComplexityLevels(models.Model):
	title = models.CharField(max_length=200)
	code = models.CharField(max_length=15)
	level = models.IntegerField(default=1)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class Scores(models.Model):
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
	complexity_level = models.IntegerField(default=1)
	score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
	complexity_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
	score_type = models.ForeignKey(ScoreTypes, on_delete=models.CASCADE)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)