from django.db import models
from organizations.models import StaffClassification, Organization
from departments.models import GroupHeads, Departments
from jd.models import JdDescriptions
from positions.models import Positions
from profiles_api.models import HrmsUsers
from helpers.image_uploads import upload_employee_profile, upload_employee_cnic, upload_employee_passport, upload_employee_attachments, upload_employee_degrees
import uuid
from roles.models import Roles
from projects.models import Projects



gender_choices = (
    (1, 'Male'),
    (2, 'Female')
)

marital_choices = (
	(1, 'Not Married'),
	(2, 'Married')
)

blood_group_choices = (
	('A+', 'A+'),
	('A-', 'A-'),
	('B+', 'B+'),
	('B-', 'B-'),
	('AB+', 'AB+'),
	('AB-', 'AB-'),
	('O+', 'O+'),
	('O-', 'O-'),
)

WORK_ARRANGEMENT_CHOICES = [
        ('remote', 'Remote'),
        ('onsite', 'Onsite'),
        ('hybrid', 'Hybrid'),
    ]

# permanent, wfh, intern
class EmployeeTypes(models.Model):                
    title = models.CharField(max_length=200)  
    level = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Employees(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
	code = models.CharField(max_length=30) # unique=True
	emp_code = models.IntegerField(null=True, blank=True)
	hrmsuser = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, related_name='user_type', null=True, blank=True)
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
	department = models.ForeignKey(Departments, on_delete=models.CASCADE, null=True, blank=True)
	staff_classification = models.ForeignKey(StaffClassification, on_delete=models.CASCADE, null=True, blank=True)
	position = models.ForeignKey(Positions, on_delete=models.CASCADE, null=True, blank=True)
	first_name = models.CharField(max_length=200, null=True, blank=True)
	middle_name =  models.CharField(max_length=200, null=True, blank=True)
	last_name = models.CharField(max_length=200, null=True, blank=True)
	current_salary = models.IntegerField(blank=True, null=True)
	starting_salary =  models.IntegerField(blank=True, null=True)
	is_multi_role = models.BooleanField(default=False)
	work_mode=models.CharField(max_length=20, choices= WORK_ARRANGEMENT_CHOICES,default='onsite')
	name = models.CharField(max_length=200)
	official_email = models.EmailField(max_length=255, null=True, blank=True)
	personal_email = models.EmailField(max_length=255, null=True, blank=True)
	profile_image = models.ImageField(upload_to=upload_employee_profile, null=True, blank=True)
	father_name = models.CharField(max_length=200, blank=True, null=True)
	dob = models.DateField(blank=True, null=True) #eg '2013-01-29'
	cnic_no = models.CharField(max_length=15) 
	gender = models.IntegerField(choices = gender_choices)
	marital_status = models.IntegerField(choices=marital_choices, null=True, blank=True)
	blood_group = models.CharField(max_length=5, choices=blood_group_choices, null=True, blank=True)
	employee_type = models.ForeignKey(EmployeeTypes, on_delete=models.CASCADE, null=True, blank=True)
	skype = models.CharField(max_length=100, null=True, blank=True)
	joining_date = models.DateField(null=True, blank=True)
	leaving_date = models.DateField(null=True, blank=True) 
	leaving_reason = models.CharField(max_length=250, null=True, blank=True)
	hiring_comment = models.CharField(max_length=250, null=True, blank=True)
	status = models.IntegerField(null=True, blank=True)
	created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, related_name='emp_creator')
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)



