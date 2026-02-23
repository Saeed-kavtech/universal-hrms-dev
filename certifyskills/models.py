from django.db import models
from organizations.models import Organization
from profiles_api.models import HrmsUsers
from employees.models import Employees
import uuid
from helpers.model_utils import CommonFieldsModel
from payroll_compositions.models import SalaryBatch
from helpers.image_uploads import upload_certificate,upload_certificate_receipt
# Create your models here.

course_type = (
    (1, 'External'),
    (2, 'Online'),
)

relevance_choices = (
    (1, 'Project'),
    (2, 'Personal Goal'),
)



status_choices = (
    (1, 'Pending'),
    (2, 'Approved By Team Lead'),
    (3, 'Rejected By Team Lead'),
    (4, 'Approved By HR'),
    (5, 'Rejected By HR'),
)


reimbursement_status_choices = (
    (1, 'Reimbursement under process by Hr'),
    (2, 'Reimbursement approved by Hr'),
    (3, 'Reimbursement under process by Accountant'),
    (4, 'Reimbursement approved by Accountant'),
)

# Create your models here.
class LNDCertifications(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE,null=True,blank=True)
    title = models.TextField(null=True,blank=True)
    duration=models.IntegerField(null=True,blank=True)
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    mode_of_course = models.PositiveIntegerField(choices = course_type,null=True,blank=True)
    relevance = models.PositiveIntegerField(choices =relevance_choices,null=True,blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    certification_status = models.PositiveIntegerField(choices = status_choices,default=1)
    course_url=models.URLField(null=True,blank=True)
    processed_in = models.ForeignKey(SalaryBatch, on_delete=models.CASCADE, null=True, blank=True) 
    team_lead = models.ForeignKey(Employees, related_name='team_lead_user', on_delete=models.CASCADE, null=True, blank=True)
    approved_by = models.ForeignKey(HrmsUsers,related_name='approved_user', on_delete=models.CASCADE,null=True,blank=True)
    course_reason=models.TextField(null=True,blank=True)
    certificate= models.FileField(upload_to=upload_certificate, null=True, blank=True)
    certification_receipt= models.FileField(upload_to=upload_certificate_receipt, null=True, blank=True)
    feedback_comment =  models.CharField(max_length=250, null=True, blank=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    reimbursement_status=models.PositiveIntegerField(choices = reimbursement_status_choices,null=True,blank=True)
    is_reimbursement = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class LNDCertificationLogs(models.Model):
    certification = models.ForeignKey(LNDCertifications, on_delete=models.CASCADE)
    decision_reason= models.TextField()
    certification_status = models.PositiveIntegerField(choices = status_choices,null=True,blank=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

