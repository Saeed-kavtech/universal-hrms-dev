from rest_framework import serializers
from employees.models import Employees
from .models import (
    EmployeesWFHAllowance, EmployeesWFHRequest, EmployeesWFHRequestDates, GymAllowance, EmployeesGymAllowance, GymStatusLogs, MedicalAllowance, EmployeesMedicalAllowance,
    ProvidentFunds, EmployeeProvidentFunds, LeaveTypes, SetLeavesDuration, EmployeesLeaves,
    LoanTypes, SetLoanRequirements, EmployeesLoan, PurposeOfLoans, TimeFrequency, TimePeriod,
    MedicalStatusLogs, ProvidentFundStatusLogs, LeavesStatusLogs, LoanStatusLogs,
    EmployeesRemainingMedicalAllowance, EmployeeLeaveDates, EmployeeLeaveCalculations,
    EmployeesOfficialHolidays,ScriptStatusLogs, CompensatoryLeave,GENDER_Classification_CHOICES
)
# import datetime
class GymAllowanceSerializers(serializers.ModelSerializer):
    staff_classification_title = serializers.SerializerMethodField()
    class Meta:
        model = GymAllowance
        fields = [
            'id',
            'staff_classification',
            'staff_classification_title',
            'monthly_limit',
            'is_active',
        ]

    def get_staff_classification_title(self, obj):
        try:
            return obj.staff_classification.title
        except Exception as e:
            print(str(e))
            return None


class UpdateGymAllowanceSerializers(serializers.ModelSerializer):
    class Meta:
        model = GymAllowance
        fields = [
            'monthly_limit',
            'is_active',
        ]

class EmployeesGymAllowanceSerializers(serializers.ModelSerializer):
    gym_monthly_limit = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    employee_email = serializers.SerializerMethodField()
    month = serializers.SerializerMethodField()
    class Meta:
        model = EmployeesGymAllowance
        fields = [
            'id',
            'employee',
            'employee_name',
            'employee_email',
            'gym_allowance',
            'gym_monthly_limit',
            'amount',
            'gym_receipt',
            'date',
            'month',
            'status',
            'additional_comments',
            'decision_reason',
            'is_active',
        ]

        read_only_fields = [
            'decision_reason',
        ]
    
    def validate_gym_receipt(self, value):
        try:
            if value:
                max_size = 5 * 1024 * 1024
                if value.size > max_size:
                    raise serializers.ValidationError
            return value
        except serializers.ValidationError:
            raise serializers.ValidationError("File size cannot be greater than 5MB")
        except Exception as e:
            print(str(e))
            return None

    def get_month(self, obj):
        try:
            if obj.date:
                return obj.date.month
        except Exception as e:
            print(str(e))
            return None

    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None
        
    def get_employee_email(self, obj):
        try:
            return obj.employee.official_email
        except Exception as e:
            print(str(e))
            return None


    def get_gym_monthly_limit(self, obj):
        try:
            return obj.gym_allowance.monthly_limit
        except Exception as e:
            print(str(e))
            return None
        
    # def validate_file_size()
            

    
class UpdateEmployeesGymAllowanceSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeesGymAllowance
        fields = [
            'id',
            'amount',
            'gym_receipt',
            'date',
            'additional_comments',
            'is_active',
        ]

    def validate_gym_receipt(self, value):
        try:
            if value:
                max_size = 5 * 1024 * 1024
                if value.size > max_size:
                    raise serializers.ValidationError
            return value
        except serializers.ValidationError:
            raise serializers.ValidationError("File size cannot be greater than 5MB")
        except Exception as e:
            print(str(e))
            return None


class GymStatusLogsSerializers(serializers.ModelSerializer):
    class Meta:
        model = GymStatusLogs
        fields = [
            'id',
            'employee_gym_allowance',
            'status',
            'decision_reason',
            'action_by',
            'action_on',
            'is_active',
        ]

class MedicalAllowanceSerializers(serializers.ModelSerializer):
    staff_classification_title = serializers.SerializerMethodField()
    class Meta:
        model = MedicalAllowance
        fields = [
            'id',
            'staff_classification',
            'staff_classification_title',
            'yearly_limit',
            'year',
            'is_active',
        ]

    def get_staff_classification_title(self, obj):
        try:
            return obj.staff_classification.title
        except Exception as e:
            print(str(e))
            return None


