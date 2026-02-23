from django.db import models
from organizations.models import Organization
from profiles_api.models import HrmsUsers

# Create your models here.

grouphead_choices = (
    (1, 'Technical'),
    (2, 'Non-Technical'),
)

class GroupHeads(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    grouphead_type = models.CharField(max_length=200, choices = grouphead_choices)
    description = models.TextField(null=True, blank=True) 
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    status = models.BooleanField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Departments(models.Model):
    grouphead = models.ForeignKey(GroupHeads, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=1)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


