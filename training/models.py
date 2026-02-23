from django.db import models
from courses.models import *
from profiles_api.models import HrmsUsers
from helpers.image_uploads import upload_training_receipt,upload_assignment,upload_by_employee_assignment
# from employees.models import Projects
from payroll_compositions.models import SalaryBatch
from projects.models import Projects
from employees.models import Employees

status_choices = (
    (1, 'Pending'),
    (2, 'In Progress'),
    (3, 'Completed')
)

assignment_status_choices = (
    (1, 'Not Submitted'),
    (2, 'Submitted')
)

mode_of_training_choices=(
    (1,'Paid'),
    (2,'Free'),
)

choices_for_training=(
    (1, 'Active'),
    (2, 'Stop'),

)
reimbursement_status_choices = (
    (1, 'Reimbursement under process by Hr'),
    (2, 'Reimbursement approved by Hr'),
    (3, 'Reimbursement under process by Accountant'),
    (4, 'Reimbursement approved by Accountant'),
)
# Create your models here.


class Training(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE,null=True,blank=True)
    description = models.TextField(null=True, blank=True) 
    duration = models.IntegerField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    status=models.IntegerField(choices=choices_for_training,default=1)
    mode_of_training=models.IntegerField(choices=mode_of_training_choices,null=True,blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    evaluator = models.ForeignKey(Employees,related_name='evaluator',on_delete=models.CASCADE,null=True,blank=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TrainingEmployee(models.Model):
    training=models.ForeignKey(Training, on_delete=models.CASCADE,null=True,blank=True)
    employee =  models.ForeignKey(Employees, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    training_status=models.IntegerField(choices=status_choices,default=1)
    training_cost = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    reimbursed_cost = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    reimbursement_status=models.PositiveIntegerField(choices = reimbursement_status_choices,null=True,blank=True)
    is_reimbursement = models.BooleanField(default=False)
    training_receipt= models.FileField(upload_to=upload_training_receipt, null=True, blank=True)
    training_evaluator = models.ForeignKey(Employees,related_name='training_evaluator',on_delete=models.CASCADE,null=True,blank=True)
    processed_in = models.ForeignKey(SalaryBatch, on_delete=models.CASCADE, null=True, blank=True) 
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TrainingAssignments(models.Model):
    title = models.CharField(max_length=200) 
    training=models.ForeignKey(Training, on_delete=models.CASCADE,null=True,blank=True)
    assignment= models.FileField(upload_to=upload_assignment, null=True, blank=True)
    submission_deadline = models.DateTimeField(null=True, blank=True)
    marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EmployeeTrainingAssignment(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE,null=True,blank=True)
    training_assignment = models.ForeignKey(TrainingAssignments, on_delete=models.CASCADE,null=True,blank=True)  # Reference the original admin assignment
    assignment_file = models.FileField(null=True,blank=True)
    submitted_assignment = models.FileField(upload_to=upload_by_employee_assignment,null=True,blank=True)
    assignment_status=models.IntegerField(choices=assignment_status_choices,default=1)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Numeric field for grading
    obtained_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class ProjectTraining(models.Model):
    project=models.ForeignKey(Projects, on_delete=models.CASCADE,null=True,blank=True)
    training=models.ForeignKey(Training, on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




