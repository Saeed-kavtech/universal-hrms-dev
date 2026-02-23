from django.db import models
from applicants.models import CourseApplicants
from profiles_api.models import HrmsUsers
from helpers.image_uploads import upload_course_applicant_attachments
# Create your models here.

class CourseApplicantCustomEmails(models.Model):
    course_applicant = models.ForeignKey(CourseApplicants, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200, null=True, blank=True)
    body = models.TextField(blank=True, null=True)
    footer = models.TextField(blank=True, null=True)
    is_trainee = models.BooleanField(default=False)
    attachment = models.FileField(upload_to=upload_course_applicant_attachments, null=True, blank=True)
    action_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

