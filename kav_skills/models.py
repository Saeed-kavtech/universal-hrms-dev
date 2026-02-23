from django.db import models
from organizations.models import Organization
from helpers.image_uploads import upload_kav_skills_resume, upload_kav_skills_cover_letter, upload_course_skills_details
Category= (
        ('A', 'A'),
       ('B', 'B'),
       ('C', 'C'),
    )
Conversion_status=(('In progress','In progress'),
                   ('Rejected','Rejected'),
                   ('On hold','On hold'),
                   ('Converted','Converted'),
                   )
# Create your models here.
class SkillTypes(models.Model):
    title = models.CharField(max_length=200) 
    cost = models.PositiveIntegerField(default=0)
    course_details = models.FileField(upload_to=upload_course_skills_details, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class KavskillsEnrollmentForm(models.Model):
    skill_type = models.ForeignKey(SkillTypes, on_delete=models.CASCADE)
    email = models.EmailField(max_length=200) 
    full_name = models.CharField(max_length=250) 
    contact_number = models.CharField(max_length=200) 
    educational_qualifications = models.CharField(max_length=200) 
    university_name = models.CharField(max_length=200) 
    cnic_no = models.CharField(max_length=15) 
    major = models.CharField(max_length=150) 
    kav_skills_resume = models.FileField(upload_to=upload_kav_skills_resume)
    cover_letter = models.FileField(upload_to=upload_kav_skills_cover_letter, null=True, blank=True)
    joining_reason = models.TextField() 
    objectives = models.TextField() 
    financial_aid = models.BooleanField(default=False)
    financial_aid_reason = models.TextField(null=True, blank=True) 
    additional_information = models.TextField(null=True, blank=True) 
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # # new fields added 
    remark = models.TextField(null=True, blank=True)
    lnd_remark = models.TextField(null=True, blank=True)
    category= models.CharField(max_length=30, choices=Category,null=True, blank=True)
    conversion_status= models.CharField(max_length=30, choices=Conversion_status,null=True, blank=True)
