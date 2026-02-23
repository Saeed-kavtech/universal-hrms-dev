from django.db import models
from profiles_api.models import HrmsUsers
from organizations.models import Organization
from employees.models import Employees
from helpers.model_utils import CommonFieldsModel
import uuid
from employees.models import EmployeeProjects
from performance_configuration.models import ScaleGroups

DURATION_STATUS_CHOICES = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (6, 6),
    (12, 12),
)

BATCH_STATUS_CHOICES = (
    ('not-used', 'not-used'),
    ('in-progress', 'in-progress'),
    ('completed', 'completed'),
    ('upcoming', 'upcoming'),
    ('overdue', 'overdue'), 
)

Sagment_STATUS_CHOICES = (
    ('in-progress', 'in-progress'),
    ('completed', 'completed'),
   
)

Evaluation_Status = (
    (1, 'completed'),
    (2, 'in-complete'),
    (3, 'carry forward to next quarter'),
)

Kip_Mode_CHOICES = (
    (1, 'Permanent'),
    (2, 'Contract'),
    (3, 'Intern'),
    (4, 'Probation'),
)


class StatusGroup(CommonFieldsModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    level = models.IntegerField()


class KpisStatus(CommonFieldsModel):
    status_group=models.ForeignKey(StatusGroup, on_delete=models.CASCADE, null=True, blank=True)
    status_key = models.CharField(max_length=100)
    status_title = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    level = models.IntegerField()
    
# Create your models here. 
# EP stands for Employee - Performance
class EPTypes(CommonFieldsModel):
    title = models.CharField(max_length=100)
    key = models.CharField(max_length=100, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)


class EPComplexity(CommonFieldsModel):
    ep_type = models.ForeignKey(EPTypes, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    level = models.IntegerField()
    score=models.PositiveIntegerField()

class KpisStatusGroup(CommonFieldsModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    level = models.IntegerField()


class EPScaling(CommonFieldsModel):
    ep_type = models.ForeignKey(EPTypes, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    level = models.IntegerField()
    

class ScaleComplexity(models.Model):
    title=models.CharField(max_length=50)
    level=models.PositiveIntegerField()
    score=models.PositiveIntegerField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EPYearlySegmentation(CommonFieldsModel):
    date = models.DateField()
    duration = models.IntegerField(choices=DURATION_STATUS_CHOICES)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    brainstorming_period = models.IntegerField()
    brainstorming_period_for_evaluator = models.IntegerField(null=True, blank=True)
    evaluation_period = models.IntegerField(null=True, blank=True)
    status=models.CharField(max_length=50,choices=Sagment_STATUS_CHOICES,default="in-progress")
    approved_by = models.ForeignKey(HrmsUsers, related_name='approved_by_user', on_delete=models.CASCADE, null=True, blank=True)
    is_lock = models.BooleanField(null=True, blank=True)
    lock_by = models.ForeignKey(HrmsUsers, related_name='lock_by_user', on_delete=models.CASCADE, null=True, blank=True)
    locked_date = models.DateField(null=True, blank=True)
    unlock_by = models.ForeignKey(HrmsUsers, related_name='unlock_by_user', on_delete=models.CASCADE, null=True, blank=True)
    unlocked_date = models.DateField(null=True, blank=True)


class EPBatch(CommonFieldsModel):
    title=models.CharField(max_length=20)
    ep_yearly_segmentation = models.ForeignKey(EPYearlySegmentation, on_delete=models.CASCADE)
    batch_no = models.CharField(max_length=100)
    batch_status = models.CharField(max_length=100, choices=BATCH_STATUS_CHOICES, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()


class KpisObjectives(CommonFieldsModel):
    title = models.TextField(null=True,blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)

class EmployeesKpis(CommonFieldsModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    title = models.TextField()
    description = models.TextField(null=True,blank=True)
    ep_type = models.ForeignKey(EPTypes, on_delete=models.CASCADE)
    kpis_objective = models.ForeignKey(KpisObjectives, on_delete=models.CASCADE,null=True,blank=True)
    objectives = models.TextField(null=True, blank=True)
    employee_project=models.ForeignKey(EmployeeProjects, on_delete=models.CASCADE,null=True,blank=True)
    scale_group=models.ForeignKey(ScaleGroups, on_delete=models.CASCADE,null=True,blank=True)
    ep_batch = models.ForeignKey(EPBatch, on_delete=models.CASCADE)
    ep_complexity = models.ForeignKey(EPComplexity, on_delete=models.CASCADE)
    scale_complexity=models.ForeignKey(ScaleComplexity, on_delete=models.CASCADE,null=True,blank=True)
    ep_scaling = models.ForeignKey(EPScaling, on_delete=models.CASCADE, null=True, blank=True)
    mmtr = models.TextField(null=True, blank=True)
    target_dates = models.DateField(null=True, blank=True)
    mode_of_kpis = models.PositiveIntegerField(choices = Kip_Mode_CHOICES)
    evaluator = models.ForeignKey(Employees, related_name='evaluator_user', on_delete=models.CASCADE, null=True, blank=True)
    kpis_status = models.ForeignKey(KpisStatus, on_delete=models.CASCADE)  
    evaluation_status=models.IntegerField(choices=Evaluation_Status, null=True, blank=True)
    result = models.IntegerField(null=True, blank=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class KpisComments(CommonFieldsModel):
    employee_kpi = models.ForeignKey(EmployeesKpis, on_delete=models.CASCADE)
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)




class KpisLogs(CommonFieldsModel):
    employees_kpi = models.ForeignKey(EmployeesKpis, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=50, null=True, blank=True)
    ep_complexity = models.ForeignKey(EPComplexity, on_delete=models.CASCADE, null=True, blank=True)
    kpis_status = models.ForeignKey(KpisStatus, on_delete=models.CASCADE, null=True, blank=True) 
    title = models.CharField(max_length=250, null=True, blank=True)
    objectives = models.TextField(null=True, blank=True)
    ep_batch = models.ForeignKey(EPBatch, on_delete=models.CASCADE, null=True, blank=True)
    ep_scaling = models.ForeignKey(EPScaling, on_delete=models.CASCADE, null=True, blank=True)
    mmtr = models.TextField(null=True, blank=True)
    target_dates = models.DateField(null=True, blank=True)
    evaluator = models.ForeignKey(Employees, related_name='evaluator_log', on_delete=models.CASCADE, null=True, blank=True)
    kpis_is_active = models.BooleanField(null=True, blank=True)

