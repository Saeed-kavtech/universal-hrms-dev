from django.db import models
from organizations.models import Organization, StaffClassification
from profiles_api.models import HrmsUsers
from employees.models import Employees
from django.utils import timezone
import uuid

BATCH_STATUS_CHOICES = (
    ('unlock', 'unlock'),
    ('lock', 'lock')
)

SALARY_BATCH_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('in-progress', 'In Progress'),
    ('transferred', 'Transferred')
)

TRANSFER_STATUS = (
    ('pending', 'Pending'),
    ('transferred', 'Transferred')
)


PAYROLL_CHOICES = (
    ('Addon','Addon'),
    ('Deduction','Deduction')
)

valueType_CHOICES = (
    (3,'Formula'),
    (2,'Fixed'),
    (1,'FFSC'),
    (4,'FFGS'),
    (5,'Variable'),
    (6,'VSC'),
    (7,'VGS')
    
)

takeaway_types_options = (
    ('Monthly','Monthly'),
    ('Semi-Monthly','Semi-Monthly'),
    ('Bi-Weekly','Bi-Weekly'),
    ('Weekly','Weekly'),    
)

payment_frequency_choices = (
    ('Monthly', 'Monthly'),
    ('Yearly', 'Yearly')
)

COUNTRY_CHOICES = [
    ('PK', 'Pakistan'),
    ('AE', 'United Arab Emirates (Dubai)'),
    ('US', 'United States of America'),
    # Add more countries as needed
]




