import calendar
from rest_framework import viewsets
from .serializers import (
    LoanTypesSerializers, SetLoanRequirementsSerializers, TimeFrequencySerializers,
    PurposeOfLoansSerializers, EmployeesLoanSerializers, UpdateEmployeesLoanSerializers,
    ListSetLoanRequirementsSerializers, TimePeriodSerializers, LoanStatusLogsSerializers,
)
from .models import (
    LoanTypes, SetLoanRequirements, PurposeOfLoans, EmployeeProvidentFunds, 
    EmployeesLoan, TimeFrequency, TimePeriod, LoanStatusLogs,
)
from helpers.status_messages import (
    exception, errorMessage, serializerError, successMessageWithData, 
    success, successMessage, successfullyCreated, successfullyUpdated
)
from helpers.decode_token import decodeToken
from helpers.email_data import requestEmailsFromEmployees, requestDecisionFromManagement
from helpers.custom_permissions import IsAuthenticated, IsEmployeeOnly
from organizations.models import StaffClassification
from employees.models import Employees
import datetime
from profiles_api.models import HrmsUsers
from django.db.models import Q

class LoanTypesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = LoanTypes.objects.all()
    serializer_class = LoanTypesSerializers

    def get_queryset(self):
        organization_id = decodeToken(self, self.request)['organization_id']
        return self.queryset.filter(organization=organization_id)

    def list(self, request, *args, **kwargs):
        try:
            query = self.get_queryset().filter(is_active=True).order_by('id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            request.data['organization'] = organization_id
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return exception(e)
        
    def get_pre_data(self, organization_id):
        try:
            query = LoanTypes.objects.filter(organization=organization_id, is_active=True).order_by('id')
            serializer = LoanTypesSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            return None
        
        
class PurposeOfLoansViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PurposeOfLoans.objects.all()
    serializer_class = PurposeOfLoansSerializers

    def get_queryset(self):
        organization_id = decodeToken(self, self.request)['organization_id']
        return self.queryset.filter(organization=organization_id)

    def list(self, request, *args, **kwargs):
        try:
            query = self.get_queryset().filter(is_active=True).order_by('id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            request.data['organization'] = organization_id
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return exception(e)

    def get_pre_data(self, organization_id):
        try:
            query = PurposeOfLoans.objects.filter(organization=organization_id, is_active=True).order_by('id')
            serializer = PurposeOfLoansSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            return None


class TimeFrequencyViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TimeFrequency.objects.all()
    serializer_class = TimeFrequencySerializers

    def get_queryset(self):
        organization_id = decodeToken(self, self.request)['organization_id']
        return self.queryset.filter(organization=organization_id)

    def list(self, request, *args, **kwargs):
        try:
            query = self.get_queryset().filter(is_active=True).order_by('id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            request.data['organization'] = organization_id
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return exception(e)
        
    def get_pre_data(self, organization_id):
        try:
            query = TimeFrequency.objects.filter(organization=organization_id, is_active=True).order_by('id')
            serializer = TimeFrequencySerializers(query, many=True)
            return serializer.data
        except Exception as e:
            return None


class TimePeriodViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TimePeriod.objects.all()
    serializer_class = TimePeriodSerializers

    def get_pre_data(self, organization_id):
        try:
            query = TimePeriod.objects.filter(time_frequency__organization=organization_id, is_active=True).order_by('id')
            serializer = TimePeriodSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            return None


class SetLoanRequirementsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = SetLoanRequirements.objects.all()
    serializer_class = SetLoanRequirementsSerializers

    def get_queryset(self):
        organization_id = decodeToken(self, self.request)['organization_id']
        return self.queryset.filter(loan_type__organization=organization_id)

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
                return errorMessage('Does not exists')
            obj = query.get()
            serializer = self.serializer_class(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            if not request.user.is_privileged:
                return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 

            required_fields = [ 'loan_type', 'organization_cap_amount',
                                'emp_salary_factor', 'max_individual_loan_limit', 'time_frequency', 
                                'emp_min_service_duration'
                            ]

            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: loan_type, organization_cap_amount, emp_salary_factor, max_individual_loan_limit, time_frequency, emp_min_service_duration]')
            
            loan_type_id = request.data['loan_type']
            loan_types = LoanTypes.objects.filter(id=loan_type_id)
            if not loan_types.exists():
                return errorMessage('Loan Type does not exists at this id')
            elif not loan_types.filter(is_active=True):
                return errorMessage('Loan type is deactivated')
            
            
            time_frequency_id = request.data['time_frequency']
            time_frequency_query = TimeFrequency.objects.filter(id=time_frequency_id, organization=organization_id, is_active=True)
            if not time_frequency_query.exists():
                return errorMessage('Does not exists at this id')
            elif not time_frequency_query.filter(is_active=True):
                return errorMessage('Time frequency is deactivated at this id')

            # obj = loan_types.get()
            # queryset = self.get_queryset().filter(loan_type=loan_type_id, is_active=True)
            # if queryset.exists():
            #     return errorMessage(f'Already data exists against {obj.title}')
            # if queryset.filter(is_lock=False).exists():
            #     return errorMessage(f'Already data exists against {obj.title}')
            # elif queryset.filter(is_lock=True, unlock_by__isnull=False).exists():
            #     return errorMessage(f'{obj.title} is already locked. Please unlock it first')
        
            serializer = self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            loan_data = serializer.save()

            queryset = self.get_queryset().filter(loan_type=loan_type_id, is_active=True).exclude(id=loan_data.id)
            if queryset.exists():
                for data in queryset:
                    data.is_active = False
                    data.save()


            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)

    def patch(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']

            pk = self.kwargs['pk']
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('Does not exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('It is deactivated at this id')

            obj = query.get()

            if 'loan_type' in request.data:
                loan_type_id = request.data['loan_type']
                loan_types = LoanTypes.objects.filter(id=loan_type_id)
                if not loan_types.exists():
                    return errorMessage('Loan Type does not exists at this id')
                elif not loan_types.filter(is_active=True):
                    return errorMessage('Loan type is deactivated')
            else:
                loan_type_id = obj.loan_type.id
            
            if 'time_frequency' in request.data:
                time_frequency_id = request.data['time_frequency']
                time_frequency_query = TimeFrequency.objects.filter(id=time_frequency_id, organization=organization_id, is_active=True)
                if not time_frequency_query.exists():
                    return errorMessage('Does not exists at this id')
                elif not time_frequency_query.filter(is_active=True):
                    return errorMessage('Time frequency is deactivated at this id')
            else:
                time_frequency_id = obj.time_frequency.id

            data_dict = {
                'loan_type': loan_type_id,
                'organization_cap_amount': request.data.get('organization_cap_amount', obj.organization_cap_amount),
                'emp_salary_factor': request.data.get('emp_salary_factor', obj.emp_salary_factor),
                'max_individual_loan_amount': request.data.get('max_individual_loan_amount', obj.max_individual_loan_limit),
                'time_frequency': time_frequency_id,
                'emp_min_service_duration': request.data.get('emp_min_service_duration', obj.emp_min_service_duration),
                'is_provident_fund': request.data.get('is_provident_fund', obj.is_provident_fund),
                'min_provident_fund_duration':request.data.get('min_provident_fund_duration', obj.min_provident_fund_duration),
            }

        
            serializer = self.serializer_class(data = data_dict)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            loan_data = serializer.save()

            queryset = self.get_queryset().filter(loan_type=loan_type_id, is_active=True).exclude(id=loan_data.id)
            if queryset.exists():
                for data in queryset:
                    data.is_active = False
                    data.save()


            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)

    # def patch(self, request, *args, **kwargs):
    #     try:
        #     pk = self.kwargs['pk']
        #     query = self.get_queryset().filter(id=pk)
        #     if not query.exists():
        #         return errorMessage('Does not exists at this id')

        #     obj = query.get()
            
        #     # is_lock = obj.is_lock
        #     # if is_lock:
        #     #     return errorMessage("requirement for loan are locked. Unlock it first")

        #     if 'loan_type' in request.data:
        #         loan_type_id = request.data['loan_type']
        #         if obj.loan_type.id != loan_type_id:
        #             loan_types = LoanTypes.objects.filter(id=loan_type_id)
        #             if not loan_types.exists():
        #                 return errorMessage('Loan Type does not exists at this id')
        #             elif not loan_types.filter(is_active=True):
        #                 return errorMessage('Loan type is deactivated')
                    
        #             obj = loan_types.get()
        #             queryset = self.get_queryset().filter(loan_type=loan_type_id, is_active=True)
        #             if queryset.filter(lock_by=False):
        #                 return errorMessage(f'Already data exists against {obj.title}')
        #             elif queryset.filter(lock_by=True, unlock_by__isnull=False):
        #                 return errorMessage(f'{obj.title} is already locked. Please unlock it first')
                    
        #     serializer = self.serializer_class(obj, data=request.data, partial=True)
        #     if not serializer.is_valid():
        #         return serializerError(serializer.errors)
        #     serializer.save()
        #     return successfullyUpdated(serializer.data)
        # except Exception as e:
        #     return exception(e)
    
    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('does not exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('Already deactivated at this id')
            # elif query.filter(is_lock=True):
            #     return errorMessage('It is locked. It cannot get deactivate. Please unlock it first')
            
            obj = query.get()
            obj.is_active = False
            obj.save()
            return successMessage('Sucessfully deactivated')
        except Exception as e:
            return exception(e)
        
    # def get_lock_loan(self, request, *args, **kwargs):
    #     try:
    #         pk = self.kwargs['pk']
    #         query = self.get_queryset().filter(id=pk)
    #         if not query.exists():
    #             return errorMessage('No Leave exists at this id')
    #         elif not query.filter(is_active=True):
    #             return errorMessage('Leave is deactivated at this id')
    #         elif query.filter(is_lock=True):
    #             return errorMessage('It is already locked')

    #         obj = query.get()
    #         obj.is_lock = True
    #         hrmsuser = HrmsUsers.objects.filter(id=request.user.id).get()
    #         obj.lock_by = hrmsuser
    #         obj.locked_date = datetime.datetime.today()
    #         obj.save()

    #         return successMessage('Successfully locked')
    #     except Exception as e:
    #         return exception(e)

    # def get_unlock_loan(self, request, *args, **kwargs):
    #     try:
    #         pk = self.kwargs['pk']
    #         query = self.get_queryset().filter(id=pk)
    #         if not query.exists():
    #             return errorMessage('No Loan exists at this id')
    #         elif query.filter(is_lock=False, is_active=True):
    #             return errorMessage('It is already unlocked. Lock it first')
    #         elif query.filter(is_lock=True, unlock_by__isnull=False, is_active=False):
    #             return errorMessage('It is already unlocked and it is deactivated as well')
    #         elif not query.filter(is_lock=True, is_active=True):
    #             return errorMessage('loan is deactivated at this id')
            
    #         obj = query.get()

    #         data_dict = {
    #             'loan_type': obj.loan_type.id,
    #             'organization_cap_amount': obj.organization_cap_amount,
    #             'emp_salary_factor': obj.emp_salary_factor,
    #             'max_individual_loan_limit': obj.max_individual_loan_limit,
    #             'time_frequency': obj.time_frequency.id,
    #             'emp_min_service_duration': obj.emp_min_service_duration,
    #             'is_provident_fund': obj.is_provident_fund,
    #             'min_provident_fund_duration': obj.min_provident_fund_duration,
    #             'is_lock': False,
    #             'is_active': obj.is_active,
    #         }

    #         serializer = self.serializer_class(data = data_dict)
    #         if not serializer.is_valid():
    #             return serializerError(serializer.errors)
    #         serializer.save()

    #         obj.is_active = False
    #         hrmsuser = HrmsUsers.objects.filter(id=request.user.id).get()
    #         obj.unlock_by = hrmsuser
    #         obj.unlocked_date = datetime.datetime.today()
    #         obj.save()

    #         return successMessageWithData('Successfully unlocked', serializer.data)
    #     except Exception as e:
    #         return exception(e)
        
    def get_pre_data(self, organization_id):
        try:
            query = SetLoanRequirements.objects.filter(loan_type__organization=organization_id, is_active=True).order_by('id')
            serializer = SetLoanRequirementsSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            return None


class EmployeesLoanViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsEmployeeOnly]
    queryset = EmployeesLoan.objects.all()
    serializer_class = EmployeesLoanSerializers
   
    def get_queryset(self):
        token_data = decodeToken(self, self.request)
        organization_id = token_data['organization_id']
        employee_id = token_data['employee_id']
        return self.queryset.filter(employee=employee_id, employee__organization=organization_id)
    
    def list(self, request, *args, **kwargs):
        try:
            query = self.get_queryset().filter(is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def retrieve(self, request, *args, **kwargs):
        try:
            message_variable = 'Employee Loan'
            pk = self.kwargs['pk']
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage(f'No {message_variable} exists at this id')
            elif not query.filter(is_active=True).exists():
                return errorMessage(f'{message_variable} is deactivated at this id')
            obj = query.get()
            serializer = self.serializer_class(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            employees = Employees.objects.get(hrmsuser=request.user.id)
            emp = employees
            emp_id = emp.id
            request.data['employee'] = emp_id
            
            # HR should fill all these information
            current_salary = emp.current_salary
            joining_date = emp.joining_date
            staff_classification = emp.staff_classification
            employee_type = emp.employee_type
            if not staff_classification:
                return errorMessage("Employee staff classification is not set. Contact admin to set your staff classification first")
            if not employee_type:
                return errorMessage("Employee type is not set. Contact admin to set employee type first")
            if employee_type:
                employee_type_title = employee_type.title
                if not employee_type_title == 'Permanent':
                    return errorMessage("You are not a permanent Employee")
            if not current_salary:
                return errorMessage("Employee salary is not set. Contact admin to add your salary first")
            if not joining_date:
                return errorMessage("Employee joining date is not set yet. Contact administrator to set the joining date first")

            required_fields = ['amount', 'loan_type', 'number_of_loan_installment', 'purpose_of_loan']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [amount, loan_type, number_of_loan_installment, purpose_of_loan]')
            amount = request.data['amount']

            request.data['priority'] = staff_classification.level

            loan_installments = request.data['number_of_loan_installment']
            
            loan_installments_list = [4, 6, 8, 12]
            
            if loan_installments not in loan_installments_list:
                return errorMessage(f'Number of loan installment could only be {loan_installments_list}')          

            purpose_of_loan_id = request.data['purpose_of_loan']
            purpose_of_loan = PurposeOfLoans.objects.filter(id=purpose_of_loan_id, organization=organization_id)
            if not purpose_of_loan.exists():
                return errorMessage('Purpose of loan does not exists')
            elif not purpose_of_loan.filter(is_active=True):
                return errorMessage('This loan purpose is deactivated at this id')


            loan_type_id = request.data['loan_type']
            loan_types = LoanTypes.objects.filter(id=loan_type_id, is_active=True)
            if not loan_types.exists():
                return errorMessage('Loan Type does not exists at this id')
            elif not loan_types.filter(is_active=True):
                return errorMessage('Loan type is deactivated')

            loan_requirements = SetLoanRequirements.objects.filter(loan_type=loan_type_id, is_active=True)
            if not loan_requirements.exists():
                return errorMessage('Loan requirements are not set yet. Kindly, set it first')
            # elif not loan_requirements.filter(is_lock=True):
            #     return errorMessage('Loan requirements are not locked yet. Kindly, lock it first')
            loan_requirement_object = loan_requirements.get()    # filter(is_lock=True).last()
            request.data['set_loan_requirement'] = loan_requirement_object.id

            salary_factor = loan_requirement_object.emp_salary_factor
            organization_cap_amount = loan_requirement_object.organization_cap_amount
            service_duration = loan_requirement_object.emp_min_service_duration
            max_loan = loan_requirement_object.max_individual_loan_limit
            is_pf = loan_requirement_object.is_provident_fund
            pf_duration = loan_requirement_object.min_provident_fund_duration
            current_date = datetime.datetime.today()
            if salary_factor:
                max_loan_amount = salary_factor * current_salary
                if amount > max_loan_amount:
                    return  errorMessage(f'Loan amount could not be greater than {max_loan_amount}')
            if organization_cap_amount:
                if amount >= organization_cap_amount:
                    return  errorMessage(f'Loan amount could not be greater than {organization_cap_amount}')
            if service_duration:
                service_duration_check = self.service_duration_check(current_date, joining_date, service_duration)
                if service_duration_check['status'] == 400:
                    return errorMessage(service_duration_check['message'])
            if max_loan:
                if amount > max_loan:
                    return errorMessage(f'Loan amount could not be greater than {max_loan}')
            if is_pf:
                pf_duration = self.pf_duration_check(emp_id, pf_duration, current_date) 
                if pf_duration['status'] == 400:
                    return errorMessage(pf_duration['message'])

            serializer = self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            requestEmailsFromEmployees('Loan', 'saddam.baig@kavmails.net')
            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)

    def service_duration_check(self, current_date, joining_date, service_duration):
        try:
            result = {'status': 400, 'message': None}
            joining_date = datetime.datetime.strptime(str(joining_date), '%Y-%m-%d').date()

            num_months = (current_date.year - joining_date.year) * 12 + (current_date.month - joining_date.month)
            if service_duration <= num_months:
                result['status'] = 200
                return result
            result['message'] = f'Employee service should be atleast {service_duration}'
            return result
        except Exception as e:
            result['message'] = str(e)
            return result

    def pf_duration_check(self, emp_id, pf_duration, current_date):
        try:
            result = {'status': 400, 'message': None}
            employee_pf = EmployeeProvidentFunds.objects.filter(employee=emp_id, has_approval=True, is_active=True)
            if not employee_pf.exists():
                result['message'] = 'Employee provident fund is not approved yet'
                return result
            if pf_duration > 0:
                oldest_approved_date = employee_pf.order_by('approved_date').values_list('approved_date', flat=True).first()
                if oldest_approved_date is not None:
                    employee_pf = employee_pf.filter(approved_date=oldest_approved_date)
                    employee_pf_obj = employee_pf.first()
                    pf_start_date = employee_pf_obj.approved_date
                    date = datetime.datetime.strptime(pf_start_date, '%Y-%m-%d').date()
                    num_months = (current_date.year - date.year) * 12 + (current_date.month - date.month)
                    if num_months < pf_duration:
                        result['message'] = f'Employee provident fund should be atleast of {pf_duration} months'
                        return result
        
            result['status'] = 200
            return result
        except Exception as e:
            result['message'] = str(e)
            return result


    def patch(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('This employee has no employee loan at this id')
            obj = query.get()
            
            if 'status' in request.data:
                return errorMessage('Employee is not allowed to change the status')

            status = obj.status
            if not status == 'in-progress':
                return errorMessage(f'It cannot get updated now. As your request current status is {status}')

            serializer = UpdateEmployeesLoanSerializers(obj, data = request.data, partial=True)
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
                return errorMessage('No loan exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('Loan is deactivated at this id')
            elif not query.filter(status='in-progress', is_active=True):
                return errorMessage('It cannot get deactivated now. Request could only get deactivated if the status is in-progress.')
            obj = query.get()

            obj.is_active = False
            obj.save()
            return successMessage('Sucessfully deactivated')
        except Exception as e:
            return exception(e)
        
    def get_pre_data(self,request,*args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            employee_id = decodeToken(self, self.request)['employee_id']
            year=request.data.get("year",None)
            if year is None:
                year=datetime.datetime.today().year
            # print(year)
            query = EmployeesLoan.objects.filter(Q(loan_start_date__year=year)|Q(loan_end_date__year=year),employee=employee_id, employee__organization=organization_id, is_active=True).order_by('-id')
            print(query.values())
            serializer = EmployeesLoanSerializers(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return None
        

class LoanStatusLogsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ] 
    queryset = LoanStatusLogs.objects.all()
    serializer_class = LoanStatusLogsSerializers

    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            pk = self.kwargs['pk']
            query = EmployeesLoan.objects.filter(employee__organization=organization_id, id=pk)
            if not query.exists():
                return errorMessage('No employee loan request exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('loan request is deactivated at this id')
            
            queryset = self.queryset.filter(employee_loan=pk, is_active=True)
            serializer = self.serializer_class(queryset, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
    
    def get_all_loan_requests(self, request,*args, **kwargs):
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
                query = EmployeesLoan.objects.filter(
                        Q(loan_end_date__gte=first_day_of_previous_month, loan_start_date__lte=last_day_of_current_month) |
                        Q(loan_end_date__gte=first_day_of_previous_month, loan_end_date__lte=last_day_of_current_month) |
                        Q(loan_start_date__gte=first_day_of_previous_month, loan_start_date__lte=last_day_of_current_month),
                        loan_type__organization=organization_id, is_active=True
                    ).order_by('-id')
                
            
            else:
                if year is None:
                    year=datetime.datetime.today().year

                query = EmployeesLoan.objects.filter(
                        Q(loan_start_date__month=month) | Q(loan_end_date__month=month),
                        Q(loan_start_date__year=year) | Q(loan_end_date__year=year),
                        loan_type__organization=organization_id, is_active=True
                    ).order_by('-id')
            
            serializer = EmployeesLoanSerializers(query, many=True)
            return success(serializer.data)

        except Exception as e:
            return None


    def patch(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            pk = self.kwargs['pk']
            query = EmployeesLoan.objects.filter(employee__organization=organization_id, id=pk)
            if not query.exists():
                return errorMessage('No employee loan request exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('loan request is deactivated at this id')
            
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
                'employee_loan': pk,
                'status': status,
                'action_by': request.user.id,
                'action_on': datetime.date.today(), 
                'decision_reason': decision_reason,
            }

            serializer = self.serializer_class(data = status_dict)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            requestDecisionFromManagement(obj.employee.name,'Loan Status Update','Loan',status,decision_reason, obj.employee.official_email)
            return successMessageWithData('Successfully updated', serializer.data)
        except Exception as e:
            return exception(e)
        