class UpdateMedicalAllowanceSerializers(serializers.ModelSerializer):
    staff_classification_title = serializers.SerializerMethodField()
    class Meta:
        model = MedicalAllowance
        fields = [
            'staff_classification_title',
            'yearly_limit',
            'is_active',
        ]

    def get_staff_classification_title(self, obj):
        try:
            return obj.staff_classification.title
        except Exception as e:
            print(str(e))
            return None



class EmployeesMedicalAllowanceSerializers(serializers.ModelSerializer):
    medical_yearly_limit = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    employee_email = serializers.SerializerMethodField()
    month = serializers.SerializerMethodField()
    employee_remaining_allowance = serializers.SerializerMethodField()
    class Meta:
        model = EmployeesMedicalAllowance
        fields = [
            'id',
            'employee',
            'employee_name',
            'employee_email',
            'medical_allowance',
            'medical_yearly_limit',
            'amount',
            'medical_receipt',
            'date',
            'month',
            'status',
            'decision_reason',
            'additional_comments',
            'employee_remaining_allowance',
            'is_active',
        ]
        
        read_only_fields = [
            'decision_reason',
        ]

    def validate_medical_receipt(self, value):
        try:
            if value:
                max_size = 5 * 1024 * 1024
                if value.size > max_size:
                    raise serializers.ValidationError
            return value
        except serializers.ValidationError:
            raise serializers.ValidationError("File size cannot be greater than 5MB")
        except Exception as e:
            print(str(e))
            return None

    def get_month(self, obj):
        try:
            if obj.date:
                return obj.date.month
        except Exception as e:
            print(str(e))
            return None

    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None
        
    def get_employee_email(self, obj):
        try:
            return obj.employee.official_email
        except Exception as e:
            print(str(e))
            return None
        
    def get_medical_yearly_limit(self, obj):
        try:
            return obj.medical_allowance.yearly_limit
        except Exception as e:
            print(str(e))
            return None
        
    def get_employee_remaining_allowance(self, obj):
        try:
            query = EmployeesRemainingMedicalAllowance.objects.filter(employee=obj.employee,medical_allowance=obj.medical_allowance,is_active=True)
            serializer = EmployeesRemainingMedicalAllowanceSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            print(str(e))
            return None

class UpdateEmployeesMedicalAllowanceSerializers(serializers.ModelSerializer):
    medical_yearly_limit = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    employee_email = serializers.SerializerMethodField()
    class Meta:
        model = EmployeesMedicalAllowance
        fields = [
            'id',
            'employee',
            'employee_name',
            'employee_email',
            'medical_allowance',
            'medical_yearly_limit',
            'amount',
            'medical_receipt',
            'date',
            'status',
            'additional_comments',
            'is_active',
        ]

    def validate_medical_receipt(self, value):
        try:
            if value:
                max_size = 5 * 1024 * 1024
                if value.size > max_size:
                    raise serializers.ValidationError
            return value
        except serializers.ValidationError:
            raise serializers.ValidationError("File size cannot be greater than 5MB")
        except Exception as e:
            print(str(e))
            return None


    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None
        
    def get_employee_email(self, obj):
        try:
            return obj.employee.official_email
        except Exception as e:
            print(str(e))
            return None

    def get_medical_yearly_limit(self, obj):
        try:
            return obj.medical_allowance.yearly_limit
        except Exception as e:
            print(str(e))
            return None
        
class EmployeesRemainingMedicalAllowanceSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    emp_joining_date = serializers.SerializerMethodField()
    class Meta:
        model = EmployeesRemainingMedicalAllowance
        fields = [
            'id',
            'employee',
            'employee_name',
            'emp_joining_date',
            'medical_allowance',
            'remaining_allowance',
            'approved_amount',
            'inprogress_amount',
            'under_review_amount',
            'not_approved_amount',
            'emp_yearly_limit',
            'date',
            'is_active',
        ]

    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None
        
    def get_emp_joining_date(self, obj):
        try:
            return obj.employee.joining_date
        except Exception as e:
            print(str(e))
            return None
        

class MedicalStatusLogsSerializers(serializers.ModelSerializer):
    class Meta:
        model = MedicalStatusLogs
        fields = [
            'id',
            'employee_medical_allowance',
            'status',
            'decision_reason',
            'action_by',
            'action_on',
            'is_active',
        ]

class ProvidentFundsSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProvidentFunds
        fields = [
            'id',
            'organization',
            'percentage',
            'user',
            'is_active',

        ]

class EmployeeProvidentFundsSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_email = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()
    class Meta:
        model = EmployeeProvidentFunds
        fields = [
            'id',
            'employee',
            'employee_name',
            'employee_email',
            'provident_fund',
            'percentage',
            'date',
            'status',
            'decision_reason',
            'has_approval',
            'additional_comments',
            'is_active',
        ]
        
        read_only_fields = [
            'decision_reason',
        ]

    def get_percentage(self, obj):
        try:
            return obj.provident_fund.percentage
        except Exception as e:
            print(str(e))
            return None

    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None
        
    def get_employee_email(self, obj):
        try:
            return obj.employee.official_email
        except Exception as e:
            print(str(e))
            return None

class ProvidentFundStatusLogsSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProvidentFundStatusLogs
        fields = [
            'id',
            'employee_provident_fund',
            'status',
            'decision_reason',
            'action_by',
            'action_on',
            'is_active',
        ]

class EmployeesOfficialHolidaysSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeesOfficialHolidays
        fields = [
            'id',
            'title',
            'description',
            'organization',
            'date',
            'is_active',
        ]

class LeaveTypesSerializers(serializers.ModelSerializer):
    gender_classification_type=serializers.SerializerMethodField()
    class Meta:
        model = LeaveTypes
        fields = [
            'id',
            'title',
            'is_staff_classification',
            'gender_classification',
            'gender_classification_type',
            'tl_required',
            'organization',
            'is_active',
        ]
    def get_gender_classification_type(self, obj):
        try:
            return GENDER_Classification_CHOICES[obj.gender_classification-1][1]
        except Exception as e:
            print(e)
            return None

class UpdateLeaveTypesSerializers(serializers.ModelSerializer):
    class Meta:
        model = LeaveTypes
        fields = [
            'id',
            'title',
            'is_active',
        ]

class SetLeavesDurationSerializers(serializers.ModelSerializer):
    staff_classification_title = serializers.SerializerMethodField()
    leave_types_title = serializers.SerializerMethodField()
    class Meta:
        model = SetLeavesDuration
        fields = [
            'id',
            'leave_types',
            'staff_classification',
            'staff_classification_title',
            'leave_types_title',
            'allowed_leaves',
            'year',
            'is_lock',
            'lock_by',
            'is_active',
        ]

    def get_leave_types_title(self, obj):
        try:
            return obj.leave_types.title
        except Exception as e:
            print(str(e))
            return None

    def get_staff_classification_title(self, obj):
        try:
            return obj.staff_classification.title
        except Exception as e:
            print(str(e))
            return None


class ExcludeSCLeavesDurationSerializers(serializers.ModelSerializer):
    class Meta:
        model = SetLeavesDuration
        fields = [
            'id',
            'leave_types',
            'allowed_leaves',
            'year',
            'is_lock',
            'lock_by',
            'is_active',
        ]


class EmployeeLeaveDatesSerializers(serializers.ModelSerializer):
    leave_types_title=serializers.SerializerMethodField()
    class Meta:
        model = EmployeeLeaveDates
        fields = [
            'employee_leave',
            'leave_types_title',
            'date',
            'is_active',
        ]
    def get_leave_types_title(self, obj):
        try:
            if obj.employee_leave.leave_types is not None:
                return obj.employee_leave.leave_types.title
            else:
                return None
        except Exception as e:
            print(str(e))
            return None

class RecordEmployeesLeavesSerializers(serializers.ModelSerializer):

    employee_leave_dates=serializers.SerializerMethodField()
    month=serializers.SerializerMethodField()
    leave_types_title= serializers.SerializerMethodField()
    
    
    class Meta:
        model = EmployeesLeaves
        fields = [
            'id',
            'employee',
            'reason',
            'start_date',
            'leave_types',
            'leave_types_title',
            'end_date',
            'duration',
            'month',
            'status',
            'attachment',
            'decision_reason',
            'team_lead',
            'employee_leave_dates',
            'is_active',
        ]

        read_only_fields = [
            'decision_reason',
        ]

    
    def get_month(self, obj):
        try:
            if obj.start_date:
                # print(obj.start_date)
                return obj.start_date.month
            return None
        except Exception as e:
            print(str(e))
            return None
    
    
   

    def get_leave_types_title(self, obj):
        try:
            if obj.leave_types is not None:
                return obj.leave_types.title
            else:
                return None
        except Exception as e:
            print(str(e))
            return None


    
    def get_employee_leave_dates(self, obj):
        try:
            year=self.context.get('year')
            query = EmployeeLeaveDates.objects.filter(employee_leave=obj.id,date__year=year,is_active=True)
            serializers = EmployeeLeaveDatesSerializers(query, many=True)
            return serializers.data
        except Exception as e:
            print(str(e))
            return None


