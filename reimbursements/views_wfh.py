from datetime import datetime
from logging import exception
from rest_framework import viewsets

from employees.models import Employees
from helpers.custom_permissions import IsAuthenticated
from helpers.decode_token import decodeToken
from helpers.status_messages import errorMessage, errorMessageWithData, serializerError, success, successMessage, successfullyCreated
from reimbursements.models import EmployeesWFHAllowance, EmployeesWFHRequest, EmployeesWFHRequestDates
from reimbursements.serializers import EmployeeWFHAllowanceSerializer, EmployeesWFHRequestDatesSerializers, EmployeesWFHRequestSerializer




class EmployeeWFHAllowanceviewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EmployeesWFHAllowance.objects.all()
    serializer_class = EmployeeWFHAllowanceSerializer

    def create(self, request,*args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            required_fields = ['limit']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all required field','limit')
            # Check if the record exists
            employee_id=request.data.get('employee',None)

            if employee_id:
               employee_query=Employees.objects.filter(id=employee_id,organization=organization_id,is_active=True)
               if employee_query.exists():
                   return errorMessage('Employee not exists in this organization')
               emp=employee_query.get()
               employee_allowance_instance = self.queryset.filter(employee=employee_id,organization=organization_id, is_active=True)
               if employee_allowance_instance.exists():
                   return errorMessage("Record already exists for this employee")
               
               if emp.work_mode!='onsite':
                   return errorMessage("Only add limit for onsite employee")
                   
            else:
                organization_allowance_instance = self.queryset.filter(employee__isnull=True,organization=organization_id, is_active=True)
                if organization_allowance_instance.exists():
                   return errorMessage("Record already exists for this organization")
                # Create a new record
            request.data['organization']=organization_id
            request.data['created_by']=request.user.id
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return errorMessage(serializer.errors)
            serializer.save()
            return success(serializer.data)
        
        except Exception as e:
            return exception(e)
        
    def list(self,request,*args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            query=self.queryset(organization=organization_id,is_active=True)
            serializers=self.serializer_class(query,many=True)
            return success(serializers.data)
        except Exception as e:
            return exception(e)




class EmployeesWFHRequestViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  
    queryset = EmployeesWFHRequest.objects.all()
    serializer_class = EmployeesWFHRequestSerializer



   
    def list(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            query = self.queryset.filter(employee__organization=organization_id,is_active=True).order_by('-id')
            # query1 = self.get_queryset().filter(is_active=True).order_by('-id').values()
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
        
    # def retrieve(self, request, *args, **kwargs):
    #     try:
            
    #         message_variable = 'Employee Leave'
    #         pk = self.kwargs['pk']
    #         query = self.get_queryset().filter(id=pk, is_active=True)
    #         if not query.exists():
    #             return errorMessage(f'No {message_variable} exists at this id')
    #         obj = query.get()
    #         serializer = self.serializer_class(obj, many=False)
    #         return success(serializer.data)
    #     except Exception as e:
    #         return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            required_fields = ['dates','employee']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [Dates, Employee]')
            
            if request.data:
                request.data._mutable = True

            employee_id =request.data['employee']
            employees = Employees.objects.filter(id=employee_id,organization=organization_id,is_active=True)
            if not employees.exists():
                return errorMessage("Employee Not exists in this organization")
            emp = employees.get()

            if emp.work_mode!='hybrid':
                return errorMessage("Employee work mode must be hybrid")

            wfh_request_dates = request.data.get('dates')
            wfh_request_dates = wfh_request_dates.split(',')

            years = {datetime.strptime(date.strip(), '%Y-%m-%d').year for date in wfh_request_dates}

            # Check if all dates are in the same year
            if len(years) > 1:
                return errorMessage("Submit a separate WFH requests specifically for the different calendar year.")
            
            
            date_validations = self.date_validation(emp.id,wfh_request_dates)
            if date_validations['status'] == 400:
                    return errorMessageWithData(date_validations['message'],date_validations['already_exists_dates'])
            # print("Data:")           
            request.data['created_by']=request.user.id
            request.data['is_active']=True
            serializer = self.serializer_class(data = request.data)
            # print(request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            employee_wfh_request=serializer.save()

            days_calculation = self.wfh_number_of_days_calculation(employee_wfh_request,wfh_request_dates)
            # print(days_calculation)
            if days_calculation['status'] == 400:
                return errorMessage(days_calculation['message'])

            # print("Test3")
            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)    


    def date_validation(self, emp_id,wfh_request_dates):
        try:
            # print("Test")
            result = {
                'status': 400, 
                'message': '', 
                'system_error_message': '',
                'already_exists_dates':[]
              
            }

            already_exists_dates=[]
           
            # print(leave_dates)
            for date in wfh_request_dates:
                
                if isinstance(date, str):
                    date = datetime.strptime(date, '%Y-%m-%d').date()
                else:
                    date = date

                emp_leaves = EmployeesWFHRequestDates.objects.filter(employee_wfh_request__employee=emp_id,date=date,is_active=True)
                
                if emp_leaves.exists():
                        already_exists_dates.append(date)
                        continue
                
            # print("Dates")
                

            if already_exists_dates:
                    # print("Test1:",already_exists_dates)
                    result['message']=f"WFH requests already exists against these dates"
                    result['already_exists_dates']=already_exists_dates
                    return result

       
            result['status'] = 200
            # print("Data Validation End:")
            return result
        except Exception as e:
            result['message'] = e
            return result


    def wfh_number_of_days_calculation(self, employee_wfh_request,wfh_request_dates):
        try:
            result = {'status': 400, 'message': '', 'duration': None, 'error_list': ''}
            emp_wfh_request_days_data = {
                'employee_wfh_request': employee_wfh_request.id,
                'date': None,
                'is_active': True 
            }
            error_list = []
            for date in wfh_request_dates:
                current_date =date 

                if isinstance(current_date, str):
                  current_date = datetime.strptime(current_date, '%Y-%m-%d').date()
                else:
                  current_date = current_date
                # print(current_date)
                emp_wfh_request_days_data['date'] = current_date
                
                serializer = EmployeesWFHRequestDatesSerializers(data=emp_wfh_request_days_data)
                if not serializer.is_valid():
                    error_list.append(serializer.errors)
                serializer.save()

            result = {'status': 200, 'message': 'success', 'error_list': ''}
            return result
        except Exception as e:
            result = {'status': 400, 'message': str(e)}
            return result
  
    
    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            # print(pk)
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('Does not exists at this id')
            elif query.filter(is_active=False).exists():
                return errorMessage('Already deactivated')
            obj = query.get()
            # if not obj.status == 'in-progress':
            #     return errorMessage('Request cannot be deleted, once it reached stage other then the in-progress stage')
            # # print(obj)
            wfh_request_dates_query=EmployeesWFHRequestDates.objects.filter(employee_wfh_request=obj,is_active=True)

            for date in wfh_request_dates_query:
                date.is_active = False
                date.save()
            # print(obj)
            # print(obj.start_date.year)
            # print(duration)
            obj.is_active = False
            obj.save()
            return successMessage("Deactivated Successfully")
        except Exception as e:
            return exception(e)
        