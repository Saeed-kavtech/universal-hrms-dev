from django.db import models
from courses.models import Courses
from instructors.models import CourseSessions, Lectures
from employees.models import Employees
from instructors.models import ModeOfInstructions
from profiles_api.models import HrmsUsers

STATUS_CHOICES = (
    (1, 'Unprocessed'),
    (2, 'In process'),
    (3, 'Approved'),
    (4, 'Rejected'),
    (5, 'Waitlisted')   
)

ATTENDANCE_STATUS_CHOICES = (
    (1, 'Present'),
    (2, 'Absent'),
    (3, 'Leave')
)

DECISION_STATUS_CHOICES = (
    (1, 'Approved'),
    (2, 'Rejected'),
    (3, 'Pending')
)


# Create your models here.
class CourseApplicants(models.Model):
    course =  models.ForeignKey(Courses, on_delete=models.CASCADE)
    course_session =  models.ForeignKey(CourseSessions, on_delete=models.CASCADE)
    employee =  models.ForeignKey(Employees, on_delete=models.CASCADE)
    is_submitted = models.BooleanField(default=True, null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    date = models.DateField(null=True, blank=True)
    additional_comments =  models.CharField(max_length=250, null=True, blank=True)
    is_trainee = models.BooleanField(default=False, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CourseApplicantsLogs(models.Model):
    course_applicant = models.ForeignKey(CourseApplicants, related_name='decision_list', on_delete=models.CASCADE)
    log_status = models.IntegerField(choices=STATUS_CHOICES, null=True, blank=True)
    decision_status = models.IntegerField(choices=DECISION_STATUS_CHOICES, default=3, null=True, blank=True)
    decision_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, null=True, blank=True)
    decision_reason = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CourseSessionTrainees(models.Model):
    course_applicant = models.ForeignKey(CourseApplicants, on_delete=models.CASCADE)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    course_session = models.ForeignKey(CourseSessions, on_delete=models.CASCADE)
    is_pass = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# class CourseSessionTraineesLogs(models.Model):
#     course_session_trainees = models.ForeignKey(CourseSessionTrainees, on_delete=models.CASCADE)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


class CourseSessionTraineeAttendance(models.Model):
    lecture =  models.ForeignKey(Lectures, on_delete=models.CASCADE)
    course_session_trainee =  models.ForeignKey(CourseSessionTrainees, on_delete=models.CASCADE)
    attendance_status = models.IntegerField(choices=ATTENDANCE_STATUS_CHOICES, null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    mode =  models.ForeignKey(ModeOfInstructions, on_delete=models.CASCADE, null=True, blank=True) # online, physical, hybrid
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)