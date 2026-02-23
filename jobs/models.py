from django.db import models
from organizations.models import StaffClassification
from departments.models import GroupHeads, Departments
from jd.models import JdDescriptions
from positions.models import Positions
from profiles_api.models import HrmsUsers
import uuid

# Create your models here.

job_post_choices = {
    '1': 'Active',
    '2': 'Progress',
    '3': 'Posted',
    '4': 'Deleted',
}


job_status_choices = {
    '1': 'Progress',
    '2': 'Posted',
    '3': 'cancel',
    '4': 'Completed',
    '5': 'Fulfilled',
    '6': 'Deleted'
}

class Jobs(models.Model): 
	uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
	department = models.ForeignKey(Departments, on_delete=models.CASCADE) 
	staff_classification =  models.ForeignKey(StaffClassification, on_delete=models.CASCADE)
	position = models.ForeignKey(Positions, on_delete=models.CASCADE)
	created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
	job_code = models.CharField(max_length=7) 
	title = models.CharField(max_length=200, blank=True, null=True)
	iterations =  models.IntegerField(default=1)   
	reports_to = models.CharField(max_length=200, blank=True, null=True)
	status = models.CharField(max_length=200, blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

# permanent, wfh, intern
class JobTypes(models.Model):                
    title = models.CharField(max_length=200)  
    level = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class JobPosts(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    job = models.ForeignKey(Jobs, related_name="job_posts", on_delete=models.CASCADE) 
    jd_selection = models.ForeignKey(JdDescriptions, on_delete=models.CASCADE) 
    project = models.CharField(max_length=200,blank=True, null=True) #todo it will be a foreign key
    job_type = models.ForeignKey(JobTypes, on_delete=models.CASCADE) 
    job_post_code = models.CharField(max_length=100, blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    min_salary = models.IntegerField(blank=True, null=True) 
    max_salary = models.IntegerField(blank=True, null=True)
    jp_reports_to  = models.CharField(max_length=200, blank=True, null=True)
    no_of_individuals = models.IntegerField(default=1)
    post_date = models.DateField(blank=True, null=True) #todo add validator according to the requirement
    expiry_date = models.DateField(blank=True, null=True) #todo add validator which checks that expiry date is greater than current date
    jp_iterations = models.IntegerField(default=1)   
    revised_by  = models.ForeignKey(HrmsUsers, related_name="revised_by", on_delete=models.CASCADE, blank=True, null=True)
    revised_date = models.DateField(blank=True, null=True)
    approved_date = models.DateField(blank=True, null=True)
    approved_by  = models.ForeignKey(HrmsUsers, related_name="approved_by", on_delete=models.CASCADE, blank=True, null=True) 
    status = models.CharField(max_length=200, default="", blank=True, null=True) #todo choices fields
    is_completed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class JobLogs(models.Model):
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE) 
    job = models.ForeignKey(Jobs, on_delete=models.CASCADE) 
    status =  models.CharField(max_length=200,blank=True, null=True) #todo choices fields
    message =  models.TextField(blank=True, null=True) 
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class JobPostLogs(models.Model):
    job_post = models.ForeignKey(JobPosts, on_delete=models.CASCADE)
    status =  models.CharField(max_length=200,blank=True, null=True) #todo choices fields
    message =  models.TextField(blank=True, null=True)
    is_fulfilled = models.BooleanField(default=False) 
    fullfilled_date = models.DateField(blank=True, null=True) #todo validator, greater than current date
    cancel_date = models.DateField(blank=True, null=True) # todo validator, greater than current date
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