class CompositionAttributes(models.Model):
    title = models.CharField(max_length=250)
    level = models.PositiveIntegerField() # organization based unique
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TaxSlab(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    initial_income_threshold = models.DecimalField(max_digits=20, decimal_places=2)
    income_ceiling = models.DecimalField(max_digits=20, decimal_places=2)
    exemption_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    fixed_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_lock = models.BooleanField(default=False)
    # lock_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, blank=True, null=True)

class PayrollBatches(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    batch_no = models.CharField(max_length=20)
    title = models.CharField(max_length=50, null=True, blank=True)
    batch_status = models.CharField(max_length=50, choices=BATCH_STATUS_CHOICES, default='unlock')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_lock = models.BooleanField(default=False)
    lock_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, null=True, blank=True)
    
    # Create your models here.
class EmployeePayrollConfiguration(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    payroll_batch = models.ForeignKey(PayrollBatches, on_delete=models.CASCADE, null=True, blank=True)
    is_salary_allowed = models.BooleanField(null=True)
    is_payslip_allowed = models.BooleanField(null=True)
    is_active = models.BooleanField(default=True)
    takeAway = models.CharField(max_length=50, choices=takeaway_types_options, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class EmployeePayrollConfigurationLog(models.Model):
    action_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # Fields to store the old and new values for each field that can change
    is_salary_allowed_old = models.BooleanField(null=True)
    is_salary_allowed_new = models.BooleanField(null=True)
    is_payslip_allowed_old = models.BooleanField(null=True)
    is_payslip_allowed_new = models.BooleanField(null=True)
    old_payroll_batch = models.ForeignKey(PayrollBatches, on_delete=models.CASCADE, related_name='old_payroll_batch',  null=True, blank=True)
    new_payroll_batch = models.ForeignKey(PayrollBatches, on_delete=models.CASCADE, related_name='new_payroll_batch', null=True, blank=True)
    is_active_old = models.BooleanField(null=True)
    is_active_new = models.BooleanField(null=True)
    takeAway_old = models.CharField(max_length=50, choices=takeaway_types_options, null=True)
    takeAway_new = models.CharField(max_length=50, choices=takeaway_types_options, null=True)
    
class valueTypeChoices(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class customisedAttributes(models.Model):
    title = models.CharField(max_length=255)
    

class PayrollAttributes(models.Model):
    payroll_type = models.CharField(max_length=50, choices=PAYROLL_CHOICES, default='Addon')
    valueType =models.ForeignKey(valueTypeChoices, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    # is_Taxable = models.BooleanField(default= False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_employee_base = models.BooleanField(default= False)
    is_organization_base = models.BooleanField(default=True)
    is_customized = models.BooleanField(default=False)
    customized_id = models.ForeignKey(customisedAttributes, on_delete=models.CASCADE, null=True, blank=True)
    payment_frequency = models.CharField(max_length=50, choices=payment_frequency_choices, default='Monthly')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class PayrollBatchAttributes(models.Model):
    payroll_batch = models.ForeignKey(PayrollBatches, on_delete=models.CASCADE) 
    payroll_attribute = models.ForeignKey(PayrollAttributes, on_delete=models.CASCADE)
    is_Taxable = models.BooleanField(null=True, blank=True, default=False)
    payroll_batch_status = models.CharField(max_length=50, choices=BATCH_STATUS_CHOICES, default='unlock')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    
class SalaryBatch(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    batch_no = models.CharField(max_length=30)
    payroll_batch = models.ForeignKey(PayrollBatches, on_delete=models.CASCADE)
    batch_status = models.CharField(max_length=50, choices=SALARY_BATCH_STATUS_CHOICES, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_lock = models.BooleanField(default=False)
    lock_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    salary_amount = models.DecimalField(max_digits=20, decimal_places=2,null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=20, decimal_places=2,null=True, blank=True)
    addons_amount = models.DecimalField(max_digits=20, decimal_places=2,null=True, blank=True)
    deduction_amount = models.DecimalField(max_digits=20, decimal_places=2,null=True, blank=True)
    customised_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    batch_total = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2)
    is_gross_allowed = models.BooleanField(null=True, blank=True)
    
class ProcessedSalary(models.Model):
    salary_batch = models.ForeignKey(SalaryBatch, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    net_salary = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    gross_salary = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    taxable_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    non_taxable_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    taxable_amount_addons = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    non_taxable_amount_addons = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    taxable_amount_deductions = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    non_taxable_amount_deductions = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_addons = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_deductions = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_customized = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    tax = models.ForeignKey(TaxSlab, on_delete=models.CASCADE, null=True, blank=True)
    addons = models.JSONField(null=True, blank=True)
    deductions = models.JSONField(null=True, blank=True)
    customised = models.JSONField(null=True, blank=True)    
    compositions = models.JSONField(null=True, blank=True) 
    bank_account_no = models.CharField(max_length=20, null=True, blank=True)
    bank_name = models.CharField(max_length = 50, null=True, blank=True)
    transfer_status = models.CharField(max_length=50, choices=TRANSFER_STATUS, default='pending')
    bank_code = models.CharField(max_length=20, null=True, blank=True)
    
    
class SalaryBatchAttributes(models.Model):
    # payroll_attribute = models.ForeignKey(PayrollAttributes, on_delete=models.CASCADE)
    payroll_batch_attribute = models.ForeignKey(PayrollBatchAttributes, on_delete=models.CASCADE)
    salary_batch = models.ForeignKey(SalaryBatch, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)

class PayrollBatchCompositions(models.Model):
    payroll_compositions_attribute = models.ForeignKey(CompositionAttributes, on_delete=models.CASCADE) 
    payroll_batch = models.ForeignKey(PayrollBatches, on_delete=models.CASCADE) 
    attribute_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    composition_status = models.CharField(max_length=50, choices=BATCH_STATUS_CHOICES, default='unlock')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class Process(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class OrganizationProcesses(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PayrollAttributesLogs(models.Model):
    payroll_attribute = models.ForeignKey(PayrollAttributes, on_delete=models.CASCADE)
    org_process = models.ForeignKey(OrganizationProcesses, on_delete=models.CASCADE)
    value = models.IntegerField(null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class PayrollCustomisedGymProcesses(models.Model):
    salary_batch = models.ForeignKey(SalaryBatch, on_delete=models.CASCADE) 
    payroll_batch_attribute = models.ForeignKey(PayrollBatchAttributes, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(null= True, blank=True)
    no_of_data = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    
class PayrollCustomisedMedicalProcesses(models.Model):
    salary_batch = models.ForeignKey(SalaryBatch, on_delete=models.CASCADE) 
    payroll_batch_attribute = models.ForeignKey(PayrollBatchAttributes, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(null=True, blank=True)
    no_of_data = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    
class PayrollCustomisedCertificationsProcesses(models.Model):
    salary_batch = models.ForeignKey(SalaryBatch, on_delete=models.CASCADE) 
    payroll_batch_attribute = models.ForeignKey(PayrollBatchAttributes, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(null=True, blank=True)
    no_of_data = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    
    
class PayrollCustomisedTrainingProcesses(models.Model):
    salary_batch = models.ForeignKey(SalaryBatch, on_delete=models.CASCADE) 
    payroll_batch_attribute = models.ForeignKey(PayrollBatchAttributes, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(null=True, blank=True)
    no_of_data = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    
class PayrollCustomisedPFProcesses(models.Model):
    salary_batch = models.ForeignKey(SalaryBatch, on_delete=models.CASCADE) 
    payroll_batch_attribute = models.ForeignKey(PayrollBatchAttributes, on_delete=models.CASCADE)
    amount = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=20)
    no_of_data = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    
class PFRecords(models.Model):
    salary_batch = models.ForeignKey(SalaryBatch, on_delete=models.CASCADE) 
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    amount = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=20)
    should_include = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    
    
    
    
class MonthlyDistribution(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    payroll_attribute = models.ForeignKey(PayrollAttributes, on_delete=models.CASCADE)
    payroll_batch = models.ForeignKey(PayrollBatches, on_delete=models.CASCADE)
    # salary_batch = models.ForeignKey(SalaryBatch, on_delete=models.CASCADE)
    staff_classification = models.ForeignKey(StaffClassification, on_delete=models.CASCADE)
    amount = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class FixedDistribution(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    payroll_batch = models.ForeignKey(PayrollBatches, on_delete=models.CASCADE)
    payroll_attribute = models.ForeignKey(PayrollAttributes, on_delete=models.CASCADE, null=True, blank=True)
    # salary_batch = models.ForeignKey(SalaryBatch, on_delete=models.CASCADE)
    amount = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   

class EligibleEmployees(models.Model):
    employee= models.ForeignKey(Employees, on_delete=models.CASCADE)
    payroll_batch = models.ForeignKey(PayrollBatches, on_delete=models.CASCADE)
    payroll_attribute = models.ForeignKey(PayrollAttributes, on_delete=models.CASCADE)
    is_active= models.BooleanField(default=True)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
class VariableDistributions(models.Model):
    payroll_attribute = models.ForeignKey(PayrollAttributes, on_delete=models.CASCADE)
    salary_batch = models.ForeignKey(SalaryBatch, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    amount = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    
  
class PayrollBatchAttributeEmployee(models.Model):
    payroll_batch = models.ForeignKey(PayrollBatches, on_delete=models.CASCADE) 
    payroll_attribute = models.ForeignKey(PayrollAttributes, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class EmployeePayrollBatchAttributeLog(models.Model):
    epa_id = models.ForeignKey(PayrollBatchAttributeEmployee, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class BatchSalary(models.Model):
    month = models.PositiveIntegerField()
    year= models.PositiveIntegerField()
    title = models.CharField(max_length=255, blank=True)  # Field for the title
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    


    
        
    
    
    
    


# class PayrollBatchCompositionLogs(models.Model):
#     payroll_attribute = models.ForeignKey(PayrollAttributes, on_delete=models.CASCADE) 
#     payroll_batch = models.ForeignKey(PayrollBatches, on_delete=models.CASCADE) 
#     attribute_percentage = models.DecimalField(max_digits=5, decimal_places=2)
#     is_active = models.BooleanField(default=True)
#     current_time = models.DateTimeField()
#     action_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, null=True, blank=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
