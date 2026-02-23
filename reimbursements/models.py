from django.db import models
from organizations.models import StaffClassification, Organization
from employees.models import Employees
from profiles_api.models import HrmsUsers
from helpers.image_uploads import upload_gym_receipts, upload_medical_receipts, upload_leave_attachments
from payroll_compositions.models import SalaryBatch

GYM_STATUS_CHOICES = (
    ('in-progress', 'in-progress'),
    ('under-review', 'under-review'),
    ('approved', 'approved'),
    ('not-approved', 'not-approved'),
)

MEDICAL_STATUS_CHOICES = (
    ('in-progress', 'in-progress'),
    ('under-review', 'under-review'),
    ('approved', 'approved'),
    ('not-approved', 'not-approved'),
) 

PROVIDENT_FUND_STATUS_CHOICES = (
    ('in-progress', 'in-progress'),
    ('under-review', 'under-review'),
    ('approved', 'approved'),
    ('not-approved', 'not-approved'),
) 

LEAVES_STATUS_CHOICES = (
    ('in-progress', 'in-progress'),
    ('under-review', 'under-review'),
    ('approved', 'approved'),
    ('not-approved', 'not-approved'),
)

LEAVES_DATE_STATUS_CHOICES = (
    ('approved', 'approved'),
    ('not-approved', 'not-approved'),
)

LOAN_STATUS_CHOICES = (
    ('in-progress', 'in-progress'),
    ('under-review', 'under-review'),
    ('approved', 'approved'),
    ('not-approved', 'not-approved'),
)

NUMBER_OF_LOAN_INSTALLMENTS_CHOICES = (
    (4, '4'),
    (6, '6'),
    (8, '8'),
    (12, '12'),
)

PROCESSES_STATUS = (
    ('not-processed', 'not-processed'),
    ('processed-to-hr', 'processed-to-hr'),
    ('processed-to-accountant', 'processed-to-accountant'),
    ('processed-by-accountant', 'processed-by-accountant'),
)


WFH_REQUEST_STATUS_CHOICES= (
    ('in-progress', 'in-progress'),
    ('under-review', 'under-review'),
    ('approved', 'approved'),
    ('not-approved', 'not-approved'),
)

GENDER_Classification_CHOICES = [
        (1, 'Male'),
        (2, 'Female'),
        (3, 'Both'),  # Applicable to both genders
    ]

