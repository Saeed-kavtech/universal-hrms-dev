# Create your models here.
from django.db import models
from organizations.models import Organization
from profiles_api.models import HrmsUsers
from employees.models import Employees
import uuid
from organizations.models import Organization
from departments.models import Departments

# Create your models here.

status_choices = (
    (1, 'Pending'),
    (2,'In Progress by Team Lead'),
    (3,'Rejected by Team Lead'),
    (4,'Approved by Team Lead'),
    (5,'In Progress by CTO'),
    (6,'Rejected by CTO'),
    (7,'Approved by CTO'),
    (8,'In Progress'),
    (9,'Rejected'),
    (10,'Solved'),
    (11,'In Progress by Main Admin'),
    (12,'Reject by Main Admin'),
    (13,'Solved by Main Admin'),
)

category_choices = (
    (1, 'Procurement'),
    (2, 'General'),
    (3,'HR Services')
)


class TicketCategory(models.Model):
    title = models.CharField(max_length=150,null=True,blank=True)
    organization =models.ForeignKey(Organization, on_delete=models.CASCADE,null=True,blank=True)
    is_department=models.BooleanField(default=True)
    is_main_admin=models.BooleanField(default=False)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class TicketCategoryDepartment(models.Model):
    ticket_category=models.ForeignKey(TicketCategory, on_delete=models.CASCADE,null=True,blank=True)
    department=models.ForeignKey(Departments, on_delete=models.CASCADE,null=True,blank=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class TicketDepartmentEmployee(models.Model):
    ticket_category_department = models.ForeignKey(TicketCategoryDepartment,on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(Employees,on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    

class Ticket(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE,null=True,blank=True)
    subject = models.TextField(null=True,blank=True)
    ticket_department=models.ForeignKey(Departments, on_delete=models.CASCADE,null=True,blank=True)
    assign_to = models.ForeignKey(Employees, related_name='assign_to', on_delete=models.CASCADE, null=True, blank=True)
    transfer_to=models.ForeignKey(Employees, related_name='transfer_to', on_delete=models.CASCADE, null=True, blank=True)
    team_lead = models.ForeignKey(Employees, related_name='team_lead', on_delete=models.CASCADE, null=True, blank=True)
    description=models.TextField(null=True,blank=True)
    ticket_status = models.PositiveIntegerField(choices = status_choices,default=1)
    category=models.ForeignKey(TicketCategory,on_delete=models.CASCADE,related_name='department_category', null=True, blank=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    send_to_admin=models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
 

class TicketLogs(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    decision_reason= models.TextField(null=True,blank=True)
    ticket_status = models.PositiveIntegerField(choices = status_choices,null=True,blank=True)
    decision_by = models.ForeignKey(HrmsUsers,related_name='decision_by', on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

