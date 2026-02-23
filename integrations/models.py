from django.db import models
from organizations.models import Organization
from profiles_api.models import HrmsUsers
# Create your models here.
medium_choices=(
    ('gmail','gmail'),
    ('zoho','zoho')
)

class MailsCredentials(models.Model):
    email = models.EmailField(null=True,blank=True)
    password= models.CharField(max_length=200,null=True,blank=True)
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE,blank=True, null=True)
    medium= models.CharField(max_length=30, choices=medium_choices, null=True, blank=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE,blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)