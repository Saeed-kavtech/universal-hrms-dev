from django.db import models
from organizations.models import StaffClassification, Organization
from profiles_api.models import HrmsUsers
from kpis.models import *
from performance_configuration.models import *

# Create your models here.
class KPIScaleGroups(models.Model):
    kpi_id = models.ForeignKey(EmployeesKpis, on_delete=models.CASCADE )
    scale_group = models.ForeignKey(ScaleGroups, on_delete=models.CASCADE)
    result=models.TextField(null=True, blank=True)
    score=models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    assign_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(HrmsUsers,related_name='approved_kpi_scale_groups', on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class KPIAspects(models.Model):
    kpi_sg = models.ForeignKey(KPIScaleGroups, on_delete=models.CASCADE)
    ep_aspects = models.ForeignKey(GroupAspects, on_delete=models.CASCADE)
    result=models.TextField(null=True, blank=True)
    score=models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class KPIAspectsParameterRating(models.Model):
    kpi_aspects=models.ForeignKey(KPIAspects, on_delete=models.CASCADE)
    parameters=models.ForeignKey(AspectsParameters, on_delete=models.CASCADE)
    scale_rating=models.ForeignKey(ScaleRating, on_delete=models.CASCADE, null=True, blank=True)
    result=models.TextField(null=True, blank=True)
    score=models.TextField(null=True, blank=True)
    is_required=models.BooleanField(default=False)
    comment = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)





