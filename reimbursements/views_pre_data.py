from rest_framework import generics
from employees.models import Employees
from helpers.custom_permissions import IsAuthenticated
from helpers.status_messages import exception, success, successMessageWithData
from helpers.decode_token import decodeToken
from .views_medical import MedicalAllowanceViewset, EmployeesMedicalAllowanceViewset, MedicalStatusLogsViewset
from .views_pf import ProvidentFundsViewset, EmployeeProvidentFundsViewset, ProvidentFundStatusLogsViewset
from .views_leaves import LeaveTypesViewset, SetLeavesDurationViewset, EmployeesLeavesViewset, LeavesStatusLogsViewset
from .views_gym import GymAllowanceViewset, EmployeesGymAllowanceViewset, GymStatusLogsViewset
from .views_loan import LoanTypesViewset, TimeFrequencyViewset, TimePeriodViewset, PurposeOfLoansViewset, SetLoanRequirementsViewset, EmployeesLoanViewset, LoanStatusLogsViewset
from .models import EmployeesGymAllowance
from .serializers import EmployeesGymAllowanceSerializers
from organizations.models import StaffClassification
from organizations.serializers import StaffClassificationOrgSerializers
from helpers.status_messages import errorMessage
from rest_framework import viewsets
import datetime
from django.db import connection
class PreDataReimbursementRequest(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
           
            
            # gym allowance
            gym_allowance = GymAllowanceViewset().get_pre_data(organization_id)
            
            # medical allowance
        
            medical_allowance = MedicalAllowanceViewset().get_pre_data(organization_id)

            # pf
            provident_fund = ProvidentFundsViewset().get_pre_data(organization_id)

            # leave types
            leave_types = LeaveTypesViewset().get_pre_data(organization_id)

            # set_leave_duration
            set_leave_duration = SetLeavesDurationViewset().get_pre_data(organization_id)

            staff_classification = StaffClassification.objects.filter(organization=organization_id, is_active=True).order_by('-id')
            staff_classification_serializer = StaffClassificationOrgSerializers(staff_classification, many=True)

            # loan data
            loan_type = LoanTypesViewset().get_pre_data(organization_id)
            time_frequency = TimeFrequencyViewset().get_pre_data(organization_id)
            time_period = TimePeriodViewset().get_pre_data(organization_id)
            purpose_of_loan = PurposeOfLoansViewset().get_pre_data(organization_id)
            set_loan_requirements = SetLoanRequirementsViewset().get_pre_data(organization_id)

            data = {
                'gym_allowance': gym_allowance,
                'medical_allowance': medical_allowance,
                'provident_fund': provident_fund,
                'leave_types': leave_types,
                'set_leave_duration': set_leave_duration,
                'staff_classification': staff_classification_serializer.data,
                'loan_type': loan_type,
                'time_frequency': time_frequency,
                'time_period': time_period,
                'purpose_of_loan': purpose_of_loan,
                'set_loan_requirements': set_loan_requirements,
            }

            return success(data)


        except Exception as e:
            return exception(e)
        

class PreDataEmployeeReimbursementRequest(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            current_year =datetime.datetime.today().year

            
            # # employee gym
            # employee_gym_allowance = EmployeesGymAllowanceViewset().get_pre_data(organization_id, employee_id)

            #  # employee medical allowance
            # employee_medical_allowance = EmployeesMedicalAllowanceViewset().get_pre_data(organization_id, employee_id)

            # # employee pf
            # employee_provident_fund = EmployeeProvidentFundsViewset().get_pre_data(organization_id, employee_id)
            # employee_leaves = EmployeesLeavesViewset().get_pre_data(organization_id, employee_id)
            # employee_loan = EmployeesLoanViewset().get_pre_data(organization_id, employee_id)
            # employee leave types
            leave_types = LeaveTypesViewset().get_pre_data(organization_id,current_year)
            # loan data
            loan_type = LoanTypesViewset().get_pre_data(organization_id)
            time_frequency = TimeFrequencyViewset().get_pre_data(organization_id)
            time_period = TimePeriodViewset().get_pre_data(organization_id)
            purpose_of_loan = PurposeOfLoansViewset().get_pre_data(organization_id)

            data = {
                'employee_gym_allowance':None,
                'employee_medical_allowance': None,
                'employee_provident_fund': None,
                'employee_leaves': None,
                'employee_loan': None,
                'leave_types': leave_types,
                'loan_type': loan_type,
                'time_frequency': time_frequency,
                'time_period': time_period,
                'purpose_of_loan': purpose_of_loan,
                
            }

            return success(data)

        except Exception as e:
            return exception(e)


     

class PreDataGetEmployeeRequests(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            month=request.data.get('month',None)
            year=request.data.get('year',None)
            
            # print(month,year)
            gym_allowance = GymStatusLogsViewset().get_all_gym_requests(organization_id,month,year)
            medical_allowance = MedicalStatusLogsViewset().get_all_medical_requests(organization_id,month,year)
            provident_fund = ProvidentFundStatusLogsViewset().get_all_pf_requests(organization_id,month,year)
            # leaves = LeavesStatusLogsViewset().get_all_leaves_requests(organization_id)
            leaves = LeavesStatusLogsViewset().get_all_leaves_requests_new(organization_id,month,year)
            loan = LoanStatusLogsViewset().get_all_loan_requests(organization_id,month,year)

            data = {
                'gym_allowance': gym_allowance,
                'medical_allowance': medical_allowance,
                'provident_fund': provident_fund,
                'leaves': leaves,
                'loan': loan,
            }

            return success(data)

        except Exception as e:
            return exception(e)

class AllowancesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]


    def get_employee_total_approved_amount(self,request,*args, **kwargs):
        try:

            organization_id = decodeToken(self, self.request)['organization_id']
            employee_id=self.kwargs['employee_id']
            start_date=request.data.get('start_date',None)
            end_date=request.data.get('end_date',None)
            start_date=None
            end_date=None
            employee=Employees.objects.filter(id=employee_id)
            if not employee.exists():
                return errorMessage("Employee not exists at given id")
            # print(current_month)
            if start_date is None:
                current_year = datetime.date.today().year

                # Get the first day of the current year
                start_date = datetime.date(current_year, 1, 1)

            

            if end_date is None:
                end_date=datetime.datetime.today().date()

            if str(end_date)<str(start_date):
                return errorMessage("end date must be greater than start date")
                        
            query_data=custom_query_employee_total_amount_count(start_date,end_date,employee_id,organization_id)
            return successMessageWithData('Success',query_data)

        except Exception as e:
            return exception(e)



def custom_query_employee_total_amount_count(start_date,end_data,employee_id,organization_id):
    # print(ep_yearly_segmentation, ep_batch,organization_id)
        with connection.cursor() as cursor:
            cursor.execute("""
    WITH date_ranges AS (
    SELECT 
        %s::date AS start_date,
        %s::date AS end_date
)
SELECT 
    e.id,
    e.name AS employee_name,
    e.official_email AS email,
    e.department_id AS dp_id,
    d.title AS dp_name,
    e.joining_date AS joining_date,
    e.current_salary AS salary,
    stf.title AS designation,
    ept.title AS status,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.dob)) AS age,
    COALESCE(medical.total_amount, 0) AS total_medical_allowance,
    COALESCE(gym.total_amount, 0) AS total_gym_allowance
FROM 
    employees_employees AS e
INNER JOIN 
    departments_departments AS d ON e.department_id = d.id AND d.is_active = True
LEFT JOIN 
    organizations_staffclassification AS stf ON e.staff_classification_id = stf.id AND stf.is_active = True
LEFT JOIN 
    employees_employeetypes AS ept ON e.employee_type_id = ept.id AND ept.is_active = True
LEFT JOIN (
    SELECT 
        ema.employee_id,
        SUM(CASE WHEN ema.status = 'approved' THEN ema.amount ELSE 0 END) AS total_amount
    FROM 
        reimbursements_employeesmedicalallowance AS ema
    WHERE 
        ema.is_active = True 
        AND ema.created_at >= (SELECT start_date FROM date_ranges)::timestamp 
        AND ema.created_at <= (SELECT end_date FROM date_ranges)::timestamp
    GROUP BY 
        ema.employee_id
) AS medical ON medical.employee_id = e.id
LEFT JOIN (
    SELECT 
        ega.employee_id,
        SUM(CASE WHEN ega.status = 'approved' THEN ega.amount ELSE 0 END) AS total_amount
    FROM 
        reimbursements_employeesgymallowance AS ega
    WHERE 
        ega.is_active = True 
        AND ega.created_at >= (SELECT start_date FROM date_ranges)::timestamp 
        AND ega.created_at <= (SELECT end_date FROM date_ranges)::timestamp
    GROUP BY 
        ega.employee_id
) AS gym ON gym.employee_id = e.id
WHERE 
    e.is_active = True 
    AND e.id = %s
    AND e.organization_id = %s;
        """, [start_date,end_data,employee_id,organization_id])
            columns = [col[0] for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return rows

        