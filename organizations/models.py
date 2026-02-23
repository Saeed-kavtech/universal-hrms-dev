from django.db import models
from profiles_api.models import HrmsUsers
from datetime import datetime
from helpers.image_uploads import upload_to
# Create your models here.

# Organization User and assign admin of organization. 
# Organization may have multi admin user, to handle this create a new model for admin users. 
# 
    

    
class Organization(models.Model):
    user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, unique=True)
    tagline = models.TextField(max_length=500, null=True, blank=True)
    vision = models.TextField(max_length=500, null=True, blank=True)
    mission = models.TextField(max_length=500, null=True, blank=True)
    logo = models.ImageField(null=True, blank=True, upload_to=upload_to, default='')
    is_active = models.BooleanField(default=True)
    established_date =  models.DateField(null=True, blank=True)
    organization_type = models.CharField(max_length=200, null=True, blank=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, related_name="org_creator")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SubadminOrganization(models.Model):
    user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    


class OrganizationLocation(models.Model):
    organization = models.ForeignKey(Organization, related_name='locations', on_delete=models.CASCADE)
    city_id = models.IntegerField(blank=True, null=True)
    city_name = models.CharField(max_length=200 )
    zipcode = models.CharField(max_length=7, blank=True, null=True)
    latitute = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    longitute = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    is_head_office = models.BooleanField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StaffClassification(models.Model):
    organization = models.ForeignKey(Organization, related_name="organization_level", on_delete=models.CASCADE)
    technical_title = models.CharField(max_length=200, blank=True, null=True)
    non_technical_title = models.CharField(max_length=200, blank=True, null=True)
    initial = models.CharField(max_length=4, blank=True, null=True)
    title = models.CharField(max_length=200, default="auto title")
    level = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Roles(models.Model):
    organization = models.ForeignKey(Organization, related_name="organization_roles", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    level = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProcedureTypes(models.Model):
    title = models.CharField(max_length=200)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OrganizationApikeys(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE,blank=True,null=True)
    google_api=models.TextField(null=True,blank=True)
    client_id=models.TextField(null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ThirdPartyTokens(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    client_id=models.TextField(null=True,blank=True)
    client_secret=models.TextField(null=True,blank=True)
    expires_in = models.IntegerField(null=True,blank=True)
    redirect_uri=models.TextField(null=True,blank=True)
    access_token = models.TextField(null=True,blank=True)
    refresh_token = models.TextField(null=True,blank=True)
    code=models.TextField(null=True,blank=True)
    scope = models.TextField(null=True,blank=True)
    token_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrganizationModuleAccess(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,null=True,blank=True)
    title= models.CharField(max_length=255)
    level = models.IntegerField()
    is_allowed = models.BooleanField(default=False)
    is_default=models.BooleanField(default=False)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)