from django.db import models
from organizations.models import Organization
from autoslug import AutoSlugField
import uuid
from helpers.image_uploads import upload_assignment,upload_by_employee_assignment
from profiles_api.models import HrmsUsers
from employees.models import Employees
# Create your models here.

# choice field
mode_of_course_choices = (
    (1, 'Online'),
    (2, 'In House'),
    (3, 'Out House')
)

complexity_level_choices = (
    (1, 'Begineer'),
    (2, 'Intermediate'),
    (3, 'Advance')
)


group_courses_choices=(
    (1,'Technical'),
    (2,'Non Technical')
)


# routers
class SubjectTypes(models.Model):
    title = models.CharField(max_length=200)
    level = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# non router Class
class Subjects(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=200)
    slug_title = AutoSlugField(populate_from='title', null=True, default=None)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    type = models.ForeignKey(SubjectTypes, on_delete=models.CASCADE) 
    description = models.TextField(null=True, blank=True) 
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Programs(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=200)
    slug_title = AutoSlugField(populate_from='title', null=True, default=None)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    
class Courses(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=200)
    slug_title = AutoSlugField(populate_from='title', null=True, default=None)
    code = models.CharField(max_length=20, unique=True, null=True, blank=True) 
    program = models.ForeignKey(Programs, on_delete=models.CASCADE,null=True,blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    program_level = models.IntegerField(null=True, blank=True) #unique 
    what_will_you_learn =  models.TextField(null=True, blank=True)
    skills_you_gain = models.TextField(null=True, blank=True) #TODO FOREIGN KEY
    credit_hours = models.IntegerField(null=True, blank=True) 
    mode_of_course = models.IntegerField(choices=mode_of_course_choices) #TODO choice field 
    course_group= models.IntegerField(choices=group_courses_choices,null=True,blank=True)
    complexity_level = models.IntegerField(choices=complexity_level_choices) #TODO choice field
    offered_by = models.CharField(max_length=200, null=True, blank=True) #TODO is this forign key of instructor
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CoursePreRequisite(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    pre_requisite = models.CharField(max_length=250) #TODO this field could be multiple. One course could have multiple pre req
    detail = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CourseSkills(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    skill = models.CharField(max_length=250, null=True, blank=True) #TODO routers
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CourseModules(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True) 
    what_we_learn = models.TextField(null=True, blank=True)
    total_hours = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class ModuleTopics(models.Model):
    title = models.CharField(max_length=200)
    course_module = models.ForeignKey(CourseModules, on_delete=models.CASCADE,null=True, blank=True) 
    credit_hours = models.IntegerField(null=True, blank=True)  
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


