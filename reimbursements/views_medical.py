from rest_framework import viewsets
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from email_templates.models import EmailRecipients
from .serializers import (
    ListEmployeesPendingMedicalAllowanceSerializers, MedicalAllowanceSerializers, UpdateMedicalAllowanceSerializers, 
    EmployeesMedicalAllowanceSerializers, UpdateEmployeesMedicalAllowanceSerializers, 
    MedicalStatusLogsSerializers, EmployeesRemainingMedicalAllowanceSerializers
)
from .models import (
    MedicalAllowance, EmployeesMedicalAllowance, MedicalStatusLogs, 
   EmployeesRemainingMedicalAllowance
)
from helpers.status_messages import (
    errorMessageWithData, exception, errorMessage, success, successMessage, successfullyCreated, 
    successfullyUpdated, serializerError, successMessageWithData
)

from helpers.decode_token import decodeToken
from helpers.email_data import requestEmailsFromEmployees, requestDecisionFromManagement, requestEmailsFromEmployeesnontl
from helpers.custom_permissions import IsAuthenticated, IsEmployeeOnly,IsAdminOnly
from organizations.models import StaffClassification
from employees.models import Employees
import csv
import os
import pandas as pd

import datetime
import calendar
import boto3
from .Scriptinglogs import script_logs

class MedicalAllowanceViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = MedicalAllowance.objects.all()
    serializer_class = MedicalAllowanceSerializers

    def get_queryset(self):
        organization_id = decodeToken(self, self.request)['organization_id']
        return self.queryset.filter(staff_classification__organization=organization_id)

    def list(self, request, *args, **kwargs):
        try:
            query = self.get_queryset().filter(is_active=True)
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            # if not request.user.is_privileged:
            #     return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
        
            required_fields=['staff_classification','yearly_limit']
            already_exists_error=[]
            data=[]


            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [staff_classification,yearly_limit]')
            
            staff_classification_id = request.data['staff_classification']

            
            staff_classification = StaffClassification.objects.filter(id=staff_classification_id, organization=organization_id)
            if not staff_classification.exists():
                return errorMessage("Staff classification does not exists")
            elif not staff_classification.filter(is_active=True).exists():
                return errorMessage("staff classification is deactivated")
            request.data['staff_classification'] = staff_classification_id

            current_year =datetime.datetime.today().year
            next_year = current_year + 1

            years=[current_year,next_year]

            for year in years:
                query = self.get_queryset().filter(year=year,staff_classification=staff_classification_id, is_active=True)
                # print(query.values())
                if query.exists():
                    already_exists_error.append(year)
                    continue
                    # return errorMessage("Already value exists against this staff_classification")
                request.data['year']=year
                serializer = self.serializer_class(data = request.data)
                if not serializer.is_valid():
                    return serializerError(serializer.errors)
                serializer.save()
                data.append(serializer.data)



            if already_exists_error:
                    return errorMessage("Year limit already set")



            return successMessageWithData("Success",data)
        except Exception as e:
            return exception(e)
        
    


    def patch(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('No Medical allowance exists at this id')

            obj = query.get()
            serializer = UpdateMedicalAllowanceSerializers(obj, data=request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)
        

    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('No Medical allowance exists at this id')
            if not query.filter(is_active=True):
                return errorMessage('Medical Allowance is deactivated at this id')
            
            obj = query.get()
            obj.is_active = False
            obj.save()
            return successMessage('Sucessfully deactivated')
        except Exception as e:
            return exception(e)
    
    def get_pre_data(self, organization_id):
        try:
            
            year=datetime.datetime.today().year
            query = MedicalAllowance.objects.filter(staff_classification__organization=organization_id,year=year, is_active=True).order_by('-id')
            serializer = MedicalAllowanceSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            return None
        
class EmployeesMedicalAllowanceViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsEmployeeOnly]
    queryset = EmployeesMedicalAllowance.objects.all()
    serializer_class = EmployeesMedicalAllowanceSerializers

    def get_queryset(self):
        token_data = decodeToken(self, self.request)
        organization_id = token_data['organization_id']
        employee_id = token_data['employee_id']
        return self.queryset.filter(employee=employee_id, employee__organization=organization_id)

    def list(self, request, *args, **kwargs):
        try:
            query = self.get_queryset().filter(is_active=True).order_by('-id')
            # print("Test")
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def retrieve(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            query = self.get_queryset().filter(id=pk, is_active=True)
            if not query.exists():
                return errorMessage('No employee medical allowance exists at this id')
            obj = query.get()
            serializer = self.serializer_class(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def get_employee_yearly_limit(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            emp_query = Employees.objects.filter(id=employee_id, organization=organization_id)
            
            obj = emp_query.get()
            joining_date = obj.joining_date
            if not joining_date:
                return errorMessage('Joining date missing. Please ask administrator to add the joining date')

            staff_classification = obj.staff_classification
            if not staff_classification:
                return errorMessage('Staff classification missing. Please ask administrator to add the staff classification')
            medical_allowance = MedicalAllowance.objects.filter(
                staff_classification=staff_classification.id, 
                staff_classification__organization=organization_id,
                is_active=True
            )

            if not medical_allowance.exists():
                return errorMessage('No medical allowance exists at this id')
            
            medical_allowance = medical_allowance.get()
            yearly_limit = medical_allowance.yearly_limit
            result = {
                'status': 200, 
                'message': 'Success',
                'yearly_limit': yearly_limit, 
                'system_error_message': ''
            }
            month = 12 - joining_date.month + 1
            result['yearly_limit'] = round(( yearly_limit / 12 ) * month)
            return Response(result)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            employees = Employees.objects.filter(hrmsuser=request.user.id)
            emp = employees.get()
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            
            joining_date = emp.joining_date
            # print(joining_date)
            # print(emp.staff_classification)

            # print(request.data)
            if not emp.staff_classification:
                return errorMessage("Add staff classification of the employee first")
            elif not emp.employee_type:
                return errorMessage("Employee type is a required field")
            elif not emp.employee_type.title == 'Permanent':
                return errorMessage('Only Permanent Employees is elligible for medical allowance')
            elif not joining_date:
                return errorMessage(
                    'Joining Date Missing. Please contact the administrator to add the joining date first.' 
                )
            
            # print("Test:",request.data)
            required_fields = ['amount', 'medical_receipt']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [amount, medical_receipt]')
            

            request.data_mutable = True
            request.data['employee'] = emp.id
            request.data['is_active'] = True
            
            current_date=datetime.datetime.today().date()
            if current_date.day>20:
                return errorMessage("Cannot apply for medical after the 20th.")
            date_str = current_date
            # print( date_str)
            valid_time_duration_check = self.check_reimbursement_time_duration(date_str, pk=None)
            if valid_time_duration_check['status'] == 400:
                return errorMessage(valid_time_duration_check['message'])
            date_year = valid_time_duration_check['year']


            # print(date_year)
            request.data['date']=date_str
            
            query = MedicalAllowance.objects.filter(staff_classification=emp.staff_classification,year=date_year,is_active=True)
            if not query.exists():
                return errorMessage("No medical allowance exists against this staff classification in seleted date year")    
            # print(query.values())
            obj = query.get()

            # print(request.data)
            medical_allownance_check=EmployeesRemainingMedicalAllowance.objects.filter(medical_allowance=obj,employee__organization=organization_id,employee=employee_id,is_active=True)
            if not medical_allownance_check.exists():
                return errorMessage('Your allowance limit is not set')
            
            # print(obj)
            request.data['medical_allowance'] = obj.id
            amount = request.data['amount']
            request.data['status'] = 'in-progress'
            
            amount = int(amount)

            if amount < 0:
                return errorMessage('Amount should be greater than 0')

            yearly_limit = obj.yearly_limit

            if amount > yearly_limit:
                return errorMessage('Medical allowance cannot be greater than the limit')
           
            emp_remaining_allowance = EmployeesRemainingMedicalAllowance.objects.filter(
                employee = emp.id,
                medical_allowance=obj,
                is_active = True
            )
            # print("test1:",emp_remaining_allowance.values())
            if emp_remaining_allowance.exists():
                emp_remaining_allowance_obj = emp_remaining_allowance.get() 

                emp_yearly_limit = emp_remaining_allowance_obj.emp_yearly_limit
                in_progress_amount = emp_remaining_allowance_obj.inprogress_amount
                approved_amount = emp_remaining_allowance_obj.approved_amount
                under_review_amount = emp_remaining_allowance_obj.under_review_amount

                # print(emp_yearly_limit)
                # print(in_progress_amount)
                # print(approved_amount)
                # print(under_review_amount)

                emp_remaining_allowance_obj.inprogress_amount = in_progress_amount + amount
                total_amount = amount + (in_progress_amount or 0) + (under_review_amount or 0) + (approved_amount or 0)
                
                

                if total_amount > emp_yearly_limit:
                    return errorMessage(
                        'Limit exceeded. The sum of your in-progress, under review, and approved amounts exceeds the total limit.'
                    )

        
            
            serializer = self.serializer_class(data = request.data)
        
            if not serializer.is_valid():
                # print(serializer.errors)
                if serializer.errors.get('medical_receipt'):
                    return errorMessage(serializer.errors.get('medical_receipt', [''])[0])
                
                return serializerError(serializer.errors)
            
            if emp_remaining_allowance.exists():
                # pass
                emp_remaining_allowance_obj.save() 

            # print(serializer.data)
            
            serializer.save()
            cc_employee=EmailRecipients.objects.filter(employee__organization=organization_id,level=2,is_active=True)

            if cc_employee.exists():
                eobj=cc_employee.get()
                requestEmailsFromEmployeesnontl(emp.name,'Medical Application Received',"Medical",eobj.employee.official_email,eobj.employee.name)
            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)    
        
    def patch(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('This employee has no medical allowance at this id')
            obj = query.get()

            if request.data:
                request.data._mutable = True

                if 'date' in request.data:
                    date_str = request.data['date']
                    valid_time_duration_check = self.check_reimbursement_time_duration(date_str, pk=pk)
                    if valid_time_duration_check['status'] == 400:
                        return errorMessage(valid_time_duration_check['message'])

            serializer = UpdateEmployeesMedicalAllowanceSerializers(obj, data = request.data, partial=True)
            if not serializer.is_valid():
                if serializer.errors.get('medical_receipt'):
                    return errorMessage(serializer.errors.get('medical_receipt', [''])[0])
                   
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)
    
    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('Does not exists at this id')
            elif query.filter(is_active=False).exists():
                return errorMessage('Already deactivated')
            
            obj = query.get()
            status = obj.status
            amount = obj.amount

            if status != 'in-progress':
                return errorMessage('Only in progress requests could be delete')
            year = datetime.date.today().year
            emp_remaining_allowance = EmployeesRemainingMedicalAllowance.objects.filter(
                employee=obj.employee, 
                medical_allowance=obj.medical_allowance,
                is_active=True
            )

            if not emp_remaining_allowance.exists():
                return errorMessage('This year employee remaining allowance has not been set yet')
            
            emp_remaining_allowance = emp_remaining_allowance.get()
            emp_remaining_allowance.inprogress_amount = emp_remaining_allowance.inprogress_amount - amount
            
            obj.is_active = False
            obj.save()
            emp_remaining_allowance.save()
            return successMessage("Deactivated Successfully")
        except Exception as e:
            return exception(e)
        
    def get_pre_data(self, request,*args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            employee_id = decodeToken(self, self.request)['employee_id']
            year=request.data.get('year',None)
            if year is None:
                year=datetime.datetime.today().year
            query = EmployeesMedicalAllowance.objects.filter(employee=employee_id, employee__organization=organization_id,date__year=year,is_active=True)
            serializer = EmployeesMedicalAllowanceSerializers(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return None  

    def check_reimbursement_time_duration(self, date_str, pk):
        try:
            result = {'status': 400, 'message': None, 'year': None, 'system_error_message': ''}
            # print(date_str)
            # date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            # print(date)
            date=date_str
            date_year = date.year
            # print(date_year)
            atmost_time_allowed_unformatted = datetime.date.today() - datetime.timedelta(days=60)
            atmost_time_allowed = datetime.datetime.strptime(str(atmost_time_allowed_unformatted), '%Y-%m-%d').date()
            if date <= atmost_time_allowed:
                result['message'] = 'You can only reimbursed 60 days before the current date'
                return result
            
            result['status'] = 200
            result['year'] = date_year

            # print(result)
            return result
        except Exception as e:
            result['system_error_message'] = str(e)
            return result
        
    def emp_yearly_join_cap(self, joining_date, yearly_limit):
        try:
            result = {'status': 400, 'message': None, 'remaining_limit': yearly_limit, 'system_error_message': ''}
            month = 12 - joining_date.month + 1
            result['remaining_limit'] = round(( yearly_limit / 12 ) * month)
            return result
        except Exception as e:
            result['system_error_message'] = str(e)
            return yearly_limit

        
        
class MedicalStatusLogsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ] 
    queryset = MedicalStatusLogs.objects.all()
    serializer_class = MedicalStatusLogsSerializers

    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            pk = self.kwargs['pk']
            query = EmployeesMedicalAllowance.objects.filter(employee__organization=organization_id, id=pk)
            if not query.exists():
                return errorMessage('No employee medical allowance request exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('medical allowance request is deactivated at this id')
            
            queryset = self.queryset.filter(employee_medical_allowance=pk, is_active=True)
            serializer = self.serializer_class(queryset, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def get_all_medical_requests(self, request,*args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            month=request.data.get('month',None)
            year=request.data.get('year',None)
            query=[]
            if month is None:
                if year is None:
                    year=datetime.datetime.today().year

                month=datetime.datetime.today().month
                
                # # Calculate the first day of the specified month and year

                first_day_of_given_month = datetime.date(year, month, 1)

                # Calculate the last day of the specified month and year
                last_day_of_current_month = first_day_of_given_month.replace(
                    day=calendar.monthrange(year, month)[1]
                )

                # Calculate the last day of the previous month
                # last_day_of_previous_month = (first_day_of_given_month - datetime.timedelta(days=1)).replace(
                #     day=calendar.monthrange(year, month-1)[1]
                # )

                if month==1:
                    last_day_of_previous_month = (first_day_of_given_month - datetime.timedelta(days=1)).replace(
                        day=calendar.monthrange(year, month)[1]
                    )
                else:
                    last_day_of_previous_month = (first_day_of_given_month - datetime.timedelta(days=1)).replace(
                        day=calendar.monthrange(year, month-1)[1]
                    )

                # Calculate the first day of the previous month
                first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

                query = EmployeesMedicalAllowance.objects.filter(
                        medical_allowance__staff_classification__organization=organization_id, date__range=[first_day_of_previous_month, last_day_of_current_month],is_active=True
                    ).order_by('-id')
                

            else:

                if year is None:
                    year=datetime.datetime.today().year

                query = EmployeesMedicalAllowance.objects.filter(
                        medical_allowance__staff_classification__organization=organization_id, date__month=month,date__year=year,is_active=True
                    ).order_by('-id')
              
            
            serializer = EmployeesMedicalAllowanceSerializers(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return None
   
    def pending_medical(self, organization_id):
        try:
            current_date=datetime.datetime.today().date()
            current_month=current_date.month
            current_year=current_date.year
            query=EmployeesMedicalAllowance.objects.filter(employee__organization=organization_id,date__month=current_month,date__year=current_year,status='in-progress',is_active=True)
            # print(query.values())
            serializer =ListEmployeesPendingMedicalAllowanceSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            return exception(e)
        
    def patch(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            pk = self.kwargs['pk']
            query = EmployeesMedicalAllowance.objects.filter(employee__organization=organization_id, id=pk)
            if not query.exists():
                return errorMessage('No employee medical allowance request exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('medical allowance request is deactivated at this id')
            
            elif not query.filter(processed_status='not-processed').exists():
                return errorMessage('Stauts only update when status is not-processed')
            
            obj = query.get()
            medical_allowance=obj.medical_allowance
            current_status = obj.status

            decision_reason = request.data.get('decision_reason', None)
            if 'status' not in request.data:
                return errorMessage('status is a required field')
            
            status = request.data['status']
            obj.status = status
            obj.decision_reason = decision_reason
            amount = obj.amount

            # current_date = datetime.date.today()

            emp_remaining_allowance = EmployeesRemainingMedicalAllowance.objects.filter(
                employee=obj.employee,
                medical_allowance=medical_allowance,
                is_active=True,
            )
            
            if not emp_remaining_allowance.exists():
                return errorMessage('Employee remaining allowance does not exists. Set it first')
            
            emp_remaining_allowance = emp_remaining_allowance.get()
            remaining_allowance = emp_remaining_allowance.remaining_allowance
            in_progress = emp_remaining_allowance.inprogress_amount
            approved = emp_remaining_allowance.approved_amount
            not_approved = emp_remaining_allowance.not_approved_amount
            under_review = emp_remaining_allowance.under_review_amount
            
            status_list = ['in-progress', 'under-review', 'not-approved', 'approved']
            if status not in status_list:
                return errorMessage(f'Status can only be {status_list}')
            
            amount = obj.amount
            if current_status != status:

                if current_status == 'in-progress':
                    in_progress -= amount
                    if status == 'under-review':
                        under_review += amount
                    elif status == 'not-approved':
                        not_approved += amount
                    elif status == 'approved':
                        approved += amount
                
                elif current_status == 'under-review':
                    under_review -= amount
                    if status == 'in-progress':
                        in_progress += amount
                    elif status == 'not-approved':
                        not_approved += amount
                    elif status == 'approved':
                        approved += amount
                        

                elif current_status == 'approved':
                    approved -= amount
                    if status == 'in-progress':
                        in_progress += amount
                    elif status == 'not-approved':
                        not_approved += amount
                    elif status == 'under-review':
                        under_review += amount

                elif current_status == 'not-approved':
                    not_approved -= amount
                    if status == 'in-progress':
                        in_progress += amount
                    elif status == 'approved':
                        approved += amount
                    elif status == 'under-review':
                        under_review += amount

                if status == 'approved':
                    remaining_allowance -= amount
                elif current_status == 'approved':
                    remaining_allowance += amount

                if remaining_allowance < 0:
                    return errorMessage('Employee remaining allowance is exhausted')

                emp_remaining_allowance.remaining_allowance = remaining_allowance
                emp_remaining_allowance.inprogress_amount = in_progress
                emp_remaining_allowance.approved_amount = approved
                emp_remaining_allowance.not_approved_amount = not_approved
                emp_remaining_allowance.under_review_amount = under_review

            medical_status_dict = {
                'employee_medical_allowance': pk,
                'status': status,
                'action_by': request.user.id,
                'action_on': datetime.date.today(), 
                'decision_reason': decision_reason,
            }

            serializer = self.serializer_class(data = medical_status_dict)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            obj.save()
            emp_remaining_allowance.save()
            requestDecisionFromManagement(obj.employee.name,'Medical Status Update','Medical',status,decision_reason, obj.employee.official_email)
            return successMessageWithData('Successfully updated', serializer.data)
        except Exception as e:
            return exception(e)
        
    def update_medical_stauts(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            # pk = self.kwargs['pk']
            decision_reason = request.data.get('decision_reason', None)
            if 'status' not in request.data:
                return errorMessage('status is a required field')
            
            status = request.data['status']
            
            status_list = ['in-progress', 'under-review', 'not-approved', 'approved']
            if status not in status_list:
                    return errorMessage(f'Status can only be {status_list}')
            
            if 'medical_array' not in request.data:
                return errorMessage('Medical array is required')
            
            medical_array=request.data['medical_array']
            count=0
            status_error=[]
            error_list=[]

            for pk in medical_array:

                query = EmployeesMedicalAllowance.objects.filter(employee__organization=organization_id, id=pk)
                if not query.exists():
                    error_list.append(pk)
                    continue
                elif not query.filter(is_active=True):
                    error_list.append(pk)
                    continue
                
                elif not query.filter(processed_status='not-processed').exists():
                    # return errorMessage('Stauts only update when status is not-processed')
                    status_error.append(pk)
                    continue
                
                obj = query.get()
                medical_allowance=obj.medical_allowance
                current_status = obj.status

                
                
                
                obj.status = status
                obj.decision_reason = decision_reason
                amount = obj.amount

                # current_date = datetime.date.today()

                emp_remaining_allowance = EmployeesRemainingMedicalAllowance.objects.filter(
                    employee=obj.employee,
                    medical_allowance=medical_allowance,
                    is_active=True,
                )
                
                if not emp_remaining_allowance.exists():
                    error_list.append(pk)
                    continue
                
                emp_remaining_allowance = emp_remaining_allowance.get()
                remaining_allowance = emp_remaining_allowance.remaining_allowance
                in_progress = emp_remaining_allowance.inprogress_amount
                approved = emp_remaining_allowance.approved_amount
                not_approved = emp_remaining_allowance.not_approved_amount
                under_review = emp_remaining_allowance.under_review_amount
                
                
                
                amount = obj.amount
                if current_status != status:

                    if current_status == 'in-progress':
                        in_progress -= amount
                        if status == 'under-review':
                            under_review += amount
                        elif status == 'not-approved':
                            not_approved += amount
                        elif status == 'approved':
                            approved += amount
                    
                    elif current_status == 'under-review':
                        under_review -= amount
                        if status == 'in-progress':
                            in_progress += amount
                        elif status == 'not-approved':
                            not_approved += amount
                        elif status == 'approved':
                            approved += amount
                            

                    elif current_status == 'approved':
                        approved -= amount
                        if status == 'in-progress':
                            in_progress += amount
                        elif status == 'not-approved':
                            not_approved += amount
                        elif status == 'under-review':
                            under_review += amount

                    elif current_status == 'not-approved':
                        not_approved -= amount
                        if status == 'in-progress':
                            in_progress += amount
                        elif status == 'approved':
                            approved += amount
                        elif status == 'under-review':
                            under_review += amount

                    if status == 'approved':
                        remaining_allowance -= amount
                    elif current_status == 'approved':
                        remaining_allowance += amount

                    if remaining_allowance < 0:
                        error_list.append(pk)
                        continue

                    emp_remaining_allowance.remaining_allowance = remaining_allowance
                    emp_remaining_allowance.inprogress_amount = in_progress
                    emp_remaining_allowance.approved_amount = approved
                    emp_remaining_allowance.not_approved_amount = not_approved
                    emp_remaining_allowance.under_review_amount = under_review

                medical_status_dict = {
                    'employee_medical_allowance': pk,
                    'status': status,
                    'action_by': request.user.id,
                    'action_on': datetime.date.today(), 
                    'decision_reason': decision_reason,
                }

                serializer = self.serializer_class(data = medical_status_dict)
                if not serializer.is_valid():
                    error_list.append(pk)
                    continue
                serializer.save()
                obj.save()
                emp_remaining_allowance.save()
                requestDecisionFromManagement(obj.employee.name,'Medical Status Update','Medical',status,decision_reason, obj.employee.official_email)
                count +=1

            data = {
                    'error_list': error_list, 
                    'status_error': status_error,
                }
            
            if count == len(medical_array):
                return successMessage('All medical status is changed successfuly')
            elif count == 0:
                return errorMessageWithData('Failed to change medical status', data) 
            elif count > 0:
                return successMessageWithData('Some of the data is processed successfully', data)
            
        except Exception as e:
            return exception(e)


class EmployeesRemainingMedicalAllowanceViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ] 
    queryset = EmployeesRemainingMedicalAllowance.objects.all()
    serializer_class = EmployeesRemainingMedicalAllowanceSerializers

    def get(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']

            current_year = datetime.date.today().year
            
            query = self.queryset.filter(
                employee__organization=organization_id,
                date__year = current_year,    
            )
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def sync_data(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            year=request.data.get('year',None)

            if year is None:
                year=datetime.datetime.today().year


            current_date = datetime.date.today()
            employees = Employees.objects.filter(organization=organization_id, is_active=True)
            missed_staff_classification = []
            missed_joining_date = []
            medical_allowance_does_not_exists = []
            serializer_errors = []
            emp_data = []

            for emp in employees:
                if not emp.staff_classification:
                    missed_staff_classification.append(emp.id)
                    continue
                joining_date = emp.joining_date
                if not joining_date:
                    missed_joining_date.append(emp.id)
                    continue

                medical = MedicalAllowance.objects.filter(
                        staff_classification=emp.staff_classification,
                        year=year,
                        is_active=True
                    )
                if not medical.exists():
                        medical_allowance_does_not_exists.append(emp.id)
                        continue
                # print(medical.values())
                medical_obj = medical.get()
                query = self.queryset.filter(employee=emp.id,medical_allowance=medical_obj, is_active=True) 
                if not query.exists():
                    
                    result = self.emp_yearly_join_cap(joining_date, medical_obj.yearly_limit,year)
                    emp_yearly_limit = result['yearly_limit']

                    yearly_limit_dict = {
                        'employee': emp.id,
                        'remaining_allowance': emp_yearly_limit,
                        'medical_allowance': medical_obj.id,
                        'emp_yearly_limit': emp_yearly_limit,
                        'date': current_date,
                    }
                    serializer = self.serializer_class(data=yearly_limit_dict)
                    if not serializer.is_valid():
                        serializer_errors.append(serializer.errors)
                    serializer.save()
                    emp_data.append(serializer.data)
                    
                # else:
                #     query = self.queryset.filter(
                #         employee=emp.id, 
                #         medical_allowance=medical_obj,
                #         is_active=True
                #     )

                #     if not query.exists():
                #         continue
                #     obj = query.first()
                    
                #     emp_medical_allowance = EmployeesMedicalAllowance.objects.filter(
                #         employee=emp.id, 
                #         is_active=True
                #     )
                #     if not emp_medical_allowance.exists():
                #         medical_allowance_does_not_exists.append(emp.id)
                #         continue

                #     emp_in_progress = emp_medical_allowance.filter(status='in-progress')
                #     emp_under_review = emp_medical_allowance.filter(status='under-review')
                #     emp_approved = emp_medical_allowance.filter(status='approved')
                #     emp_not_approved = emp_medical_allowance.filter(status='not-approved')

                #     in_progress_amount = 0
                #     approved_amount = 0
                #     under_review_amount = 0
                #     not_approved_amount = 0
                #     if emp_in_progress.exists():
                #         for employee in emp_in_progress:
                #             in_progress_amount += employee.amount

                #     if emp_under_review.exists():
                #         for employee in emp_under_review:
                #             under_review_amount += employee.amount

                #     if emp_approved.exists():
                #         for employee in emp_approved:
                #             approved_amount += employee.amount

                #     if emp_not_approved.exists():
                #         for employee in emp_not_approved:
                #             not_approved_amount += employee.amount

                #     remaining_amount = int(obj.emp_yearly_limit) - int(approved_amount or 0)
                #     remaining_amount_data = {
                #         'remaining_allowance': remaining_amount,
                #         'inprogress_amount': in_progress_amount,
                #         'under_review_amount': under_review_amount,
                #         'not_approved_amount': not_approved_amount,
                #         'approved_amount': approved_amount,
                #     }

                #     serializer = self.serializer_class(obj, data = remaining_amount_data, partial=True)
                #     if not serializer.is_valid():
                #         serializer_errors.append(serializer.errors)
                #     serializer.save()
                #     emp_data.append(serializer.data)


            data = {
                'missed_sc': missed_staff_classification,
                'missed_jd': missed_joining_date,
                'missed_medical_allowance': medical_allowance_does_not_exists,
                'serializer_error': serializer_errors,
                'remaining_allowance': emp_data,
            }
            return successMessageWithData('Success', data)

        except Exception as e:
            return exception(e)
        

    def emp_yearly_join_cap(self, joining_date, yearly_limit,year):
        try:
            result = {'status': 400, 'message': None, 'yearly_limit': yearly_limit, 'system_error_message': ''}
            if joining_date.year == year:
                month = 12 - joining_date.month + 1
                result['yearly_limit'] = round(( yearly_limit / 12 ) * month)
            else:
                result['yearly_limit'] = yearly_limit
            return result
        except Exception as e:
            result['system_error_message'] = str(e)
            return yearly_limit

class NewEmployeeMedicalAllowanceViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsAdminOnly]  

    def allow_emp_medical(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)

            organization_id = token_data['organization_id']
            pk=self.kwargs['pk']

            year=request.data.get('year',None)
            if year is None:
               year=datetime.datetime.today().year

            # current_year = datetime.date.today().year
            current_date = datetime.date.today()
            total_amount=0
            med_allowance=None

            employee=Employees.objects.filter(id=pk,organization_id=organization_id,is_active=True)

            if not employee.exists():
                return errorMessage("Employee not exists at this id")
            emp=employee.get()



            if emp.staff_classification is not None:
                    # print(emp.id)
                    # print(emp.staff_classification_id)
               
                    med_all=MedicalAllowance.objects.filter(staff_classification=emp.staff_classification,year=year,is_active=True)
                    if med_all.exists():
                        yearly_limit = med_all.first().yearly_limit
                        # print(f"Yearly Limit: {yearly_limit}")
                        medical_emp_yearly_limit = 0
                        if emp.joining_date:
                            joining_year = emp.joining_date.year
                            if joining_year < year:
                                medical_emp_yearly_limit = yearly_limit
                            else:
                                joining_month = emp.joining_date.month - 1
                                # Calculate remaining months in the year
                                remaining_months = 12 - joining_month
                                
                                count=round(yearly_limit/12 * remaining_months)
                                medical_emp_yearly_limit = count
                        else:
                            return errorMessage('Joining Data is missing')

                        if medical_emp_yearly_limit<0:
                            medical_emp_yearly_limit=0

                        medical_allowance_id=med_all.get()

                        med_count = EmployeesRemainingMedicalAllowance.objects.filter(medical_allowance=medical_allowance_id,employee=emp.id, is_active=True)
                        if not med_count.exists():
                            med_allowance=EmployeesRemainingMedicalAllowance.objects.create(
                                medical_allowance=medical_allowance_id,
                                employee=emp,
                                remaining_allowance=medical_emp_yearly_limit,
                                emp_yearly_limit=medical_emp_yearly_limit,
                                date=current_date 
                                )
                            approved_ammount_count=EmployeesMedicalAllowance.objects.filter(employee=emp.id,date__year=year,status='approved',is_active=True)
                            
                            for obj in approved_ammount_count:
                                total_amount+=obj.amount
                            # med_count = EmployeesRemainingMedicalAllowance.objects.get(medical_allowance=medical_allowance_id,employee=emp.id, is_active=True)
                            med_allowance.remaining_allowance = max(med_allowance.remaining_allowance - total_amount, 0)
                            med_allowance.save()    
                            
                        user_id=request.user.id
                        script_title="Medical Script"
                        script_type=3
                        status=1
                        staff_classification=emp.staff_classification.id

                        output = script_logs(pk,staff_classification,script_title,script_type,year,status,user_id)
                        # print(output)
                        if output['status'] == 400:
                                return errorMessage(output['message'])

                        return successMessageWithData('success',output['data'])
                        
                        
                        
                    else:
                        return errorMessage('Medical data not exists againts staff_classification_id ')

             
            else:
                    return errorMessage('staff_classification_id is missing')

        except Exception as e:
            return exception(e)


    

    def NewEmployeeMedicalSet(self, request, *args, **kwargs):
        try:
            result = {
                'status': 400, 
                'message': '', 
                'data': None,
                'system_error_message': '',
            }

            not_found_data=[]
            # print('in script start')
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            year=request.data.get('year',None)
            if year is None:
                year=datetime.datetime.today().year
            current_date = datetime.date.today()
            employee=Employees.objects.filter(organization_id=organization_id,is_active=True)

            for emp in employee:
                if emp.staff_classification_id is not None:
                    # print(emp.id)
                    # print(emp.staff_classification_id)
               
                    med_all=MedicalAllowance.objects.filter(staff_classification=emp.staff_classification_id,year=year,is_active=True)
                    if med_all.exists():
                        yearly_limit = med_all.first().yearly_limit
                        # print(f"Yearly Limit: {yearly_limit}")
                        medical_emp_yearly_limit = 0
                        if emp.joining_date:
                            joining_year = emp.joining_date.year
                            if joining_year < year:
                                medical_emp_yearly_limit = yearly_limit
                            else:
                                joining_month = emp.joining_date.month - 1
                                # Calculate remaining months in the year
                                remaining_months = 12 - joining_month
                                
                                count=round(yearly_limit/12 * remaining_months)
                                medical_emp_yearly_limit = count
                        else:
                            not_found_data.append([emp.id,emp.name,"Joining date is missing"])
                            continue

                        if medical_emp_yearly_limit<0:
                            medical_emp_yearly_limit=0

                        medical_allowance_id=med_all.get()

                        med_count = EmployeesRemainingMedicalAllowance.objects.filter(medical_allowance=medical_allowance_id,employee=emp.id, is_active=True)
                        if not med_count.exists():
                            EmployeesRemainingMedicalAllowance.objects.create(
                                medical_allowance=medical_allowance_id,
                                employee=emp,
                                remaining_allowance=medical_emp_yearly_limit,
                                emp_yearly_limit=medical_emp_yearly_limit,
                                date=current_date 
                                )
                        else:
                            # print(med_count.values())
                            instance_to_update = med_count.first()
                            if emp.joining_date:
                                joining_year = emp.joining_date.year
                                
                                # print(emp.joining_date)
                                if joining_year < year:
                                    emp_yearly_medical_count=yearly_limit
                                   

                        
                                else:
                                    joining_month = emp.joining_date.month - 1
                                    # Calculate remaining months in the year
                                    remaining_months = 12 - joining_month
                                    
                                    count=round(yearly_limit/12 * remaining_months)
                                    # print(count)
                                    emp_yearly_medical_count=count
                                  

                                approved_amount = instance_to_update.approved_amount
                                new_remaining_medical_count=emp_yearly_medical_count-approved_amount
                                # print(approved_leaves)
                                
                                # print(leave_type_title)
                               
                                # print(leave_type_title)
                                if new_remaining_medical_count<0:
                                    not_found_data.append([emp.id,emp.name,'Employee have negative medical balance'])
                                    # continue
                                
                                instance_to_update.remaining_allowance=new_remaining_medical_count
                                instance_to_update.emp_yearly_limit=emp_yearly_medical_count
                                instance_to_update.save()

                    else:
                        not_found_data.append([emp.id,emp.name,"staff_classification_id is not exists"])
                        continue
             
                else:
                    not_found_data.append([emp.id,emp.name,"staff_classification_id is missing"])
                    continue
           
            print('employee process completed')
            
            if not_found_data:
                directory_path = 'C:\\Users\\Kavtech\\Downloads'
                file_name = 'employees_not_found_medical.csv'
                file_path = os.path.join(directory_path, file_name)
                # Create the directory if it doesn't exist
                if not os.path.exists(directory_path):
                    os.makedirs(directory_path)
                not_found_df = pd.DataFrame(not_found_data, columns=['Emp_id','Emp_Name', 'Message'])
                not_found_df.to_csv(file_path, index=False)
           
            result['status'] = 200
            result['message'] = 'Success'
            return successMessage('success')
            

        except Exception as e:
            result['message'] = e
            return errorMessage(e)


class PreviousMedicalDataScriptsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ] 
    queryset = EmployeesMedicalAllowance.objects.all()
    serializer_class = EmployeesMedicalAllowanceSerializers

    def donwload_medical_approved_files(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            month=request.data.get('month',None)
            year=request.data.get('year',None)

            if month is None and year is None:
               return errorMessage("Month and year is missing")

            query = EmployeesMedicalAllowance.objects.filter(date__year=year,employee__organization=organization_id,is_active=True)
            if not query.exists():
                return errorMessage("No data found")

           # Get the name of the month
            month_name = calendar.month_name[int(month)]

            # Create a folder to store downloaded files if it doesn't exist
            folder_name=f"medical_reciept"
           # Specify the folder path on your local machine
            download_folder_name = os.path.join('Downloads', 'medical_files', folder_name)
            download_folder_path = os.path.join(os.path.expanduser('~'), download_folder_name)
            os.makedirs(download_folder_path, exist_ok=True)

            # Initialize boto3 client for DigitalOcean Spaces
            session = boto3.session.Session()
            s3_client = session.client(
                's3',
                region_name=settings.AWS_S3_REGION_NAME,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            total_amount = 0
            for obj in query:
                file_key = obj.medical_receipt.name
                if file_key:
                    file_name = os.path.basename(file_key)
                    file_path = os.path.join(download_folder_path, file_name)
                    with open(file_path, 'wb') as f:
                        s3_client.download_fileobj(settings.AWS_STORAGE_BUCKET_NAME, file_key, f)
                    total_amount += obj.amount

            # Create a text file containing the total amount
            file=f"total_amount.txt"
            total_file_path = os.path.join(download_folder_path, file)
            with open(total_file_path, 'w') as total_file:
             total_file.write(f"Total Medical Amount: {total_amount}")

            return success({"message": f"Files downloaded to {download_folder_path}", "total_amount": total_amount})

        except Exception as e:
            return exception (e)

    
    def download_images(self, request, *args, **kwargs):
        # Set your DigitalOcean Space access key and secret key
        ACCESS_KEY = 'DO00RMBJ96L6G7RER2HW'
        SECRET_KEY = 'QhyXmTyIk+4nNTMVTxf0abch1EpFV7PH9TvDGIAn5EE'

        # Set the name of your DigitalOcean Space and the folder where images are located
        SPACE_NAME = 'universal-hrms-live'
        FOLDER_NAME = 'organization/medical/'

        # Set the local directory where you want to save downloaded images
        LOCAL_DIRECTORY = 'C:\\Users\\Kavtech\\Downloads\\medical'

        # Connect to DigitalOcean Space
        session = boto3.session.Session()
        client = session.client('s3',
                                region_name='sgp1',
                                endpoint_url='https://sgp1.digitaloceanspaces.com',
                                aws_access_key_id=ACCESS_KEY,
                                aws_secret_access_key=SECRET_KEY)

        # List objects in the specified folder
        response = client.list_objects_v2(Bucket=SPACE_NAME, Prefix=FOLDER_NAME)

        if 'Contents' in response:
            # Download each object (image) in the folder
            for obj in response['Contents']:
                key = obj['Key']
                file_name = os.path.basename(key)
                local_file_path = os.path.join(LOCAL_DIRECTORY, file_name)
                client.download_file(SPACE_NAME, key, local_file_path)

            return success("Done")
        else:
            return success("No images found in the specified folder.")



    
    
    
    def create(self, request, *args, **kwargs):
        try:
            # print('hellow')
            organization_id = decodeToken(self, self.request)['organization_id']

            file_name = 'medical-previous-record.csv'
            file_path = os.path.join('static/import/ess/', file_name)

            employees_query = Employees.objects.filter(organization=organization_id)

            query = self.queryset.filter(employee__organization=organization_id, is_active=True)

            with open(file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                i = 0

                # This will store all the columns values csv file
                result = []
                columns = []
                for rows in reader: 
                    if i == 0:
                        for j in range(len(rows)):
                            columns.append(rows[j])
                        break     

                for rows in reader:
                    for j in range(len(rows)):
                        if j==1 and j==3:
                            continue

                        if columns[j] == 'emp_code':
                            emp_code = rows[j]
                            print(rows[j])
                            if not emp_code:
                                print('emp_code does not exists')
                                break
                            emp_code = int(emp_code)
                            emp = employees_query.filter(emp_code=emp_code)
                            if not emp.exists():
                                print('emp does not exists')
                                break
                            emp_obj = emp.get()
                            
                            if not emp_obj.staff_classification:
                                print('employee staff classification is not added yet')
                                break
                            
                            print(emp_obj.staff_classification)
                            medical_allowance = MedicalAllowance.objects.filter(
                                staff_classification=emp_obj.staff_classification,
                                staff_classification__organization=organization_id, 
                                is_active=True
                            )
                            if not medical_allowance.exists():
                                print('medical_allowance is not set')
                                break
                                
            
                            medical_allowance_obj = medical_allowance.get()
                            
                            medical_allowance_id = medical_allowance_obj.id
                        
                        if columns[j] == 'date':
                            date_value = rows[j]
                            date = datetime.datetime.strptime(date_value, "%m/%d/%Y").date()
                            month = date.month
                            year = date.year
                            if query.filter(employee__emp_code=rows[0], amount=rows[1], date__month=month, date__year=year).exists():
                                print(emp_obj.name)
                                print('already exists')
                                break
                            
                            if month > 4:
                                rows[3] = 'under-review'

                            medical_data = {
                                'employee': emp_obj.id,
                                'medical_allowance': medical_allowance_id,
                                'amount': rows[1],
                                'date': date,
                                'status': rows[3],
                                'is_active': True,
                            }
                            result.append(medical_data)
                            serializer = self.serializer_class(data=medical_data)
                            if not serializer.is_valid():
                                print(serializer.errors)
                                continue
                            
                            serializer.save()
                            print('success')
                            break


                
                            
            return successMessageWithData('successfully read', result)

                                
        except Exception as e:
            return exception(e)   
        