class EmployeePassports(models.Model):
	employee = models.ForeignKey(Employees, related_name= 'passport_data', on_delete=models.CASCADE)
	passport_no = models.CharField(max_length=20)
	date_of_issue = models.DateField(null=True, blank=True)
	date_of_expiry = models.DateField(null=True, blank=True)
	tracking_no = models.CharField(max_length=50, null=True, blank=True)
	booklet_no = models.CharField(max_length=50, null=True, blank=True)
	country_code = models.CharField(max_length=20, null=True, blank=True)
	passport_type = models.CharField(max_length=10, null=True, blank=True)
	issuing_authority = models.CharField(max_length=50, null=True, blank=True)
	attachment = models.ImageField(upload_to=upload_employee_passport, blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class EmployeeCnic(models.Model):
	
	employee = models.ForeignKey(Employees, related_name= 'cnic_data', on_delete=models.CASCADE)
	cnic = models.CharField(max_length=15)
	date_of_issue = models.DateField(null=True, blank=True)
	date_of_expiry = models.DateField(null=True, blank=True)
	front_image = models.ImageField(upload_to=upload_employee_cnic, blank=True, null=True)
	back_image = models.ImageField(upload_to=upload_employee_cnic, blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class AttachmentTypes(models.Model):
	title = models.CharField(max_length=100)
	is_degree = models.BooleanField(default=False)
	is_letter = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class EmployeeAttachments(models.Model):
	employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
	attachment_type = models.ForeignKey(AttachmentTypes, on_delete=models.CASCADE)
	attachment = models.FileField(upload_to=upload_employee_attachments)
	description = models.TextField(blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class ContactRelations(models.Model):
	relation = models.CharField(max_length=50, unique=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class EmployeeEmergencyContacts(models.Model):
	employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
	relation = models.ForeignKey(ContactRelations, on_delete=models.CASCADE, null=True, blank=True)
	name = models.CharField(max_length=200, null=True, blank=True)
	mobile_no = models.CharField(max_length=20, null=True, blank=True)
	landline = models.CharField(max_length=20, null=True, blank=True)
	address = models.CharField(max_length=200, null=True, blank=True)
	email = models.EmailField(null=True, blank=True)
	imid = models.CharField(max_length=20, null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class Dependent(models.Model):
	relationship = models.CharField(max_length=50, unique=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class EmployeeDependent(models.Model):
	employee = models.ForeignKey(Employees, on_delete=models.CASCADE)	
	name =  models.CharField(max_length=200, null=True, blank=True)
	relationship = models.ForeignKey(Dependent, on_delete=models.CASCADE)
	date_of_birth = models.DateField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


# class EmployeeRoleTypes(models.Model):
# 	title = models.CharField(max_length=250, unique=True)
# 	level = models.IntegerField(null=True, blank=True)
# 	is_active = models.BooleanField(default=True)
# 	created_at = models.DateTimeField(auto_now_add=True)
# 	updated_at = models.DateTimeField(auto_now=True)


class EmployeeProjects(models.Model):
	employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
	project = models.ForeignKey(Projects, on_delete=models.CASCADE, null=True, blank=True)
	jira_account_id = models.CharField(max_length=250, null=True, blank=True)
	project_assigned_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class EmployeeProjectsLogs(models.Model):
	employee_project = models.ForeignKey(EmployeeProjects, related_name='project_logs', on_delete=models.CASCADE, null=True, blank=True)
	employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
	project = models.ForeignKey(Projects, on_delete=models.CASCADE, null=True, blank=True)
	request_type = models.CharField(max_length=100, null=True, blank=True)
	action_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, null=True, blank=True)
	emp_project_is_active = models.BooleanField(default=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class EmployeeRoles(models.Model):
	employee_project = models.ForeignKey(EmployeeProjects, on_delete=models.CASCADE, null=True, blank=True)
	role = models.ForeignKey(Roles, on_delete=models.CASCADE)
	# employee_role_type = models.ForeignKey(EmployeeRoleTypes, on_delete=models.CASCADE, null=True, blank=True)
	start_date = models.DateField(null=True, blank=True) 
	end_date = models.DateField(null=True, blank=True)
	role_assigned_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class EmployeeRolesLogs(models.Model):
	employee_role = models.ForeignKey(EmployeeRoles, related_name='role_logs', on_delete=models.CASCADE, null=True, blank=True)
	employee_project = models.ForeignKey(EmployeeProjects, on_delete=models.CASCADE, null=True, blank=True)
	role = models.ForeignKey(Roles, on_delete=models.CASCADE, null=True, blank=True)
	# employee_role_type = models.ForeignKey(EmployeeRoleTypes, on_delete=models.CASCADE, null=True, blank=True)
	request_type = models.CharField(max_length=100, null=True, blank=True)
	start_date = models.DateField(null=True, blank=True) 
	end_date = models.DateField(null=True, blank=True)
	action_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, null=True, blank=True)
	emp_role_is_active = models.BooleanField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class SystemRoles(models.Model):
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(HrmsUsers, related_name='admin_user', on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    assigned_by = models.ForeignKey(HrmsUsers, related_name='action_by', on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EmployeeResume(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, null=True, blank=True)
    resume_data = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


