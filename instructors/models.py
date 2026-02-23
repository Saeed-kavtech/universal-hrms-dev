from django.db import models
from organizations.models import Organization
from courses.models import Courses
from autoslug import AutoSlugField
import uuid
# Create your models here.

status_choices = (
    (1, 'Scheduled'),
    (2, 'Not Scheduled'),
    (3, 'InProgress'),
    (4, 'Completed')
)

session_status_choices = (
    ('Not initiated', 'Not initiated'),
    ('InProgress', 'InProgress'),
    ('Completed', 'Completed')
)

# routers
class ModeOfInstructions(models.Model):
    mode = models.CharField(max_length=200)
    level = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# paid, free
class CourseSessionTypes(models.Model):
    title = models.CharField(max_length=250)
    level = models.IntegerField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Instructors(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=200)
    slug_name = AutoSlugField(populate_from='name', null=True, default=None) 
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    is_available = models.BooleanField(default=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CourseSessions(models.Model):
    session_type =  models.CharField(max_length=250, null=True, blank=True) # spring, fall, winter
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    course_session_type = models.ForeignKey(CourseSessionTypes, on_delete=models.CASCADE, null=True, blank=True)
    session_status = models.CharField(choices = session_status_choices, max_length=30, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    duration = models.CharField(max_length=250, null=True, blank=True) 
    total_lectures = models.IntegerField(null=True, blank=True)
    no_of_students = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CourseSessionInstructors(models.Model):
    course_session = models.ForeignKey(CourseSessions, related_name='cs_instructor', on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructors, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Lectures(models.Model):
    course_session_instructor = models.ForeignKey(CourseSessionInstructors, on_delete=models.CASCADE)
    lecture_no = models.IntegerField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    duration = models.CharField(max_length=250, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField(null=True, blank=True) 
    is_taken = models.BooleanField(default=False, null=True, blank=True)
    mode_of_instruction = models.ForeignKey(ModeOfInstructions, on_delete=models.CASCADE, null=True, blank=True)
    status = models.IntegerField(choices = status_choices, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


