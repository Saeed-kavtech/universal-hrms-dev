import calendar
from rest_framework import viewsets
from .serializers import (
    ProvidentFundsSerializers, ProvidentFundsSerializers, EmployeeProvidentFundsSerializers, 
    ProvidentFundStatusLogsSerializers
)
from .models import ProvidentFunds, EmployeeProvidentFunds, ProvidentFundStatusLogs
from helpers.status_messages import (
    exception, errorMessage, success, successMessage, successfullyCreated, 
    successfullyUpdated, serializerError, successMessageWithData
)
from helpers.decode_token import decodeToken
from helpers.email_data import requestEmailsFromEmployees, requestDecisionFromManagement
from helpers.custom_permissions import IsAuthenticated, IsEmployeeOnly
from employees.models import Employees
import datetime


class ProvidentFundsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ProvidentFunds.objects.all()
    serializer_class = ProvidentFundsSerializers

    def get_queryset(self):
        organization_id = decodeToken(self, self.request)['organization_id']
        return self.queryset.filter(organization=organization_id)

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
            if not request.user.is_privileged:
                return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            
            request.data['organization'] = organization_id
            request.data['user'] = request.user.id
            serializer = self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            data = serializer.save()
            
            query = self.get_queryset().filter(is_active=True).exclude(id=data.id)
            if query.exists():
                for obj in query:
                    obj.is_active=False
                    obj.save()

            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)      

    def delete(self, request, *args, **kwargs):
        try:
            query = self.get_queryset()
            if not query.exists():
                return errorMessage('No provident funds exists')
            if not query.filter(is_active=True):
                return errorMessage('Provident funds is already deactivated')
            
            obj = query.filter(is_active=True).get()
            obj.is_active = False
            obj.save()
            return successMessage('Sucessfully deactivated')
        except Exception as e:
            return exception(e)
        
    def get_pre_data(self, organization_id):
        try:
            query = ProvidentFunds.objects.filter(organization=organization_id, is_active=True).order_by('-id')
            serializer = ProvidentFundsSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            return None


class EmployeeProvidentFundsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsEmployeeOnly]
    queryset = EmployeeProvidentFunds.objects.all()
    serializer_class = EmployeeProvidentFundsSerializers

    def get_queryset(self):
        token_data = decodeToken(self, self.request)
        organization_id = token_data['organization_id']
        employee_id = token_data['employee_id']
        return self.queryset.filter(employee=employee_id, employee__organization=organization_id)

    def list(self, request, *args, **kwargs):
        try:
            query = self.get_queryset().filter(is_active=True)
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']

            emp = Employees.objects.get(id=employee_id)
            if not emp.employee_type:
                return errorMessage("Employee type is a required field")
            elif not emp.employee_type.title == 'Permanent':
                return errorMessage('Only Permanent Employees is elligible for Provident Funds')

            if not 'has_approval' in request.data:
                return errorMessage(' please approve the terms and conditions first')
            
            provident_fund = ProvidentFunds.objects.filter(organization=organization_id, is_active=True)
            if not provident_fund:
                return errorMessage('Provident Fund is not set by the adminstrator. Please contact the adminstrator')

            emp_provident_fund = self.get_queryset().filter(is_active=True)
            if emp_provident_fund.exists():
                return errorMessage('have already applied for the provident fund')

            pf_obj = provident_fund.get()
            request.data['provident_fund'] = pf_obj.id
            request.data['employee'] = emp.id
            request.data['status'] = 'in-progress'
            request.data['date'] = datetime.date.today()
            
            serializer = self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            requestEmailsFromEmployees('Provident Fund', 'saddam.baig@kavmails.net')
            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)      
        
    def get_pre_data(self, request,*args, **kwargs):
        try:    
            organization_id=decodeToken(self,self.request)['organization_id']  
            employee_id=decodeToken(self,self.request)['employee_id']    
            print(employee_id)
            year =request.data.get('year',None)
            if year is None:
                year=datetime.datetime.today().year  

            query = EmployeeProvidentFunds.objects.filter(employee=employee_id, employee__organization=organization_id,date__year=year,is_active=True)
            serializer = EmployeeProvidentFundsSerializers(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return None  


class ProvidentFundStatusLogsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ] 
    queryset = ProvidentFundStatusLogs.objects.all()
    serializer_class = ProvidentFundStatusLogsSerializers

    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            pk = self.kwargs['pk']
            query = EmployeeProvidentFunds.objects.filter(employee__organization=organization_id, id=pk)
            if not query.exists():
                return errorMessage('No employee provident fund request exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('provident fund request is deactivated at this id')
            
            queryset = self.queryset.filter(employee_provident_fund=pk, is_active=True)
            serializer = self.serializer_class(queryset, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def get_all_pf_requests(self,request,*args, **kwargs):
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
                query = EmployeeProvidentFunds.objects.filter(
                        provident_fund__organization=organization_id,date__range=[first_day_of_previous_month, last_day_of_current_month],is_active=True
                    ).order_by('-id')
               
            
            else:
                if year is None:
                    year=datetime.datetime.today().year
                query = EmployeeProvidentFunds.objects.filter(
                        provident_fund__organization=organization_id,date__month=month,date__year=year,is_active=True
                    ).order_by('-id')
                

            serializer = EmployeeProvidentFundsSerializers(query, many=True)
            return success(serializer.data)

        except Exception as e:
            return None
   

    def patch(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            pk = self.kwargs['pk']
            query = EmployeeProvidentFunds.objects.filter(employee__organization=organization_id, id=pk)
            if not query.exists():
                return errorMessage('No employee provident fund request exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('provident fund request is deactivated at this id')
            
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
                'employee_provident_fund': pk,
                'status': status,
                'action_by': request.user.id,
                'action_on': datetime.date.today(), 
                'decision_reason': decision_reason,
            }

            serializer = self.serializer_class(data = status_dict)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            requestDecisionFromManagement(obj.employee.name,'Provident Fund Status Update','Provident Fund',status,decision_reason, obj.employee.official_email)
            return successMessageWithData('Successfully updated', serializer.data)
        except Exception as e:
            return exception(e)
        
