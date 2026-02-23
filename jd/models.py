from django.db import models
from organizations.models import  StaffClassification
from departments.models import GroupHeads, Departments
from positions.models import Positions

# Create your models here.
# JD model
class JdDescriptions(models.Model):
    department = models.ForeignKey(Departments, on_delete=models.CASCADE) 
    staff_classification =  models.ForeignKey(StaffClassification, on_delete=models.CASCADE, null=True, blank=True) 
    position = models.ForeignKey(Positions, on_delete=models.CASCADE, null=True, blank=True) 
    project = models.CharField(max_length=200,blank=True, null=True) #todo project will be a forign key (when project table would be created)
    title = models.CharField(max_length=200) #todo this title must be unique
    code = models.CharField(max_length=7) #todo this code must be unique
    main_responsibilities =  models.TextField( null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


#Job Description(JD) has 2 blocks which we called JD types. One is job specification and the other one is additional information
class JdTypes(models.Model):
    title = models.CharField(max_length=200) 
    level = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)           

# jd_type_choices = {
#     'Job specification': 'job specification',
#     'Additional Information': 'Additional Information'
# }
class JdDimensions(models.Model):
    title = models.CharField(max_length=200)
    level = models.IntegerField(default=1)
    jd_type = models.ForeignKey(JdTypes, on_delete=models.CASCADE, null=True, blank=True) 
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #order_by = [type,level]

class JdSpecifications(models.Model):
    jd = models.ForeignKey(JdDescriptions, related_name = "jd_specifications", on_delete=models.CASCADE) 
    jd_dimension = models.ForeignKey(JdDimensions, on_delete=models.CASCADE) 
    essential = models.TextField(max_length=300, null=True, blank=True)
    desirable =  models.TextField(max_length=300, null=True, blank=True) 
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
