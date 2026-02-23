from django.db import models

from employees.models import Employees
from organizations.models import Organization
from profiles_api.models import HrmsUsers
from interviews.models import InterviewMedium

# Create your models here.
class MeetingCategory(models.Model):
    title = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
     

class Meetings(models.Model):
    meeting_uuid = models.TextField(null=True,blank=True)
    meeting_id = models.BigIntegerField(null=True,blank=True)
    host_id = models.CharField(max_length=64,null=True,blank=True)
    topic = models.CharField(max_length=255,null=True,blank=True)
    status=models.CharField(max_length=64,null=True,blank=True) 
    meeting_type = models.IntegerField(null=True,blank=True)  
    start_time = models.TimeField(null=True,blank=True)
    date=models.DateField(null=True,blank=True)
    duration = models.IntegerField(null=True,blank=True)  
    timezone = models.CharField(max_length=64,null=True,blank=True) 
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    join_url = models.TextField(null=True,blank=True)  
    start_url = models.TextField(null=True,blank=True)
    password = models.CharField(max_length=32, blank=True, null=True)
    meeting_medium = models.ForeignKey(InterviewMedium, on_delete=models.CASCADE, null=True, blank=True)
    meeting_category = models.CharField(max_length=32, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class InternalMeetingParticipant(models.Model):
    hrms_user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, null=True, blank=True)
    meeting= models.ForeignKey(Meetings, on_delete=models.CASCADE, null=True, blank=True)
    is_host=models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class ExternalMeetingParticipant(models.Model):
    meeting= models.ForeignKey(Meetings, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    is_host=models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
  
