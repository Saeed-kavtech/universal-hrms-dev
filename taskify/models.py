from django.db import models
from helpers.image_uploads import upload_tasks_attachments
from organizations.models import Organization
from projects.models import Projects
from profiles_api.models import HrmsUsers
from employees.models import Employees
priority_choices = (
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
)
# Create your models here.
class TasksStatus(models.Model):
    title = models.CharField(max_length=100,null=True,blank=True)
    level = models.IntegerField(null=True,blank=True)
    project=models.ForeignKey(Projects, on_delete=models.CASCADE,null=True,blank=True)
    organization=models.ForeignKey(Organization, on_delete=models.CASCADE,null=True,blank=True)
    created_by=models.ForeignKey(HrmsUsers, on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TaskTypes(models.Model):
    title = models.CharField(max_length=100,null=True,blank=True)
    level = models.IntegerField(null=True,blank=True)
    project=models.ForeignKey(Projects, on_delete=models.CASCADE,null=True,blank=True)
    organization=models.ForeignKey(Organization, on_delete=models.CASCADE,null=True,blank=True)
    created_by=models.ForeignKey(HrmsUsers, on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TaskGroups(models.Model):
    title = models.CharField(max_length=100,null=True,blank=True)
    project=models.ForeignKey(Projects, on_delete=models.CASCADE,null=True,blank=True)
    description = models.TextField(null=True, blank=True)
    organization=models.ForeignKey(Organization, on_delete=models.CASCADE,null=True,blank=True)
    created_by=models.ForeignKey(HrmsUsers, on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Tasks(models.Model):
    title = models.CharField(max_length=100,null=True,blank=True)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE,null=True,blank=True)
    assign_to = models.ForeignKey(Employees, related_name='task_assign_to', on_delete=models.CASCADE, null=True, blank=True)
    project=models.ForeignKey(Projects, on_delete=models.CASCADE,null=True,blank=True)
    estimated_time=models.TimeField(null=True,blank=True)
    task_type=models.ForeignKey(TaskTypes, on_delete=models.CASCADE,null=True,blank=True)
    priority=models.CharField(max_length=20,choices=priority_choices,null=True,blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    status=models.ForeignKey(TasksStatus, on_delete=models.CASCADE,null=True,blank=True)
    planned_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    account_hour = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    external_ticket_reference = models.URLField(null=True, blank=True)
    description=models.TextField(null=True,blank=True)
    is_child=models.BooleanField(default=False)
    time_log=models.TimeField(null=True,blank=True)
    created_by=models.ForeignKey(HrmsUsers, on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TaskTimeLogs(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE,null=True,blank=True)
    date = models.DateField()
    hours_spent = models.DecimalField(max_digits=5, decimal_places=2)  # Allows hours with decimal places
    log_description = models.TextField(blank=True, null=True)
    status=models.ForeignKey(TasksStatus, on_delete=models.CASCADE,null=True,blank=True)
    created_by=models.ForeignKey(HrmsUsers, on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TaskLogs(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    title = models.CharField(max_length=100,null=True,blank=True)
    estimated_time=models.TimeField(null=True,blank=True)
    task_type=models.ForeignKey(TaskTypes, on_delete=models.CASCADE,null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    hours_spent = models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True)
    priority=models.CharField(max_length=20,choices=priority_choices,null=True,blank=True)
    parent = models.ForeignKey(Tasks, on_delete=models.CASCADE,related_name='task_parent',null=True, blank=True)
    project=models.ForeignKey(Projects, on_delete=models.CASCADE,null=True,blank=True)
    assign_to = models.ForeignKey(Employees, related_name='task_log_assign_to', on_delete=models.CASCADE, null=True, blank=True)
    status=models.ForeignKey(TasksStatus, on_delete=models.CASCADE,null=True,blank=True)
    is_deactivated= models.BooleanField(null=True, blank=True)
    planned_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    account_hour = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    date= models.DateField(null=True, blank=True)
    external_ticket_reference = models.URLField(null=True, blank=True)
    created_by = models.ForeignKey(HrmsUsers,on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TaskComment(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    comment= models.TextField(null=True,blank=True)
    created_by = models.ForeignKey(HrmsUsers,on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TaskAttachments(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE,null=True,blank=True)
    comment=models.ForeignKey(TaskComment, on_delete=models.CASCADE,null=True,blank=True)
    attachment=models.FileField(upload_to=upload_tasks_attachments, null=True, blank=True)
    created_by = models.ForeignKey(HrmsUsers,on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TaskGroupLinks(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE,null=True,blank=True)
    group=models.ForeignKey(TaskGroups, on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

