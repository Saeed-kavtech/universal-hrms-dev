from django.db import models
from positions.models import Positions
from employees.models import Employees, EmployeeTypes
from jobs.models import *
from profiles_api.models import HrmsUsers
from organizations.models import  Organization
# from jobs.models import Jobs

Requisition_Status = (
    (1,'Requested By Employee'),
    (2,'Pending By HR'),
    (3,'Initiated By HR'),
    (4, 'Request Approved'),
    (5, 'Request Rejected')
)
class ReplacementFor(models.Model):
    title = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class EmployeeRequisition(models.Model):
    position = models.ForeignKey(Positions, on_delete=models.CASCADE, null=True, blank=True)
    supervisor = models.ForeignKey(Employees, on_delete=models.CASCADE, null=True, blank=True, related_name='supervisor')
    desired_start_date = models.DateField(null=True, blank=True)
    no_of_individuals  = models.IntegerField()
    proposed_salary = models.IntegerField(blank=True, null=True) 
    employee_type = models.ForeignKey(EmployeeTypes, on_delete=models.CASCADE, null=True, blank=True)
    replacement_for = models.ForeignKey(ReplacementFor, on_delete=models.CASCADE,null=True,blank=True)
    requisition_date = models.DateField(auto_now_add=True)
    replacement_of = models.ForeignKey(Employees, on_delete=models.CASCADE, null=True, blank=True, related_name='replacement_of')
    status = models.IntegerField( choices=Requisition_Status, default=1)
    reason = models.CharField(max_length=255, null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    jd_selection = models.ForeignKey(JdDescriptions, on_delete=models.CASCADE) 
    job = models.ForeignKey(Jobs, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    

# Create your models here.
