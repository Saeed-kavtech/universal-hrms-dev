from django.db import models
from employees.models import Employees
from organizations.models import Organization

# Create your models here.

class Banks(models.Model):
	name = models.CharField(max_length=200)
	short_form =models.CharField(max_length=20, null=True, blank=True)
	code = models.CharField(max_length=20, null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class EmployeeBankDetails(models.Model):
	employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
	bank = models.ForeignKey(Banks, on_delete=models.CASCADE)
	branch_name = models.CharField(max_length=100, null=True, blank=True)
	account_no = models.CharField(max_length=20)
	account_title = models.CharField(max_length=200)
	iban = models.CharField(max_length=30, null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
 
 
class OrganizationBankDetail(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    account_title = models.CharField(max_length=255)
    account_number = models.CharField(max_length=21)
    bank_name = models.CharField(max_length=255)
    branch_name = models.CharField(max_length=255, null=True, blank=True)
    cif_number = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)