class GymAllowance(models.Model):
    staff_classification = models.ForeignKey(StaffClassification, on_delete=models.CASCADE)
    monthly_limit = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EmployeesGymAllowance(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    gym_allowance = models.ForeignKey(GymAllowance, on_delete=models.CASCADE)
    amount = models.IntegerField()
    gym_receipt = models.FileField(upload_to=upload_gym_receipts, null=True, blank=True)
    date = models.DateField()
    processed_status = models.CharField(max_length=100, choices=PROCESSES_STATUS, default='not-processed')
    processed_in = models.ForeignKey(SalaryBatch, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=100, choices=GYM_STATUS_CHOICES, default='in-progress')
    decision_reason = models.CharField(max_length=250, null=True, blank=True)
    additional_comments =  models.CharField(max_length=250, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class GymStatusLogs(models.Model):
    employee_gym_allowance = models.ForeignKey(EmployeesGymAllowance, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=GYM_STATUS_CHOICES)
    decision_reason = models.CharField(max_length=250, null=True, blank=True)
    action_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    action_on = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MedicalAllowance(models.Model):
    staff_classification = models.ForeignKey(StaffClassification, on_delete=models.CASCADE)
    yearly_limit = models.IntegerField()
    year=models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EmployeesMedicalAllowance(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    medical_allowance = models.ForeignKey(MedicalAllowance, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.IntegerField()
    medical_receipt = models.FileField(upload_to=upload_medical_receipts, null=True, blank=True)
    date = models.DateField()
    processed_status = models.CharField(max_length=100, choices=PROCESSES_STATUS, default='not-processed')
    processed_in = models.ForeignKey(SalaryBatch, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=100, choices=MEDICAL_STATUS_CHOICES, default='in-progress')
    decision_reason = models.CharField(max_length=250, null=True, blank=True)
    additional_comments =  models.CharField(max_length=250, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EmployeesRemainingMedicalAllowance(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    medical_allowance = models.ForeignKey(MedicalAllowance, on_delete=models.CASCADE, null=True, blank=True)
    remaining_allowance = models.IntegerField(null=True, blank=True)
    approved_amount = models.IntegerField(default=0, null=True, blank=True)
    inprogress_amount = models.IntegerField(default=0, null=True, blank=True)
    not_approved_amount = models.IntegerField(default=0, null=True, blank=True)
    under_review_amount = models.IntegerField(default=0, null=True, blank=True)
    emp_yearly_limit = models.IntegerField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MedicalStatusLogs(models.Model):
    employee_medical_allowance = models.ForeignKey(EmployeesMedicalAllowance, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=MEDICAL_STATUS_CHOICES)
    decision_reason = models.CharField(max_length=250, null=True, blank=True)
    action_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    action_on = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProvidentFunds(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    percentage = models.IntegerField()
    user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EmployeeProvidentFunds(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    provident_fund = models.ForeignKey(ProvidentFunds, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=100, choices=PROVIDENT_FUND_STATUS_CHOICES, default='in-progress')
    has_approval = models.BooleanField()
    approved_date = models.DateField(null=True, blank=True)
    decision_reason = models.CharField(max_length=250, null=True, blank=True)
    additional_comments =  models.CharField(max_length=250, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProvidentFundStatusLogs(models.Model):
    employee_provident_fund = models.ForeignKey(EmployeeProvidentFunds, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=PROVIDENT_FUND_STATUS_CHOICES)
    decision_reason = models.CharField(max_length=250, null=True, blank=True)
    action_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    action_on = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class LeaveTypes(models.Model):
    title = models.CharField(max_length=100)
    is_staff_classification = models.BooleanField(null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    tl_required=models.BooleanField(default=False)
    gender_classification =models.IntegerField(choices =GENDER_Classification_CHOICES,default=3)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SetLeavesDuration(models.Model):
    leave_types = models.ForeignKey(LeaveTypes, on_delete=models.CASCADE)
    staff_classification = models.ForeignKey(StaffClassification, on_delete=models.CASCADE, null=True, blank=True)
    allowed_leaves = models.IntegerField()
    year=models.IntegerField()
    is_lock = models.BooleanField(default=False)
    lock_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EmployeesLeaves(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    leave_types = models.ForeignKey(LeaveTypes, on_delete=models.CASCADE)
    set_leave_duration = models.ForeignKey(SetLeavesDuration, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.PositiveIntegerField(null=True, blank=True)
    remaining_casual_leaves = models.PositiveIntegerField(null=True, blank=True)
    remaining_annual_leaves = models.PositiveIntegerField(null=True, blank=True)
    decision_reason = models.CharField(max_length=250, null=True, blank=True)
    status = models.CharField(max_length=100, choices=LEAVES_STATUS_CHOICES, default='in-progress')
    attachment = models.FileField(upload_to=upload_leave_attachments, null=True, blank=True)
    team_lead= models.ForeignKey(Employees,related_name='emp_team_lead',on_delete=models.CASCADE,null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EmployeesOfficialHolidays(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EmployeeLeaveDates(models.Model):
    employee_leave = models.ForeignKey(EmployeesLeaves, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=100, choices=LEAVES_DATE_STATUS_CHOICES,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EmployeeLeaveCalculations(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, null=True, blank=True)
    set_leave_duration = models.ForeignKey(SetLeavesDuration, on_delete=models.CASCADE, null=True, blank=True)
    employee_leave_dates = models.ForeignKey(EmployeeLeaveDates, on_delete=models.CASCADE, null=True, blank=True)
    approved_leaves = models.PositiveIntegerField(default=0, null=True, blank=True)
    in_progress_leaves = models.PositiveIntegerField(default=0, null=True, blank=True)
    remaining_leaves = models.PositiveIntegerField(default=0,null=True, blank=True)
    underreview_leaves = models.PositiveIntegerField(default=0, null=True, blank=True)
    not_approved_leaves = models.PositiveIntegerField(default=0, null=True, blank=True)
    emp_yearly_leaves = models.PositiveIntegerField(default=0,null=True, blank=True)
    date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)





class LeavesStatusLogs(models.Model):
    employee_leave = models.ForeignKey(EmployeesLeaves, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=LEAVES_STATUS_CHOICES)
    decision_reason = models.CharField(max_length=250, null=True, blank=True)
    action_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    action_on = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
  
class LoanTypes(models.Model):
    title = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PurposeOfLoans(models.Model):
    title = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TimeFrequency(models.Model):
    title = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TimePeriod(models.Model):
    time_frequency = models.ForeignKey(TimeFrequency, on_delete=models.CASCADE)
    start_month = models.PositiveIntegerField(null=True, blank=True)
    end_month = models.PositiveIntegerField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SetLoanRequirements(models.Model):
    loan_type = models.ForeignKey(LoanTypes, on_delete=models.CASCADE)
    organization_cap_amount = models.PositiveIntegerField(null=True, blank=True) # company total cap
    emp_salary_factor = models.PositiveIntegerField(null=True, blank=True) # employee cap
    max_individual_loan_limit = models.PositiveIntegerField(null=True, blank=True)
    time_frequency = models.ForeignKey(TimeFrequency, on_delete=models.CASCADE, null=True, blank=True)
    emp_min_service_duration = models.PositiveIntegerField(null=True, blank=True) 
    is_provident_fund = models.BooleanField(default=False)
    min_provident_fund_duration = models.PositiveIntegerField(default=0)
    is_limit_exhausted = models.BooleanField(default=False)
    is_lock = models.BooleanField(default=False)
    lock_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, null=True, blank=True)
    locked_date = models.DateField(null=True, blank=True)
    unlock_by = models.ForeignKey(HrmsUsers, related_name='unlock_by', on_delete=models.CASCADE, null=True, blank=True)
    unlocked_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EmployeesLoan(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    set_loan_requirement = models.ForeignKey(SetLoanRequirements, on_delete=models.CASCADE, null=True, blank=True)
    loan_type = models.ForeignKey(LoanTypes, on_delete=models.CASCADE)
    purpose_of_loan = models.ForeignKey(PurposeOfLoans, on_delete=models.CASCADE)
    number_of_loan_installment = models.IntegerField(choices=NUMBER_OF_LOAN_INSTALLMENTS_CHOICES, null=True, blank=True)
    priority = models.PositiveIntegerField(null=True, blank=True)
    amount = models.PositiveIntegerField()
    reason = models.TextField(null=True, blank=True)
    loan_start_date = models.DateField(null=True, blank=True)
    loan_end_date = models.DateField(null=True, blank=True)
    decision_reason = models.CharField(max_length=250, null=True, blank=True)
    status = models.CharField(max_length=100, choices=LOAN_STATUS_CHOICES, default='in-progress')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class LoanStatusLogs(models.Model):
    employee_loan = models.ForeignKey(EmployeesLoan, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=LOAN_STATUS_CHOICES)
    decision_reason = models.CharField(max_length=250, null=True, blank=True)
    action_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    action_on = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ScriptStatusLogs(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, null=True, blank=True)
    staff_classification=models.ForeignKey(StaffClassification,on_delete=models.CASCADE,null=True, blank=True)
    year=models.IntegerField()
    script_title= models.CharField(max_length=50,null=True,blank=True)
    script_type= models.IntegerField(null=True,blank=True)
    action_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE,null=True,blank=True)
    is_completed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CompensatoryLeave(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='employee')
    date = models.DateField()
    reason = models.TextField(null=True, blank=True)
    jira_ticket = models.CharField(max_length=100, null=True, blank=True)
    team_lead = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='compensatory_team_lead')
    TEAM_LEAD_CHOICES = (
        ('pending by team lead', 'Pending By Team Lead'),
        ('approved by team lead', 'Approved By Team Lead'),
        ('rejected by team lead', 'Rejected By Team Lead'),
    )
    HR_CHOICES = (
        ('pending by hr', 'Pending By HR'),
        ('approved by hr', 'Approved By HR'),
        ('rejected by hr', 'Rejected By HR'),
    )
    team_lead_approval = models.CharField(max_length=30, choices=TEAM_LEAD_CHOICES, default='pending by team lead')
    hr_approval = models.CharField(max_length=30, choices=HR_CHOICES, default='pending by hr')
    # team_lead_approval = models.BooleanField(default=False)
    # hr_approval = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class EmployeesWFHAllowance(models.Model):
		employee = models.ForeignKey(Employees, on_delete=models.CASCADE,null=True,blank=True)
		organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
		limit= models.IntegerField()
		comment=  models.CharField(max_length=250, null=True, blank=True)
		created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
		is_active = models.BooleanField(default=True)
		created_at = models.DateTimeField(auto_now_add=True)
		updated_at = models.DateTimeField(auto_now=True)


class EmployeesWFHRequest(models.Model):
        employee = models.ForeignKey(Employees, on_delete=models.CASCADE)  # Assuming an Employee model exists
        # status = models.CharField(max_length=10, choices=WFH_REQUEST_STATUS_CHOICES, default="Pending")
        # approved_by = models.ForeignKey(HrmsUsers, related_name='approved_wfh_requests', on_delete=models.SET_NULL, null=True, blank=True)
        # approval_date = models.DateTimeField(null=True, blank=True)
        comment= models.TextField(null=True, blank=True)
        created_by = models.ForeignKey(HrmsUsers, related_name='created_wfh_requests', on_delete=models.CASCADE)
        is_active = models.BooleanField(default=True)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

class EmployeesWFHRequestDates(models.Model):
    employee_wfh_request = models.ForeignKey(EmployeesWFHRequest, on_delete=models.CASCADE)
    date = models.DateField()
    # status = models.CharField(max_length=100, choices=LEAVES_DATE_STATUS_CHOICES,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