class UpdateEmployeesLeavesSerializers(serializers.ModelSerializer):
    allowed_leaves = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    employee_email = serializers.SerializerMethodField()
    leave_types_title = serializers.SerializerMethodField()
    staff_classification_title = serializers.SerializerMethodField()
    
    class Meta:
        model = EmployeesLeaves
        fields = [
            'id',
            'reason',
            'allowed_leaves',
            'employee_name',
            'employee_email',
            'leave_types_title',
            'staff_classification_title',
            'start_date',
            'end_date',
            'duration',
            'attachment',
            'team_lead',
            'decision_reason',
            'is_active',
        ]
    
        read_only_fields = [
            'decision_reason',
        ]


    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None
        
    def get_employee_email(self, obj):
        try:
            return obj.employee.official_email
        except Exception as e:
            print(str(e))
            return None

    def get_leave_types_title(self, obj):
        try:
            return obj.leave_types.title
        except Exception as e:
            print(str(e))
            return None

    def get_staff_classification_title(self, obj):
        try:
            return obj.employee.staff_classification.title
        except Exception as e:
            print(str(e))
            return None


    def get_allowed_leaves(self, obj):
        try:
            return obj.set_leave_duration.allowed_leaves
        except Exception as e:
            print(str(e))
            return None
        

class EmployeeLeaveCalculationsSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeeLeaveCalculations
        fields = [
            'employee',
            'set_leave_duration',
            'approved_leaves',
            'in_progress_leaves',
            'remaining_leaves',
            'underreview_leaves',
            'not_approved_leaves',
            'emp_yearly_leaves',
            'date',
            'is_active',
        ]

class ListEmployeeLeaveDateSerializers(serializers.ModelSerializer):
        # employee_name=serializers.SerializerMethodField()
        # employee_email=serializers.SerializerMethodField()
        staff_classification_title=serializers.SerializerMethodField()
        leave_data=serializers.SerializerMethodField()

        class Meta:
            model = Employees
            fields = [
            'id',
            'name',
            'official_email',
            'staff_classification_title', 
            'leave_data',          
            ]
            
     
        def get_staff_classification_title(self, obj):
            try:
                return obj.staff_classification.title
            except Exception as e:
                print(str(e))
                return None
            
        def get_leave_data(self, obj):
            try:
                # print(obj.id)
                year=self.context.get('year')
                # print('year',year)
                query = EmployeeLeaveCalculations.objects.filter(employee=obj.id,set_leave_duration__isnull=False,set_leave_duration__year=year,is_active=True)
                # print(query.values())
                data=[]
                for record in query:
                    if record.set_leave_duration.leave_types.is_staff_classification == True and record.set_leave_duration.staff_classification == obj.staff_classification:
                       data.append(record)
                    elif record.set_leave_duration.leave_types.is_staff_classification ==False:
                        data.append(record)

                serializers = ListEmployeeLeaveCalculationsSerializers(data,context={"year":year}, many=True)
                return serializers.data
                
            except Exception as e:
                print(str(e))
                return None
            

