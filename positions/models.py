from django.db import models
from organizations.models import StaffClassification
from departments.models import GroupHeads, Departments

experience_choices = (
    (1, '0-2 years'),
    (2, '2-4 years'),
    (3, '4-6 years'),
    (4, '6-8 years'),
    (5, '8-10 years'),
    (6, '10+ years'),
)

qualification_choices = (
    (1, "Bachelor's"),
    (2, "Master's"),
    (3, 'MPhil'),
    (4, 'other'),
)


# Create your models here.
class Positions(models.Model):
    grouphead = models.ForeignKey(GroupHeads, on_delete=models.CASCADE) 
    department = models.ForeignKey(Departments, on_delete=models.CASCADE) 
    staff_classification = models.ForeignKey(StaffClassification, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=12)
    code_number = models.IntegerField(null=True, blank=True)
    qualification = models.IntegerField(choices = qualification_choices)   
    years_of_experience = models.IntegerField(choices = experience_choices)   
    min_salary = models.IntegerField(blank=True, null=True) 
    max_salary = models.IntegerField(blank=True, null=True) #todo validator max salary greater than min salary
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Experiences(models.Model):                
    title = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)