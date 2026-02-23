from django.db import models

from helpers.image_uploads import upload_datahive_files
from organizations.models import Organization
from profiles_api.models import HrmsUsers
from projects.models import Projects
# NOTE: do not import model_enhanced here to avoid circular import during app loading

# Create your models here.
class Tags(models.Model):
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Categories(models.Model):
    title = models.CharField(max_length=50)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Documents(models.Model):
    title = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to=upload_datahive_files)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, null=True, blank=True)
    is_public = models.BooleanField(default=True, null=True, blank=True)
    tags = models.ManyToManyField(Tags,blank=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