class ListEmployeeLeaveCalculationsSerializers(serializers.ModelSerializer):
    employee_leave_records=serializers.SerializerMethodField()
    leave_types=serializers.SerializerMethodField()

    class Meta:
        model = EmployeeLeaveCalculations
        fields = [
            'set_leave_duration',
            'leave_types',
            'approved_leaves',
            'in_progress_leaves',
            'remaining_leaves',
            'underreview_leaves',
            'not_approved_leaves',
            'emp_yearly_leaves',
            'date',
            'is_active',
            'employee_leave_records',
        ]

    def get_leave_types(self,obj):
        try:
          
           if obj.set_leave_duration is not None and obj.set_leave_duration.leave_types is not None:
                # print(obj.set_leave_duration.leave_types.id)
                return obj.set_leave_duration.leave_types.id
           else:
                return None
        
        except Exception as e:
            print(str(e))
            return None
        


    def get_employee_leave_records(self, obj):
        try:
            # print(obj.employee.id)
            if obj.set_leave_duration is not None and obj.set_leave_duration.leave_types is not None:
                year=self.context.get('year')
                query = EmployeesLeaves.objects.filter(employee=obj.employee.id,leave_types=obj.set_leave_duration.leave_types.id,start_date__year=year,is_active=True)
                serializers = RecordEmployeesLeavesSerializers(query,context={
                    'year':year,
                }, many=True)
                return serializers.data
            # return None
            else:
                return None
            
        except Exception as e:
            # print(str(e))
            return None
        



class EmployeesLeavesSerializers(serializers.ModelSerializer):
    allowed_leaves = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    employee_email = serializers.SerializerMethodField()
    leave_types_title = serializers.SerializerMethodField()
    staff_classification_title = serializers.SerializerMethodField()
    month = serializers.SerializerMethodField()
    employee_leave_dates = serializers.SerializerMethodField()
    emp_yearly_leaves = serializers.SerializerMethodField()
    # remaining_leaves = serializers.SerializerMethodField()
    class Meta:
        model = EmployeesLeaves
        fields = [
            'id',
            'employee',
            'employee_name',
            'employee_email',
            'leave_types',
            'leave_types_title',
            'staff_classification_title',
            'set_leave_duration',
            'allowed_leaves',
            'reason',
            'start_date',
            'end_date',
            'duration',
            'month',
            'status',
            'attachment',
            'team_lead',
            'decision_reason',
            'employee_leave_dates',
            'is_active',
            'emp_yearly_leaves',
            # 'remaining_leaves',
        ]

        read_only_fields = [
            'decision_reason',
        ]

    def get_month(self, obj):
        try:
            if obj.start_date:
                return obj.start_date.month
            return None
        except Exception as e:
            print(str(e))
            return None
    
    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None
        
    def get_employee_email(self, obj):
        try:
            return obj.employee.official_email
        except Exception as e:
            print(str(e))
            return None

    def get_leave_types_title(self, obj):
        try:
            return obj.leave_types.title
        except Exception as e:
            print(str(e))
            return None

    def get_staff_classification_title(self, obj):
        try:
            return obj.employee.staff_classification.title
        except Exception as e:
            print(str(e))
            return None
        
    def get_employee_leave_dates(self, obj):
        try:
            query = EmployeeLeaveDates.objects.filter(employee_leave=obj.id, is_active=True)
            serializers = EmployeeLeaveDatesSerializers(query, many=True)
            return serializers.data
        except Exception as e:
            print(str(e))
            return None


    def get_allowed_leaves(self, obj):
        try:
            return obj.set_leave_duration.allowed_leaves
        except Exception as e:
            print(str(e))
            return None
        
    def get_emp_yearly_leaves(self, obj):
        try:
            employee_leave_calculation = EmployeeLeaveCalculations.objects.get(
                employee=obj.employee,
                set_leave_duration=obj.set_leave_duration,
            )
            return employee_leave_calculation.emp_yearly_leaves  # Replace emp_yearly_leaves with the actual field name
        except EmployeeLeaveCalculations.DoesNotExist:
            # Handle the case when the related EmployeeLeaveCalculations instance does not exist
            return None
        except Exception as e:
            print(str(e))
            return None
        
   

     
    # def get_remaining_leaves(self, obj):

    #   try:
    #         pass
    #         # print(employee_leave_calculation.remaining_leaves)
     
    #   except Exception as e:
    #         print(str(e))
    #         return None
      



# class DashboardCountEmployeeLeaveCalculationsSerializers(serializers.ModelSerializer):
#     leave_type_title = serializers.SerializerMethodField()
#     leave_type_id = serializers.SerializerMethodField()
#     allowed_leaves=serializers.SerializerMethodField()
#     remaing_leaves=serializers.SerializerMethodField()
#     class Meta:
#         model = EmployeeLeaveCalculations
#         fields = [
            
#             'leave_type_title',
#             'leave_type_id',
#             'allowed_leaves',
#             'remaing_leaves',

         
#         ]

