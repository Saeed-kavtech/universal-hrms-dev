from django.db import models
from organizations.models import StaffClassification, Organization
from profiles_api.models import HrmsUsers
# Create your models here.
class ScaleGroups(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.TextField()
    have_aspects=models.BooleanField(default=False)
    is_default_group=models.BooleanField(default=False)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ScaleRating(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.TextField()
    level = models.PositiveIntegerField()
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class GroupAspects(models.Model):
    scale_group = models.ForeignKey(ScaleGroups, on_delete=models.CASCADE)
    title = models.TextField()
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AspectsParameters(models.Model):
    title = models.TextField()
    aspects = models.ForeignKey(GroupAspects, on_delete=models.CASCADE)
    is_required=models.BooleanField(default=False)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




