from rest_framework import viewsets

from email_templates.models import EmailRecipients
from .serializers import (
    GymAllowanceSerializers, ListEmployeesPendingGymAllowanceSerializers, UpdateGymAllowanceSerializers, EmployeesGymAllowanceSerializers, 
    UpdateEmployeesGymAllowanceSerializers, GymStatusLogsSerializers
)
from .models import GymAllowance, EmployeesGymAllowance, GymStatusLogs
from helpers.status_messages import (
    errorMessageWithData, exception, errorMessage, success, successMessage, successfullyCreated,
    successfullyUpdated, serializerError, successMessageWithData
)
from helpers.decode_token import decodeToken
from helpers.email_data import requestEmailsFromEmployees, requestDecisionFromManagement, requestEmailsFromEmployeesnontl
from helpers.custom_permissions import IsAuthenticated, IsEmployeeOnly
from organizations.models import StaffClassification
from employees.models import Employees
import datetime
import csv
import os
import calendar
from django.db.models import Q

class GymAllowanceViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = GymAllowance.objects.all()
    serializer_class = GymAllowanceSerializers

    def get_queryset(self):
        organization_id = decodeToken(self, self.request)['organization_id']
        return self.queryset.filter(staff_classification__organization=organization_id)

    def list(self, request, *args, **kwargs):
        try:
            obj = self.get_queryset().filter(is_active=True)
            serializer = self.serializer_class(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            
            if not request.user.is_privileged:
                return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            staff_classification_id = request.data.get('staff_classification', None)
            if not staff_classification_id:
                return errorMessage('Staff classification is the required field')
            
            staff_classification = StaffClassification.objects.filter(id=staff_classification_id, organization=organization_id)
            if not staff_classification.exists():
                return errorMessage("Staff classification does not exists")
            elif not staff_classification.filter(is_active=True).exists():
                return errorMessage("staff classification is deactivated")
            request.data['staff_classification'] = staff_classification_id

            query = self.get_queryset().filter(staff_classification=staff_classification_id, is_active=True)
            if query.exists():
                return errorMessage("Already value exists against this staff_classification")

            monthly_limit = request.data.get('monthly_limit', None)
            if not monthly_limit:
                return errorMessage('Monthly limit is the required field')
            serializer = self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)
        
    
    def patch(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            gym_allowance = self.get_queryset().filter(id=pk)
            if not gym_allowance.exists():
                return errorMessage('No gym allowance exists at this id')

            obj = gym_allowance.get()
            serializer = UpdateGymAllowanceSerializers(obj, data=request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)
        

    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']

            gym_allowance = self.get_queryset().filter(id=pk)
            if not gym_allowance.exists():
                return errorMessage('No gym allowance exists at this uuid')
            if not gym_allowance.filter(is_active=True):
                return errorMessage('Gym allowance is deactivated at this id')
            obj = gym_allowance.get()

            obj.is_active = False
            obj.save()
            return successMessage('Sucessfully deactivated')
        except Exception as e:
            return exception(e)
        
    def get_pre_data(self, organization_id):
        try:
            query = GymAllowance.objects.filter(staff_classification__organization=organization_id, is_active=True).order_by('-id')
            serializer = GymAllowanceSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            return None
        

class EmployeesGymAllowanceViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsEmployeeOnly]
    queryset = EmployeesGymAllowance.objects.all()
    serializer_class = EmployeesGymAllowanceSerializers

    def get_queryset(self):
        token_data = decodeToken(self, self.request)
        organization_id = token_data['organization_id']
        employee_id = token_data['employee_id']
        return self.queryset.filter(employee=employee_id, employee__organization=organization_id)

    def list(self, request, *args, **kwargs):
        try:
            obj = self.get_queryset().filter(is_active=True).order_by('-id')
            serializer = self.serializer_class(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def retrieve(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            query = self.get_queryset().filter(id=pk, is_active=True)
            if not query.exists():
                return errorMessage('No employee gym allowance exists at this id')
            obj = query.get()
            serializer = self.serializer_class(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employees = Employees.objects.filter(hrmsuser=request.user.id)
            emp = employees.get()
            if not emp.staff_classification:
                return errorMessage("Add staff classification of the employee first")
            elif not emp.employee_type:
                return errorMessage("Employee type is a required field")
            elif not emp.employee_type.title == 'Permanent':
                return errorMessage('Only Permanent Employees is elligible for gym allowance')
            
            required_fields = ['amount', 'gym_receipt']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [amount, date, gym_receipt]')
            
            request.data_mutable = True
            request.data['employee'] = emp.id
            request.data['is_active'] = True
            
            current_date=datetime.datetime.today().date()
            if current_date.day>20:
                return errorMessage("Cannot apply for gym after the 20th.")
            date_str = current_date

            valid_time_duration_check = self.check_reimbursement_time_duration(date_str, pk=None)
            if valid_time_duration_check['status'] == 400:
                return errorMessage(valid_time_duration_check['message'])
            
            request.data['date']=date_str

            gym_allowance = GymAllowance.objects.filter(staff_classification=emp.staff_classification, staff_classification__organization=emp.organization, is_active=True)
            if not gym_allowance.exists():
                return errorMessage("No gym allowance exists against this staff classification")    
            
            gym_allowance_obj = gym_allowance.get()
            request.data['gym_allowance'] = gym_allowance_obj.id
            amount = request.data['amount']
            if int(amount) > gym_allowance_obj.monthly_limit:
                return errorMessage('Gym allowance cannot be greater than the limit')

            serializer = self.serializer_class(data = request.data)
            if not serializer.is_valid():
                if serializer.errors.get('gym_receipt'):
                    return errorMessage(serializer.errors.get('gym_receipt', [''])[0])
                   
                return serializerError(serializer.errors)
            serializer.save()

            cc_employee=EmailRecipients.objects.filter(employee__organization=organization_id,level=2,is_active=True)
            if cc_employee.exists():
                eobj=cc_employee.get()
                requestEmailsFromEmployeesnontl(emp.name,'Gym Application Received',"Gym",eobj.employee.official_email,eobj.employee.name)

            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)    
        
    def patch(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('This employee has no gym allowance at this id')
            obj = query.get()
            
            if request.data:
                request.data_mutable = True
            if 'date' in request.data:
                date_str = request.data['date']
                valid_time_duration_check = self.check_reimbursement_time_duration(date_str, pk=pk)
                if valid_time_duration_check['status'] == 400:
                    return errorMessage(valid_time_duration_check['message'])

            serializer = UpdateEmployeesGymAllowanceSerializers(obj, data = request.data, partial=True)
            if not serializer.is_valid():
                if serializer.errors.get('gym_receipt'):
                    return errorMessage(serializer.errors.get('gym_receipt', [''])[0])
                   
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
            obj.is_active = False
            obj.save()
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

            query = EmployeesGymAllowance.objects.filter(employee=employee_id, employee__organization=organization_id,date__year=year, is_active=True)
            serializer = EmployeesGymAllowanceSerializers(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return None  

    def check_reimbursement_time_duration(self, date_str, pk):
        try:
            result = {'status': 400, 'message': None, 'system_error_message': ''}
            # date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            date=date_str
            date_month = date.month
            atmost_time_allowed_unformatted = datetime.date.today() - datetime.timedelta(days=60)
            atmost_time_allowed = datetime.datetime.strptime(str(atmost_time_allowed_unformatted), '%Y-%m-%d').date()
            if date <= atmost_time_allowed:
                result['message'] = 'You can only be reimbursed for expenses incurred within the last 60 days'
                return result
            
            if pk:
                    query = self.get_queryset().exclude(id=pk).filter(
                        Q(date__month=date_month) &
                        Q(date__year=date.year) &
                        Q(is_active=True) &
                        ~Q(status='not-approved')
                    )
            else:
                query = self.get_queryset().filter(
                 Q(date__month=date_month) &
                 Q(date__year=date.year) &
                 Q(is_active=True) &
                 ~Q(status='not-approved')
                )
            
            if query.exists():
                result['message'] = 'The gym reimbursement form for this month has already been filled'
                return result
            
            result['status'] = 200
            return result
        except Exception as e:
            result['system_error_message'] = str(e)
            return result



class GymStatusLogsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ] 
    queryset = GymStatusLogs.objects.all()
    serializer_class = GymStatusLogsSerializers

    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            pk = self.kwargs['pk']
            query = EmployeesGymAllowance.objects.filter(employee__organization=organization_id, id=pk)
            if not query.exists():
                return errorMessage('No employee gym allowance request exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('Gym allowance request is deactivated at this id')
            
            queryset = self.queryset.filter(employee_gym_allowance=pk, is_active=True)
            serializer = self.serializer_class(queryset, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    
    def get_all_gym_requests(self, request,*args, **kwargs):
        try:  
            organization_id = decodeToken(self, self.request)['organization_id']
            month=request.data.get('month',None)
            year=request.data.get('year',None)

            employee=request.data.get('employee',None)
            
            if employee is not None:

                employee_query = Employees.objects.filter(
                        id=employee, 
                        organization=organization_id, 
                        is_active=True
                    )
                if not employee_query.exists():
                        return errorMessage('Employee does not exists at this id')
            
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
                # current_date = datetime.datetime.today().date()
                # # print(current_date)
                # first_day_of_current_month = current_date.replace(day=1)
                # last_day_of_current_month = first_day_of_current_month.replace(
                #     day=28
                # ) + datetime.timedelta(days=4)  # Just to handle edge cases at the end of the month
                
                # last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
                # first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
               
                query = EmployeesGymAllowance.objects.filter(
                    gym_allowance__staff_classification__organization=organization_id,date__range=[first_day_of_previous_month, last_day_of_current_month], is_active=True
                    ).order_by('-id')
                # print(query.values())
                
                 
            else:

                if year is None:
                    year=datetime.datetime.today().year
                
                query = EmployeesGymAllowance.objects.filter(
                    gym_allowance__staff_classification__organization=organization_id,date__month=month,date__year=year, is_active=True
                    ).order_by('-id')
                
            if employee is not None:
                query=query.filter(employee=employee)
            # print(query.values())
            serializer = EmployeesGymAllowanceSerializers(query, many=True)
            return success(serializer.data)
            
            
        except Exception as e:
            return exception(e)

    def pending_gym(self, organization_id):
        try:
            current_date=datetime.datetime.today().date()
            current_month=current_date.month
            current_year=current_date.year
            query=EmployeesGymAllowance.objects.filter(employee__organization=organization_id,date__month=current_month,date__year=current_year,status='in-progress',is_active=True)
            # print(query.values())
            serializer =ListEmployeesPendingGymAllowanceSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            return exception(e)
        
    def patch(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            pk = self.kwargs['pk']
            query = EmployeesGymAllowance.objects.filter(employee__organization=organization_id, id=pk)
            if not query.exists():
                return errorMessage('No employee gym allowance request exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('Gym allowance request is deactivated at this id')
            
            obj = query.get()
            decision_reason = request.data.get('decision_reason', None)
            if 'status' not in request.data:
                return errorMessage('status is a required field')
            
            status = request.data['status']
            obj.status = status
            obj.decision_reason = decision_reason
            obj.save()
            
            status_list = ['in-progress', 'under-review', 'not-approved', 'approved']
            if status not in status_list:
                return errorMessage(f'Status can only be {status_list}')
            
            status_dict = {
                'employee_gym_allowance': pk,
                'status': status,
                'action_by': request.user.id,
                'action_on': datetime.date.today(), 
                'decision_reason': decision_reason,
            }

            serializer = self.serializer_class(data = status_dict)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            requestDecisionFromManagement(obj.employee.name,'Gym Status Update','Gym',status,decision_reason, obj.employee.official_email)
            return successMessageWithData('Successfully updated', serializer.data)
        except Exception as e:
            return exception(e)

    def update_gym_status(self, request, *args, **kwargs):
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
            
            if 'gym_array' not in request.data:
                return errorMessage('Gym array is required')
            
            gym_array=request.data['gym_array']
            count=0
            status_error=[]
            error_list=[]

            for pk in gym_array:

                query = EmployeesGymAllowance.objects.filter(employee__organization=organization_id, id=pk)
                if not query.exists():
                    error_list.append(pk)
                    continue
                elif not query.filter(is_active=True):
                    error_list.append(pk)
                    continue
                
                obj = query.get()
                
                obj.status = status
                obj.decision_reason = decision_reason
                obj.save()
                
                
                
                status_dict = {
                    'employee_gym_allowance': pk,
                    'status': status,
                    'action_by': request.user.id,
                    'action_on': datetime.date.today(), 
                    'decision_reason': decision_reason,
                }

                serializer = self.serializer_class(data = status_dict)
                if not serializer.is_valid():
                    error_list.append(pk)
                    continue
                serializer.save()
                requestDecisionFromManagement(obj.employee.name,'Gym Status Update','Gym',status, obj.employee.official_email)
                count+=1
            
            data = {
                    'error_list': error_list, 
                }

            if count == len(gym_array):
                return successMessage('All medical status is changed successfuly')
            elif count == 0:
                return errorMessageWithData('Failed to change medical status', data) 
            elif count > 0:
                return successMessageWithData('Some of the data is processed successfully', data)

        except Exception as e:
            return exception(e)



class PreviousGymDataScriptsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ] 
    queryset = EmployeesGymAllowance.objects.all()
    serializer_class = EmployeesGymAllowanceSerializers

    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            query = EmployeesGymAllowance.objects.filter(employee__organization=organization_id, is_active=True)               
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']

            file_name = 'gym-previous-record.csv'
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
                    print('row')
                    # traverse all the columns in the csv file
                    for j in range(len(rows)):
                        # checks if emp_code exists or not
                        if j == 1 or j==2 or j==4:
                            continue
                        
                        if columns[j] == 'emp_code':
                            emp_code = rows[j]
                            if not emp_code:
                                print('emp_code does not exists')
                                break
                            emp_code = int(emp_code)
                            emp = employees_query.filter(emp_code=emp_code, organization=organization_id)
                            if not emp.exists():
                                print('emp does not exists')
                                break
                            emp_obj = emp.get()
                            
                            if not emp_obj.staff_classification:
                                print('employee staff classification is not added yet')
                                break

                            gym_allowance = GymAllowance.objects.filter(
                                staff_classification=emp_obj.staff_classification,
                                staff_classification__organization=organization_id, 
                                is_active=True
                            )
                            if not gym_allowance.exists():
                                print('gym_allowance is not set')
                                break
                             
            
                            gym_allowance_obj = gym_allowance.get()
                            
                            gym_allowance_id = gym_allowance_obj.id
                        
                        if columns[j] == 'date':
                            date_value = rows[j]
                            date = datetime.datetime.strptime(date_value, "%m/%d/%Y").date()
                            month = date.month
                            year = date.year
                            if query.filter(employee__emp_code=rows[0], date__month=month, date__year=year).exists():
                                print('already exists')
                                continue
                            
                            
                            gym_data = {
                                'employee': emp_obj.id,
                                'gym_allowance': gym_allowance_id,
                                'amount': rows[2],
                                'date': date,
                                'status': rows[4],
                                'is_active': True,
                            }
                            result.append(gym_data)
                            serializer = self.serializer_class(data=gym_data)
                            if not serializer.is_valid():
                                print(serializer.errors)
                                continue
                            serializer.save()
                            print('success')
                            break
                    
                            
            return successMessageWithData('successfully read', result)

                                
                
            
        except Exception as e:
            return exception(e)   
        