#     def get_leave_type_title(self, obj):
#      try:
#         return obj.set_leave_duration.leave_types.title
#      except Exception as e:
#             print(str(e))
#             return None
    
#     def get_leave_type_id(self, obj):
#        try:
#         return obj.set_leave_duration.leave_types_id
#        except Exception as e:
#             print(str(e))
#             return None
    
#     def get_leave_type_id(self, obj):
#      try:
#         return obj.set_leave_duration.leave_types.allowed_leaves
#      except Exception as e:
#             print(str(e))
#             return None
     
#     def get_leave_durations(self, obj):
#      try:
#       if obj.set_leave_duration.employeesleaves.status=="approved":
#          res= obj.set_leave_duration.leave_types.allowed_leaves - obj.set_leave_duration.employeesleaves.duration
#          if res<0:
#              res=0
#          return res
#      except Exception as e:
#             print(str(e))
#             return None
    
    

class LeavesStatusLogsSerializers(serializers.ModelSerializer):
    class Meta:
        model = LeavesStatusLogs
        fields = [
            'id',
            'employee_leave',
            'status',
            'decision_reason',
            'action_by',
            'action_on',
            'is_active',
        ]  

# loan serializers

class LoanTypesSerializers(serializers.ModelSerializer):
    class Meta:
        model = LoanTypes
        fields = [
            'id',
            'title',
            'organization',
            'is_active',
        ]

class TimeFrequencySerializers(serializers.ModelSerializer):
    class Meta:
        model = TimeFrequency
        fields = [
            'id',
            'organization',
            'title',
            'is_active'
        ]

class TimePeriodSerializers(serializers.ModelSerializer):
    time_frequency_title = serializers.SerializerMethodField()
    class Meta:
        model = TimePeriod
        fields = [
            'id',
            'time_frequency',
            'time_frequency_title',
            'start_month',
            'end_month',
            'is_active',
        ]

    def get_time_frequency_title(self, obj):
        try:
            return obj.time_frequency.title
        except Exception as e:
            print(str(e))
            return None


class ListSetLoanRequirementsSerializers(serializers.ModelSerializer):
    loan_type_title = serializers.SerializerMethodField()
    time_frequency_title = serializers.SerializerMethodField()
    time_period_data = serializers.SerializerMethodField()
    class Meta:
        model = SetLoanRequirements
        fields = [
            'id',
            'loan_type',
            'loan_type_title',
            'organization_cap_amount',
            'emp_salary_factor',
            'max_individual_loan_limit',
            'time_frequency',
            'time_frequency_title',
            'time_period_data',
            'emp_min_service_duration',
            'is_provident_fund',
            'min_provident_fund_duration',
            'is_limit_exhausted',
            'is_lock',
            'lock_by',
            'locked_date',
            'unlock_by',
            'unlocked_date',
            'is_active',
        ]

    def get_loan_type_title(self, obj):
        try:
            return obj.loan_type.title
        except Exception as e:
            print(str(e))
            return None
        
    def get_time_frequency_title(self, obj):
        try:
            return obj.time_frequency.title
        except Exception as e:
            print(str(e))
            return None
        
    def get_time_period_data(self, obj):
        try:
            query = TimePeriod.objects.filter(time_frequency=obj.time_frequency, is_active=True)
            serializer = TimePeriodSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            print(str(e))
            return None



class SetLoanRequirementsSerializers(serializers.ModelSerializer):
    loan_type_title = serializers.SerializerMethodField()
    time_frequency_title = serializers.SerializerMethodField()
    class Meta:
        model = SetLoanRequirements
        fields = [
            'id',
            'loan_type',
            'loan_type_title',
            'organization_cap_amount',
            'emp_salary_factor',
            'max_individual_loan_limit',
            'time_frequency',
            'time_frequency_title',
            'emp_min_service_duration',
            'is_provident_fund',
            'min_provident_fund_duration',
            'is_active',
        ]

    def get_loan_type_title(self, obj):
        try:
            return obj.loan_type.title
        except Exception as e:
            print(str(e))
            return None
        
    def get_time_frequency_title(self, obj):
        try:
            return obj.time_frequency.title
        except Exception as e:
            print(str(e))
            return None
        

