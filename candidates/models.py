from django.db import models
from jobs.models import JobPosts
from profiles_api.models import HrmsUsers
from organizations.models import Organization
from stages.models import Stages
from helpers.image_uploads import upload_candidate_resume
import uuid

from time_intervals.models import TimeIntervals



class Candidates(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    candidate_name = models.CharField(max_length=200)
    cnic_no = models.CharField(max_length=15) 
    email = models.EmailField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE) 
    mobile_no = models.CharField(max_length=13)  
    linkedin_profile = models.CharField(max_length=200, blank=True, null=True) #properway to store it
    is_hrms_user = models.BooleanField(blank=False, null=True, default=False)
    is_already_applied=models.BooleanField(default=False)
    reference_name=models.CharField(max_length=100,null=True, blank=True) 
    reference_connection=models.TextField(null=True, blank=True)
    user_id = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

#TODO for attachment or group_of_attachment
class RecruitmentStages(models.Model): 
    title = models.CharField(max_length=200)
    level = models.IntegerField(default=1)
    sent_email_required = models.IntegerField(default=0) # 1 for required, 2 for optional
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CandidateJobs(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    candidate = models.ForeignKey(Candidates, on_delete=models.CASCADE)
    job_post = models.ForeignKey(JobPosts, on_delete=models.CASCADE, blank=True, null=True)
    resume = models.FileField(upload_to=upload_candidate_resume)
    # is stage a choice field? Do we need to store it
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name="candidate_job_stages", blank=True, null=True)
    time_interval = models.ForeignKey(TimeIntervals, on_delete=models.CASCADE, related_name="candidate_job_time_interval", blank=True, null=True)
    evaluation_score = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=200,blank=True, null=True) #todo Is status choices fields
    is_qualified = models.BooleanField(default=True)
    disqualified_time = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



# log if any candidate updates its columns based on cnic
class CandidatesLog(models.Model):
    candidate = models.ForeignKey(Candidates, on_delete=models.CASCADE)
    prev_data = models.TextField(null=True, blank=True)
    update_data = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CandidateStatusLog(models.Model):
    candidate = models.ForeignKey(Candidates, on_delete=models.CASCADE)
    candidate_job = models.ForeignKey(CandidateJobs, on_delete=models.CASCADE, blank=True, null=True)
    action_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    action = models.CharField(max_length=100, null=True, blank=True)
    action_reason = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CandidateJobsStageLog(models.Model):
    candidate_job = models.ForeignKey(CandidateJobs, on_delete=models.CASCADE)
    updated_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE)
    is_email_sent = models.BooleanField(default=False)
    email_body = models.TextField(null=True, blank=True)
    action = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


#TODO Log for candidate actions. 

# Recruitment Stages.