class UpdateSetLoanRequirementsSerializers(serializers.ModelSerializer):
    loan_type_title = serializers.SerializerMethodField()
    time_frequency_title = serializers.SerializerMethodField()
    class Meta:
        model = SetLoanRequirements
        fields = [
            'id',
            'loan_type',
            'loan_type_title',
            'organization_cap_amount',
            'emp_salary_factor',
            'max_individual_loan_limit',
            'time_frequency',
            'time_frequency_title',
            'emp_min_service_duration',
            'is_provident_fund',
            'min_provident_fund_duration',
            'is_active',
        ]
    
    def get_loan_type_title(self, obj):
        try:
            return obj.loan_type.title
        except Exception as e:
            print(str(e))
            return None
        
    def get_time_frequency_title(self, obj):
        try:
            return obj.time_frequency.title
        except Exception as e:
            print(str(e))
            return None


class PurposeOfLoansSerializers(serializers.ModelSerializer):
    class Meta:
        model = PurposeOfLoans
        fields = [
            'id',
            'title',
            'organization',
            'is_active',
        ]

class EmployeesLoanSerializers(serializers.ModelSerializer):
    purpose_of_loan_title = serializers.SerializerMethodField()
    loan_type_title = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    employee_email = serializers.SerializerMethodField()
    class Meta:
        model = EmployeesLoan
        fields = [
            'id',
            'employee',
            'set_loan_requirement',
            'purpose_of_loan',
            'purpose_of_loan_title',
            'employee_name',
            'employee_email',
            'loan_type',
            'loan_type_title',
            'number_of_loan_installment',
            'priority',
            'amount',
            'reason',
            'loan_start_date',
            'loan_end_date',
            'status',
            'decision_reason',
            'is_active',
        ]
    
        read_only_fields = [
            'decision_reason',
        ]

    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None

    def get_employee_email(self, obj):
        try:
            return obj.employee.official_email
        except Exception as e:
            print(str(e))
            return None

    def get_loan_type_title(self, obj):
        try:
            return obj.loan_type.title
        except:
            return None
        
    def get_purpose_of_loan_title(self, obj):
        try:
            return obj.purpose_of_loan.title
        except:
            return None

class UpdateEmployeesLoanSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeesLoan
        fields = [
            'id',
            'number_of_loan_installment',
            'purpose_of_loan',
            'amount',
            'reason',
            'loan_start_date',
            'status',
            'is_active',
        ]

class LoanStatusLogsSerializers(serializers.ModelSerializer):
    class Meta:
        model = LoanStatusLogs
        fields = [
            'id',
            'employee_loan',
            'status',
            'decision_reason',
            'action_by',
            'action_on',
            'is_active',
        ]

class ScriptStatusLogsSerializers(serializers.ModelSerializer):
    class Meta:
        model=ScriptStatusLogs
        fields = ['id','employee','script_title','staff_classification','script_type', 'is_completed','year','action_by','is_active', 'created_at', 'updated_at']

class CompensatoryLeavesSerializer(serializers.ModelSerializer):
    team_lead_name = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CompensatoryLeave
        fields = '__all__'
        
    def get_team_lead_name(self, obj):
        try:
            return obj.team_lead.name
        except:
            return None
        
    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except:
            return None

class ListEmployeePendingLeaveSerializer(serializers.ModelSerializer):
    leave_types_title= serializers.SerializerMethodField()
    employee_name=serializers.SerializerMethodField()
    class Meta:
        model = EmployeesLeaves
        fields = [
            'id',
            'employee',
            'employee_name',
            'leave_types',
            'leave_types_title',
            'start_date',
            'end_date',
            'duration',
            'status',
            'is_active',
        ]
    
    def get_employee_name(self, obj):
        try:
            if obj.employee:
                # print(obj.start_date)
                return obj.employee.name
            return None
        except Exception as e:
            print(str(e))
            return None
    
    
   

    def get_leave_types_title(self, obj):
        try:
            if obj.leave_types is not None:
                return obj.leave_types.title
            else:
                return None
        except Exception as e:
            print(str(e))
            return None
            
class ListEmployeesPendingMedicalAllowanceSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    class Meta:
        model = EmployeesMedicalAllowance
        fields = [
            'id',
            'employee',
            'employee_name',
            'medical_allowance',
            'amount',
            'medical_receipt',
            'date',
            'status',
            'is_active',
        ]
        
        read_only_fields = [
            'decision_reason',
        ]

    def validate_medical_receipt(self, value):
        try:
            if value:
                max_size = 5 * 1024 * 1024
                if value.size > max_size:
                    raise serializers.ValidationError
            return value
        except serializers.ValidationError:
            raise serializers.ValidationError("File size cannot be greater than 5MB")
        except Exception as e:
            print(str(e))
            return None


    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None
        
class ListEmployeesPendingGymAllowanceSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    class Meta:
        model = EmployeesGymAllowance
        fields = [
            'id',
            'employee',
            'employee_name',
            'amount',
            'gym_receipt',
            'date',
            'status',
            'is_active',
        ]

        read_only_fields = [
            'decision_reason',
        ]
    
    def validate_gym_receipt(self, value):
        try:
            if value:
                max_size = 5 * 1024 * 1024
                if value.size > max_size:
                    raise serializers.ValidationError
            return value
        except serializers.ValidationError:
            raise serializers.ValidationError("File size cannot be greater than 5MB")
        except Exception as e:
            print(str(e))
            return None

  

    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None
        
        
        
      
class DashboardEmployeesLeavesSerializers(serializers.ModelSerializer):
    profile_image=serializers.SerializerMethodField()
    employee_name=serializers.SerializerMethodField()
    employee_uuid=serializers.SerializerMethodField()
    employee=serializers.SerializerMethodField()
    leave_type=serializers.SerializerMethodField()
    leave_type_title=serializers.SerializerMethodField()
    department_title=serializers.SerializerMethodField()
    position_title=serializers.SerializerMethodField()
    
    class Meta:
        model = EmployeeLeaveDates
        fields = [
            'id',
            'employee',
            'employee_name',
            'employee_uuid',
            'profile_image',
            'department_title',
            'position_title',
            'date',
            'employee_leave',
            'leave_type',
            'leave_type_title',
            'is_active',
        ]
        
    def get_employee_name(self, obj):
        try:
            return obj.employee_leave.employee.name
        except Exception as e:
            print(str(e))
            return None
        
    def get_position_title(self, obj):
        try:
            return obj.employee.position.title
        except Exception as e:
            print(str(e))
            return None
        
    def get_department_title(self, obj):
        try:
            return obj.employee.department.title
        except Exception as e:
            print(str(e))
            return None
        
    def get_employee(self, obj):
        try:
            return obj.employee_leave.employee.id
        except Exception as e:
            print(str(e))
            return None
        
    def get_employee_uuid(self, obj):
        try:
            return obj.employee_leave.employee.uuid
        except Exception as e:
            print(str(e))
            return None
        
    def get_leave_type(self, obj):
        try:
            return obj.employee_leave.leave_type
        except Exception as e:
            print(str(e))
            return None
        
    def get_leave_type_title(self, obj):
        try:
            return obj.employee_leave.leave_type
        except Exception as e:
            print(str(e))
            return None
        
    def get_profile_image(self, obj):
        try:
            # organization_id = self.context.get('organization_id')
            if obj.created_by.is_admin:
                return obj.created_by.profile_image.url
            
            query=Employees.objects.filter(hrmsuser=obj.created_by.id,is_active=True)
            if not query.exists():
                return None
            obj=query.get()
            return obj.profile_image.url
        except Exception as e:
            print(str(e))
            return None        
        


class EmployeeWFHAllowanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeesWFHAllowance
        fields = [
            'id',                
            'employee',
            'organization',
            'limit',
            'comment',
            'created_by',
            'is_active',
            'created_at',
            'updated_at'
        ]

class EmployeesWFHRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    dates=serializers.SerializerMethodField()
    class Meta:
        model = EmployeesWFHRequest
        fields = [
            'id',
            'employee',
            'employee_name',
            # 'status',
            # 'approved_by',
            # 'approval_date',
            'comment',
            'created_by',
            'is_active',
            'created_at',
            'updated_at',
            'dates',
        ]

    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None
        
    def get_dates(self,obj):
        try:
            query=EmployeesWFHRequestDates.objects.filter(employee_wfh_request=obj.id,is_active=True)
            serializers=EmployeesWFHRequestDatesSerializers(query,many=True)
            return serializers.data
        except Exception as e:
            return None
        
class EmployeesWFHRequestDatesSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeesWFHRequestDates
        fields = [
            'employee_wfh_request',
            'date',
            'is_active',
        ]
