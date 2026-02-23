import calendar
from rest_framework import viewsets
from .serializers import (
    LeaveTypesSerializers, ListEmployeePendingLeaveSerializer, ScriptStatusLogsSerializers, UpdateLeaveTypesSerializers, SetLeavesDurationSerializers,
    EmployeesLeavesSerializers, UpdateEmployeesLeavesSerializers, ExcludeSCLeavesDurationSerializers,
    LeavesStatusLogsSerializers, EmployeeLeaveDatesSerializers, EmployeeLeaveCalculationsSerializers,
    EmployeesOfficialHolidaysSerializers, ListEmployeeLeaveCalculationsSerializers,ListEmployeeLeaveDateSerializers, CompensatoryLeavesSerializer
)
from .models import (
    LeaveTypes, ScriptStatusLogs, SetLeavesDuration, EmployeesLeaves, LeavesStatusLogs, MedicalAllowance,
    EmployeesOfficialHolidays, EmployeeLeaveDates, EmployeeLeaveCalculations,EmployeesRemainingMedicalAllowance, CompensatoryLeave
)
from email_templates.models import EmailRecipients
from helpers.status_messages import ( 
    exception, errorMessage, serializerError, successMessageWithData,
    success, successMessage, successfullyCreated, successfullyUpdated,errorMessageWithData
)
from employees_attendance.models import EmployeesAttendanceLabel
from helpers.decode_token import decodeToken
from helpers.email_data import requestEmailsFromEmployees, requestDecisionFromManagement,LeaveRequestEmailsFromEmployees,SimpleLeaveRequestEmailsFromEmployees,requestEmailsFromEmployeesnontl
from helpers.custom_permissions import IsAuthenticated, IsEmployeeOnly,IsAdminOnly
from organizations.models import StaffClassification
from employees.models import Employees, EmployeeTypes
import datetime
import math
import pandas as pd
import os
from .Scriptinglogs import script_logs


from django.db.models import Q

class EmployeesOfficialHolidaysViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EmployeesOfficialHolidays.objects.all()
    serializer_class = EmployeesOfficialHolidaysSerializers

    def get_queryset(self):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            return self.queryset.filter(organization=organization_id)
        except Exception as e:
            print(str(e))
            return None

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset().filter(is_active=True)
            serializer = self.get_serializer(queryset, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def upcoming_holidays(self,organization_id):
        try:
            current_date=datetime.datetime.today().date()
            queryset = EmployeesOfficialHolidays.objects.filter(organization=organization_id,date__gte=current_date,is_active=True)
            serializer = EmployeesOfficialHolidaysSerializers(queryset, many=True)
            return serializer.data
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
            organization_id = decodeToken(self, request)['organization_id']
            request.data['organization'] = organization_id
            
            if not 'date' in request.data:
                return errorMessage('Date is a required Field')
            if not 'title' in request.data:
                return errorMessage('Title is a required Field')
            
            date = request.data['date']
            
            query = self.get_queryset().filter(date=date, is_active=True)
            if query.exists():
                return errorMessage('Holiday already exists against this date')          

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
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('No Leave Type exists at this id')

            obj = query.get()
            # print(request.data)
            # if 'date' in request.data:
            #     date = request.data['date']
            #     print("date:",date)
            #     print("title:",request.data['title'])
                # if obj.date != date:
                #     queryset = self.get_queryset().filter(date=date, is_active=True)
                    # print("Test:",queryset)
                    # if queryset.exists():
                    #     return errorMessage('Holiday already exists against this date')   
            
            serializer = self.serializer_class(obj, data = request.data, partial=True)

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
                return errorMessage('Does not exists at this id')
            if not query.filter(is_active=True):
                return errorMessage('Deactivated at this id')
            
            obj = query.get()
            date = obj.date
            emp_leaves = EmployeeLeaveDates.objects.filter(date=date, is_active=True)
            if emp_leaves.exists():
                return errorMessage('Employees leaves exists against this holiday')

            obj.is_active = False
            obj.save()
            return successMessage('Sucessfully deactivated')
        except Exception as e:
            return exception(e)
        

class LeaveTypesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = LeaveTypes.objects.all()
    serializer_class = LeaveTypesSerializers

    def get_queryset(self):
        organization_id = decodeToken(self, self.request)['organization_id']
        return self.queryset.filter(organization=organization_id)

    def list(self, request, *args, **kwargs):
        try:
            obj = self.get_queryset().filter(is_active=True)
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
            organization_id = decodeToken(self, request)['organization_id']
            request.data['organization'] = organization_id

            if 'is_staff_classification' not in request.data:
                return errorMessage('is_staff_classification is a required field')
            
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
            leave_type = self.get_queryset().filter(id=pk)
            if not leave_type.exists():
                return errorMessage('No Leave Type exists at this id')

            obj = leave_type.get()
    
            serializer = UpdateLeaveTypesSerializers(obj, data = request.data, partial=True)

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
                return errorMessage('No leave exists at this id')
            if not query.filter(is_active=True):
                return errorMessage('Leave is deactivated at this id')
            
            obj = query.get()
            obj.is_active = False
            obj.save()
            return successMessage('Sucessfully deactivated')
        except Exception as e:
            return exception(e)

    def get_pre_data(self, organization_id,year=None):
        try:
            query = LeaveTypes.objects.filter(organization=organization_id,created_at__year=year, is_active=True).order_by('id')
            serializer = LeaveTypesSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            return None

class SetLeavesDurationViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = SetLeavesDuration.objects.all()
    serializer_class = SetLeavesDurationSerializers

    def get_queryset(self):
        organization_id = decodeToken(self, self.request)['organization_id']
        return self.queryset.filter(leave_types__organization=organization_id)

    def list(self, request, *args, **kwargs):
        try:
            obj = self.get_queryset().filter(is_active=True)
            serializer = self.serializer_class(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def retrieve(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('Does not exists')
            elif not query.filter(is_active=True).exists():
                return errorMessage('Deactivated at this id')

            obj = query.get()
            serializer = self.serializer_class(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']

            # if not request.user.is_privileged:
            #     return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 

            required_fields = ['leave_types', 'allowed_leaves']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [leave_types, allowed_leaves]')
            
            already_exists_data=[]
            data=[]
            current_year =datetime.datetime.today().year
            next_year = current_year + 1

            years=[current_year]

            leave_type_id = request.data['leave_types']
            leave = LeaveTypes.objects.filter(id=leave_type_id, organization=organization_id)
            if not leave.exists():
                    return errorMessage('This leave type does not exists')

            for year in years:
                
                leave_obj = leave.get()
                request.data['leaves_type'] = leave_obj.id
                
                is_staff_classification_based = leave_obj.is_staff_classification
                if is_staff_classification_based == None:
                    return errorMessage('You need to set is_staff_classification first in leave types')

                if 'is_lock' in request.data:
                    is_lock = request.data['is_lock']
                    if is_lock:
                        request.data['lock_by'] = request.user.id

                if is_staff_classification_based == False:
                    # title = leave_obj.title 
                    # if title == 'Annual Leaves':
                    #     return errorMessage('Annual leaves are staff classification based')
                    
                    if self.get_queryset().filter(year=year,leave_types=leave_obj, is_active=True).exists():
                        # return errorMessage('Data already exists against this leave type in given year')
                        already_exists_data.append(year)
                        continue

                    request.data['year']=year
                    
                    serializer = ExcludeSCLeavesDurationSerializers(data = request.data)
                    if not serializer.is_valid():
                        return serializerError(serializer.errors)
                    serializer.save()
                    data.append(serializer.data)

                        
                else:
                    staff_classification_id = request.data.get('staff_classification', None)
                    check_staff_classification = self.check_staff_classification(staff_classification_id, organization_id)
                    if check_staff_classification['status'] == 400:
                        return errorMessage(check_staff_classification['message'])
                    
                    request.data['staff_classification'] = staff_classification_id
                    if self.get_queryset().filter(staff_classification=staff_classification_id,year=year,leave_types=leave_obj, is_active=True).exists():
                        already_exists_data.append(year)
                        continue
                    
                    request.data['year']=year
                    
                    serializer = self.serializer_class(data = request.data)
                
                    if not serializer.is_valid():
                        return serializerError(serializer.errors)
                    serializer.save()
                    data.append(serializer.data)

            
            if already_exists_data:
                    return errorMessage("Year limit already set")

            return successMessageWithData("Success",data)
        except Exception as e:
            return exception(e)


    def patch(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            pk = self.kwargs['pk']
            leave = self.get_queryset().filter(id=pk)
            if not leave.exists():
                return errorMessage('No Leave exists at this id')

            obj = leave.get()
            
            is_lock = obj.is_lock
            if is_lock:
                return errorMessage("Leaves are locked. It cannot get updated now")
            
            if 'is_lock' in request.data:
                is_lock = request.data['is_lock']
                if is_lock:
                    request.data['lock_by'] = request.user.id

            is_staff_classification_based = obj.leave_types.is_staff_classification
            request.data['leave_types'] = obj.leave_types.id

            if is_staff_classification_based == True:
                if 'staff_classification' in request.data:
                    staff_classification_id = request.data['staff_classification']
                    check_staff_classification = self.check_staff_classification(staff_classification_id, organization_id)
                    if check_staff_classification['status'] == 400:
                        return errorMessage(check_staff_classification['message'])
                    request.data['staff_classification'] = staff_classification_id
                else:
                    staff_classification_id = obj.staff_classification.id

                if self.get_queryset().filter(staff_classification=staff_classification_id, leave_types=obj.leave_types.id, is_active=True).exclude(id=pk).exists():
                    return errorMessage('Already data exists against this staff classification')
                serializer = self.serializer_class(obj, data=request.data, partial=True)

            elif is_staff_classification_based == False:
                if self.get_queryset().filter(leave_types=obj.leave_types, is_active=True).exclude(id=pk).exists():
                    return errorMessage('Already data exists. Deactivate it first')
                serializer = ExcludeSCLeavesDurationSerializers(obj, data=request.data, partial=True)
           
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
                return errorMessage('No Leave exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('Leave is deactivated at this id')
            elif query.filter(is_lock=True):
                return errorMessage('It is locked. It cannot get deactivate. Please unlock it first')
            
            obj = query.get()
            obj.is_active = False
            obj.save()
            return successMessage('Sucessfully deactivated')
        except Exception as e:
            return exception(e)
        
    def patch_unlock_leave(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('No Leave exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('Leave is deactivated at this id')
            elif query.filter(is_lock=False):
                return errorMessage('It is already unlocked. Lock it first')
            
            obj = query.get()

            staff_classification = obj.staff_classification
            if staff_classification:
                staff_classification = staff_classification.id

            data_dict = {
                'leave_types': obj.leave_types.id,
                'staff_classification': staff_classification,
                'allowed_leaves': obj.allowed_leaves,
                'is_lock': False,
                'is_active': obj.is_active,
            }

            serializer = self.serializer_class(data = data_dict)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()

            obj.is_active = False
            obj.save()
            return successMessageWithData('Successfully unlocked', serializer.data)
        except Exception as e:
            return exception(e)
    
    def get_pre_data(self, organization_id):
        try:
            
            year=datetime.datetime.today().year
            query = SetLeavesDuration.objects.filter(leave_types__organization=organization_id,year=year,is_active=True).order_by('-id')
            serializer = SetLeavesDurationSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            return None

    def check_staff_classification(self, staff_classification_id, organization_id):
        try:
            result = {'status': 400, 'message': None, 'system_error_message': None}     

            if staff_classification_id == None:
                result['message'] = 'Staff classification is the required field'
                return result
            
            staff_classification = StaffClassification.objects.filter(id=staff_classification_id, organization=organization_id)
            if not staff_classification.exists():
                result['message'] = 'Staff classification does not exists'
                return result
            elif not staff_classification.filter(is_active=True).exists():
                result['message'] = 'Staff classification is deactivated'
                return result
            
            result['status'] = 200
            return result
        except Exception as e:
            result['message'] = 'Exception Handling'
            result['system_error_message'] = str(e)
            return result

class NewEmployeeLeaveNSCAllowanceViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsAdminOnly]  
    queryset = EmployeeLeaveCalculations.objects.all()
    serializer_class = EmployeeLeaveCalculationsSerializers

    def NewEmployeeNSCLeaveSet(self, request, *args, **kwargs):
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
            # print(current_date)
            employee=Employees.objects.filter(organization_id=organization_id,is_active=True)
            for emp in employee:

                if emp.staff_classification_id is not None:
                    # print(emp.id)
                    # print(emp.staff_classification_id)

                    leave_duration = SetLeavesDuration.objects.filter(Q(leave_types__gender_classification=emp.gender )|Q(leave_types__gender_classification=3),staff_classification__isnull=True,year=year,leave_types__organization=organization_id,is_active=True)
                    
                    # print(leave_duration.values())
                    for ld in leave_duration:

                        if ld.leave_types.title=="Compensatory Leaves":
                            continue
                        
                        # print(ld.leave_types.title)
                        query = EmployeeLeaveCalculations.objects.filter(
                            employee=emp.id, 
                            set_leave_duration=ld.id, 
                            is_active=True
                        )
                        in_progress_leaves = 0
                        under_review_leaves=0 
                        approved_leaves= 0
                        not_approved_leaves = 0
                        remaining_leaves_count=0

                        if not query.exists():
                            
                            # print(emp.joining_date)

                            if emp.joining_date:
                                joining_year = emp.joining_date.year
                                # print(emp.joining_date)

                                if joining_year < year:
                                    emp_yearly_leaves_count=ld.allowed_leaves
                                    remaining_leaves_count=ld.allowed_leaves

                        
                                else:
                                    joining_month = emp.joining_date.month - 1
                                    # Calculate remaining months in the year
                                    remaining_months = 12 - joining_month
                                    
                                    count=round(ld.allowed_leaves/12 * remaining_months)
                                    print(count)

                                    emp_yearly_leaves_count=count
                                    remaining_leaves_count=count
                        
                            else:
                                not_found_data.append([emp.id,emp.name,"Joining Data is missing"]) 
                                continue

                        else:
                            instance_to_update = query.first()
                            if emp.joining_date:
                                joining_year = emp.joining_date.year
                                
                                # print(emp.joining_date)
                                if joining_year < year:
                                    emp_yearly_leaves_count=ld.allowed_leaves
                                    remaining_leaves_count=ld.allowed_leaves

                        
                                else:
                                    joining_month = emp.joining_date.month - 1
                                    # Calculate remaining months in the year
                                    remaining_months = 12 - joining_month
                                    
                                    count=round(ld.allowed_leaves/12 * remaining_months)
                                    # print(count)

                                    emp_yearly_leaves_count=count
                                    remaining_leaves_count=count

                                approved_leaves = instance_to_update.approved_leaves
                                new_remaining_leaves_count=emp_yearly_leaves_count-approved_leaves
                                leave_type_title=instance_to_update.set_leave_duration.leave_types.title
                                # print(new_remaining_leaves_count)
                                # print(leave_type_title)
                                if new_remaining_leaves_count<0:
                                    
                                    leave_type_title=instance_to_update.set_leave_duration.leave_types.title
                                    not_found_data.append([emp.id,emp.name,f"Negative leave balance occurs against {leave_type_title} and value is {new_remaining_leaves_count}"])
                                    new_remaining_leaves_count=0
                                    # continue
                                
                                instance_to_update.remaining_leaves=new_remaining_leaves_count
                                instance_to_update.emp_yearly_leaves=emp_yearly_leaves_count
                                instance_to_update.save()
                                # print("Test")
                                continue

                            else:
                                not_found_data.append([emp.id,emp.name,"Joining Data is missing"]) 
                                continue


                        leaves_calculation_data = {
                            'employee':emp.id,
                            'set_leave_duration':ld.id,
                            'in_progress_leaves': in_progress_leaves,
                            'remaining_leaves': remaining_leaves_count,
                            'approved_leaves': approved_leaves,
                            'not_approved_leaves': not_approved_leaves,
                            'underreview_leaves': under_review_leaves,
                            'emp_yearly_leaves':emp_yearly_leaves_count,
                            "date":current_date,
                            "is_active":1
                        }
                        # print(leaves_calculation_data) 
                        serializer = EmployeeLeaveCalculationsSerializers(data=leaves_calculation_data)
                        if not serializer.is_valid():
                            result['message'] = serializer.errors
                            return serializerError(serializer)
                                
                        serializer = serializer.save()
                        # print("test1")

                            
                else:
                     not_found_data.append([emp.id,emp.name,"staff_classification_id is missing"])
                     continue
            print('employee process completed')
            if not_found_data:
                directory_path = 'C:\\Users\\Kavtech\\Downloads'
                file_name = 'employees_not_found_leaves_nsc.csv'
                file_path = os.path.join(directory_path, file_name)
                # Create the directory if it doesn't exist
                if not os.path.exists(directory_path):
                    os.makedirs(directory_path)
                not_found_df = pd.DataFrame(not_found_data, columns=['Emp_id','Emp_Name', 'Message'])
                not_found_df.to_csv(file_path, index=False)
            # result['data'] = serializer.data
            result['status'] = 200
            result['message'] = 'Success'
            return successMessage('success')
        except Exception as e:
            result['message'] = e
            return errorMessage(e)

    def allow_emp_nsc_leaves(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            user_id=request.user.id

            organization_id = token_data['organization_id']
            pk=self.kwargs['pk']

            year=request.data.get('year',None)
            if year is None:
               year=datetime.datetime.today().year
            # current_year = datetime.date.today().year
            current_date = datetime.date.today()
            # print(current_date)
            employee=Employees.objects.filter(id=pk,organization_id=organization_id,is_active=True)

            if not employee.exists():
                return errorMessage("Employee not exists at this id")
            emp=employee.get()
            serializer=None
            

            if emp.staff_classification is not None:
                    # print(emp.id)
                    # print(emp.staff_classification_id)

                    # leave_duration = SetLeavesDuration.objects.filter(staff_classification__isnull=True,year=year,leave_types__organization=organization_id,is_active=True)
                    leave_duration = SetLeavesDuration.objects.filter(Q(leave_types__gender_classification=emp.gender )|Q(leave_types__gender_classification=3),staff_classification__isnull=True,year=year,leave_types__organization=organization_id,is_active=True)
                    
                    if not leave_duration.exists():
                        return errorMessage("No non-staffclassififcation Leaves data exists")
                    
                    # print("OUT")
                    for ld in leave_duration:

                        if ld.leave_types.title=="Compensatory Leaves":
                            continue
                        
                        # print(ld.leave_types.title)
                        query = EmployeeLeaveCalculations.objects.filter(
                            employee=emp.id, 
                            set_leave_duration=ld.id, 
                            is_active=True
                        )
                        in_progress_leaves = 0
                        under_review_leaves=0 
                        approved_leaves= 0
                        not_approved_leaves = 0
                        remaining_leaves_count=0

                        if not query.exists():
                        
                            
                            if emp.joining_date:
                                joining_year = emp.joining_date.year
                                
                                # print(emp.joining_date)
                                if joining_year < year:
                                    emp_yearly_leaves_count=ld.allowed_leaves
                                    remaining_leaves_count=ld.allowed_leaves

                        
                                else:
                                    joining_month = emp.joining_date.month - 1
                                    # Calculate remaining months in the year
                                    remaining_months = 12 - joining_month
                                    
                                    count=round(ld.allowed_leaves/12 * remaining_months)
                                    # print(count)

                                    emp_yearly_leaves_count=count
                                    remaining_leaves_count=count
                        
                            else:
                                return errorMessage('Joining Data is missing')
                            
                        else:
                            continue

                     
                        # print("Out")
                        if remaining_leaves_count < 0:
                            remaining_leaves_count = 0

                        leaves_calculation_data = {
                            'employee':emp.id,
                            'set_leave_duration':ld.id,
                            'in_progress_leaves': in_progress_leaves,
                            'remaining_leaves': remaining_leaves_count,
                            'approved_leaves': approved_leaves,
                            'not_approved_leaves': not_approved_leaves,
                            'underreview_leaves': under_review_leaves,
                            'emp_yearly_leaves':emp_yearly_leaves_count,
                            "date":current_date,
                            "is_active":1
                        }
                        # print(ld.leave_types.title) 
                        serializer = EmployeeLeaveCalculationsSerializers(data=leaves_calculation_data)
                        if not serializer.is_valid():
                            return serializerError(serializer.errors)
                        
                        serializer = serializer.save() 


                    script_title="Non Staff Classification Leaves Script"
                    script_type=2
                    status=1
                    staff_classification=None

                    output = script_logs(pk,staff_classification,script_title,script_type,year,status,user_id)
                            # print(output)
                    if output['status'] == 400:
                                    return errorMessage(output['message'])
                        
                            
                    return successMessageWithData('success',output['data'])
                    
                   
                        
            else:
                    return errorMessage("staff_classification_id is missing")

        except Exception as e:
            return exception(e)

 
    





class NewEmployeeLeaveAllowanceViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsAdminOnly]  
    queryset = EmployeeLeaveCalculations.objects.all()
    serializer_class = EmployeeLeaveCalculationsSerializers

    def NewEmployeeLeaveSet(self, request, *args, **kwargs):
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

            

            # current_year = datetime.date.today().year
            current_date = datetime.date.today()
            # print(current_date)
            employee=Employees.objects.filter(organization_id=organization_id,is_active=True)
            for emp in employee:

                if emp.staff_classification_id is not None:
                    # print(emp.id)
                    # print(emp.staff_classification_id)

                    leave_duration = SetLeavesDuration.objects.filter(staff_classification=emp.staff_classification_id,year=year,is_active=True)
                    
                    # print("OUT")
                    for ld in leave_duration:
                        
                        # print(ld.leave_types.title)
                        query = EmployeeLeaveCalculations.objects.filter(
                            employee=emp.id, 
                            set_leave_duration=ld.id, 
                            is_active=True
                        )
                        in_progress_leaves = 0
                        under_review_leaves=0 
                        approved_leaves= 0
                        not_approved_leaves = 0
                        remaining_leaves_count=0

                        if not query.exists():
                        
                            
                            if emp.joining_date:
                                joining_year = emp.joining_date.year
                                
                                # print(emp.joining_date)
                                if joining_year < year:
                                    emp_yearly_leaves_count=ld.allowed_leaves
                                    remaining_leaves_count=ld.allowed_leaves

                        
                                else:
                                    joining_month = emp.joining_date.month - 1
                                    # Calculate remaining months in the year
                                    remaining_months = 12 - joining_month
                                    
                                    count=round(ld.allowed_leaves/12 * remaining_months)
                                    # print(count)

                                    emp_yearly_leaves_count=count
                                    remaining_leaves_count=count
                        
                            else:
                                not_found_data.append([emp.id,emp.name,"Joining Data is missing"]) 
                                continue

                        else:
                            # print(query.values())
                            # print("Else")
                            instance_to_update = query.first()
                            if emp.joining_date:
                                joining_year = emp.joining_date.year
                                
                                # print(emp.joining_date)
                                if joining_year < year:
                                    emp_yearly_leaves_count=ld.allowed_leaves
                                    remaining_leaves_count=ld.allowed_leaves

                        
                                else:
                                    joining_month = emp.joining_date.month - 1
                                    # Calculate remaining months in the year
                                    remaining_months = 12 - joining_month
                                    
                                    count=round(ld.allowed_leaves/12 * remaining_months)
                                    # print(count)

                                    emp_yearly_leaves_count=count
                                    remaining_leaves_count=count

                                approved_leaves = instance_to_update.approved_leaves
                                new_remaining_leaves_count=emp_yearly_leaves_count-approved_leaves
                                # print(approved_leaves)
                                
                                # print(leave_type_title)
                               
                                # print(leave_type_title)
                                if new_remaining_leaves_count<0:
                                    
                                    leave_type_title=instance_to_update.set_leave_duration.leave_types.title
                                    not_found_data.append([emp.id,emp.name,f"Negative leave balance occurs against {leave_type_title} and value is {new_remaining_leaves_count}"])
                                    new_remaining_leaves_count=0
                                    # continue
                                
                                instance_to_update.remaining_leaves=new_remaining_leaves_count
                                instance_to_update.emp_yearly_leaves=emp_yearly_leaves_count
                                instance_to_update.save()

                                continue

                            else:
                                not_found_data.append([emp.id,emp.name,"Joining Data is missing"]) 
                                continue

                        # print("Out")
                        if remaining_leaves_count < 0:
                            remaining_leaves_count = 0

                        leaves_calculation_data = {
                            'employee':emp.id,
                            'set_leave_duration':ld.id,
                            'in_progress_leaves': in_progress_leaves,
                            'remaining_leaves': remaining_leaves_count,
                            'approved_leaves': approved_leaves,
                            'not_approved_leaves': not_approved_leaves,
                            'underreview_leaves': under_review_leaves,
                            'emp_yearly_leaves':emp_yearly_leaves_count,
                            "date":current_date,
                            "is_active":1
                        }
                        # print(ld.leave_types.title) 
                        serializer = EmployeeLeaveCalculationsSerializers(data=leaves_calculation_data)
                        if not serializer.is_valid():
                            result['message'] = serializer.errors
                            return serializerError(serializer)
                                
                        serializer = serializer.save()
                        # print("test1")

                            
                else:
                     not_found_data.append([emp.id,emp.name,"staff_classification_id is missing"])
                     continue
            print('employee process completed')
            if not_found_data:
                directory_path = 'C:\\Users\\Kavtech\\Downloads'
                file_name = 'employees_not_found_leaves.csv'
                file_path = os.path.join(directory_path, file_name)
                # Create the directory if it doesn't exist
                if not os.path.exists(directory_path):
                    os.makedirs(directory_path)
                not_found_df = pd.DataFrame(not_found_data, columns=['Emp_id','Emp_Name', 'Message'])
                not_found_df.to_csv(file_path, index=False)
            # result['data'] = serializer.data
            result['status'] = 200
            result['message'] = 'Success'
            return successMessage('success')
        except Exception as e:
            result['message'] = e
            return errorMessage(e)
    

    def allow_emp_leaves(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)

            organization_id = token_data['organization_id']
            pk=self.kwargs['pk']

            year=request.data.get('year',None)
            if year is None:
               year=datetime.datetime.today().year

            

            # current_year = datetime.date.today().year
            current_date = datetime.date.today()
            # print(current_date)
            employee=Employees.objects.filter(id=pk,organization_id=organization_id,is_active=True)

            if not employee.exists():
                return errorMessage("Employee not exists at this id")
            emp=employee.get()

            if emp.staff_classification is not None:
                    # print(emp.id)
                    # print(emp.staff_classification_id)

                    leave_duration = SetLeavesDuration.objects.filter(staff_classification=emp.staff_classification,year=year,leave_types__organization=organization_id,is_active=True)
                    # print("OUT")

                    if not leave_duration.exists():
                        return errorMessage("No leaves data exists against this staffclassification")

                    for ld in leave_duration:
                        
                        # print(ld.leave_types.title)
                        query = EmployeeLeaveCalculations.objects.filter(
                            employee=emp.id, 
                            set_leave_duration=ld.id, 
                            is_active=True
                        )
                        in_progress_leaves = 0
                        under_review_leaves=0 
                        approved_leaves= 0
                        not_approved_leaves = 0
                        remaining_leaves_count=0
                        previous_approved_leaves=0

                        if not query.exists():
                        
                            
                            if emp.joining_date:
                                joining_year = emp.joining_date.year
                                
                                # print(emp.joining_date)
                                if joining_year < year:
                                    emp_yearly_leaves_count=ld.allowed_leaves
                                    remaining_leaves_count=ld.allowed_leaves

                        
                                else:
                                    joining_month = emp.joining_date.month - 1
                                    # Calculate remaining months in the year
                                    remaining_months = 12 - joining_month
                                    
                                    count=round(ld.allowed_leaves/12 * remaining_months)
                                    # print(count)

                                    emp_yearly_leaves_count=count  
                                    remaining_leaves_count=count

                                approved_leaves_durations=EmployeesLeaves.objects.filter(employee=emp.id,set_leave_duration=ld,status='approved',start_date__year=year,is_active=True)

                                for obj in approved_leaves_durations:
                                    previous_approved_leaves+=obj.duration

                                remaining_leaves_count=max(remaining_leaves_count-previous_approved_leaves,0)

                        
                            else:
                                return errorMessage('Joining Data is missing')
                            
                        else:
                            continue

                     
                        # print("Out")
                        if remaining_leaves_count < 0:
                            remaining_leaves_count = 0

                        leaves_calculation_data = {
                            'employee':emp.id,
                            'set_leave_duration':ld.id,
                            'in_progress_leaves': in_progress_leaves,
                            'remaining_leaves': remaining_leaves_count,
                            'approved_leaves': approved_leaves,
                            'not_approved_leaves': not_approved_leaves,
                            'underreview_leaves': under_review_leaves,
                            'emp_yearly_leaves':emp_yearly_leaves_count,
                            "date":current_date,
                            "is_active":1
                        }
                        # print(ld.leave_types.title) 
                        serializer = EmployeeLeaveCalculationsSerializers(data=leaves_calculation_data)
                        if not serializer.is_valid():
                            return serializerError(serializer.errors)
                        serializer = serializer.save() 
                        

                    user_id=request.user.id
                    script_title="Staff Classification Leaves Script"
                    status=1
                    script_type=1
                    staff_classification=emp.staff_classification.id

                    output = script_logs(pk,staff_classification,script_title,script_type,year,status,user_id)
                        # print(output)
                    if output['status'] == 400:
                                return errorMessage(output['message'])

                    return successMessageWithData('success',output['data'])
                                
            else:
                    return errorMessage("staff_classification_id is missing")


        except Exception as e:
            return exception(e)




class EmployeesLeavesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsEmployeeOnly]  
    queryset = EmployeesLeaves.objects.all()
    serializer_class = EmployeesLeavesSerializers

    def get_queryset(self):
       
        token_data = decodeToken(self, self.request)
        organization_id = token_data['organization_id']
        employee_id = token_data['employee_id']
        
        return self.queryset.filter(employee=employee_id, employee__organization=organization_id) 


   
    def list(self, request, *args, **kwargs):
        try:
           
            query = self.get_queryset().filter(is_active=True).order_by('-id')
            # query1 = self.get_queryset().filter(is_active=True).order_by('-id').values()
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
        
    def retrieve(self, request, *args, **kwargs):
        try:
            
            message_variable = 'Employee Leave'
            pk = self.kwargs['pk']
            query = self.get_queryset().filter(id=pk, is_active=True)
            if not query.exists():
                return errorMessage(f'No {message_variable} exists at this id')
            obj = query.get()
            serializer = self.serializer_class(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            employees = Employees.objects.filter(hrmsuser=request.user.id)
            emp = employees.get()
            # print(emp)

            if not emp.staff_classification:
                return errorMessage("Add staff classification of the employee first")
            elif not emp.employee_type:
                return errorMessage("Employee type is a required field")
            elif not emp.employee_type.title == 'Permanent':
                return errorMessage('Only Permanent Employees is elligible for Annual Leaves')

            required_fields = ['start_date', 'end_date', 'leave_types','team_lead']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [start_date, end_date, leave_types,team_lead]')
            
            if request.data:
                request.data._mutable = True

            start_date_str = request.data['start_date']
            present_date_obj = datetime.date.today()
            end_date_str = request.data['end_date'] 

            start_year = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
            end_year = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

            if start_year.year != end_year.year:
                return errorMessage("Submit a separate leave request specifically for the next calendar year")

            if end_year < start_year:#here we check year 
                return errorMessage('end_date cannot be less than the start date')
            # print(request.data['leave_types'])



            leave_type_id = request.data['leave_types']
            leave_type_query = LeaveTypes.objects.filter(Q(gender_classification=emp.gender )|Q(gender_classification=3),id=leave_type_id, organization=emp.organization)
            if not leave_type_query.exists():
                return errorMessage('Leave type does not exists')
            elif not leave_type_query.filter(is_active=True).exists():
                return errorMessage('Leave type is not active')
            
            leave_type_obj = leave_type_query.get()
            

            tl=None

            # team_lead=request.data.get('team_lead',None)

            team_lead=request.data['team_lead']

            # if leave_type_obj.tl_required and team_lead is None:
            #     return errorMessage(f"For {leave_type_obj.title} team lead is required")

            if team_lead is not None:
                # if team_lead==emp.id:
                #     return errorMessage('You can not set yourself as team lead')
                
                team_lead_query=Employees.objects.filter(id=team_lead,organization=organization_id,is_active=True)
                
                if not team_lead_query.exists():
                    return errorMessage('Team Lead not exists at this id')
                
                tl=team_lead_query.get()
            
            # print(leave_type_query)
            
            # if 'is_lock' in request.data:
            #     if request.data['is_lock'] == True:
            #         request.data['lock_by'] = request.user.id

            # print("leave_type_id :" , leave_type_id)
            # return
            leave_duration = SetLeavesDuration.objects.filter(leave_types=leave_type_id,year=start_year.year, is_active=True)
            # leave_duration = SetLeavesDuration.objects.filter(Q(leave_types__gender_classification=emp.gender )|Q(leave_types__gender_classification=3),staff_classification__isnull=True,year=start_year.year,leave_types__organization=organization_id,is_active=True)
            
            if not leave_duration.exists():
                return errorMessage('This leave duration is not set yet')
            

            
            leave_duration_object = leave_duration.first()   # leave_duration.filter(is_lock=True).first()
            # print(leave_duration_object)
            if leave_duration_object.leave_types.is_staff_classification == True:
                if not emp.staff_classification:
                    return errorMessage('staff classification is not set against this employee')
                leave_duration = leave_duration.filter(staff_classification=emp.staff_classification) # , is_lock=True
                if not leave_duration.exists():
                    return errorMessage('Contact Admininistrator, leave duration is not set against this staff classification') #  or it is not locked yet
                leave_duration_object = leave_duration.get()
            
            # if leave_duration_object:
            request.data['set_leave_duration'] = leave_duration_object.id
            # print(request.data.get('leave_dates'))

            leave_dates = request.data.get('leave_dates')
            # print(leave_dates)
            leave_dates = leave_dates.split(',')
            date_validations = self.date_validation(emp.id,leave_dates,leave_duration_object)
            if date_validations['status'] == 400:
                    return errorMessageWithData(date_validations['message'],date_validations['already_exists_dates'])
            # print("Data:")

            start_date =  start_date_str
            present_date = present_date_obj
            end_date = end_date_str

            if isinstance(start_date, str):
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            else:
                start_date = start_date
            
            if isinstance(end_date, str):
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                end_date = end_date
            
            if isinstance(present_date, str):
                present_date = datetime.datetime.strptime(present_date, '%Y-%m-%d').date()
            else:
                present_date = present_date

            # print(leave_duration_object)
            limit_check=EmployeeLeaveCalculations.objects.filter(set_leave_duration=leave_duration_object,employee=employee_id,set_leave_duration__leave_types=request.data['leave_types'],employee__organization=organization_id,is_active=True)  
            # return limit_check
            if not limit_check.exists():
                return errorMessage('Ask admin to set employee specific leave first')
            
            # print(limit_check)

            # return 0
            
            approved_leaves = limit_check.first().approved_leaves
            # in_progress_leaves = limit_check.first().in_progress_leaves
            emp_yearly_leaves = limit_check.first().emp_yearly_leaves
            # underreview_leaves=limit_check.first().underreview_leaves
            # print(request.data['leave_types'])
            
            duration=request.data['duration']
            # print(approved_leaves,"::",in_progress_leaves,"::",emp_yearly_leaves,"::",int(duration))

            limit_count=approved_leaves+int(duration)
            # return errorMessage(underreview_leaves)

            if limit_count>emp_yearly_leaves:
                return errorMessage('Your yearly leaves limit is exhausted')
            
            # print("Test1")
            
            
            # elif not leave_duration.filter(is_lock=True):
            #     return errorMessage('This leave duration is not locked yet. Ask adminstrator to set it first')
            
            
            
           
            emp_leave_dates = EmployeeLeaveDates.objects.filter(employee_leave__set_leave_duration=leave_duration_object,employee_leave__employee=emp.id, is_active=True)
            # print(emp_leave_dates)
            output = None
            if emp_leave_dates:
                # print(emp.id)
                # print(present_date)
                output = self.emp_leave_dates_calculation(emp.id, emp_leave_dates, leave_duration_object, present_date,duration)
                # print("output:",output)
                if output['status'] == 400:
                    # print("IF")
                    return errorMessage(output['message'])
            
            request.data['employee'] = emp.id
            request.data['is_active'] = True
            request.data['status'] = 'in-progress'

            # duration=request.data['duration']
            
            # print(leave_type_obj)
            if leave_type_obj.title == 'Annual Leaves':
                date_check = self.is_date_greater_than_07_days(start_date)
                if date_check['status'] == 400:
                    return errorMessage(date_check['message'])

            

            
            serializer = self.serializer_class(data = request.data)
            # print(request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            employee_leave = serializer.save()
            # print("Test3")
            days_calculation = self.number_of_days_calculation(employee_leave,leave_dates)
            # print(days_calculation)
            if days_calculation['status'] == 200:
                # duration = days_calculation['duration']
                if duration:
                    employee_leave.duration = duration
                    employee_leave.save()
                elif duration == 0 or not duration:
                    employee_leave.is_active=False
                    employee_leave.save()
                    return errorMessage('You are trying to apply leave on a off day')

            # if output is not None:
            #     obj = output['data']
            #     # print(obj.in_progress_leaves)
            #     # print("Test1:",type(obj))
            #     # print(type(duration))
            #     obj.in_progress_leaves = obj.in_progress_leaves + int(duration)
            #     obj.save()

            # else :
            #     obj=limit_check.get()
            #     obj.in_progress_leaves = obj.in_progress_leaves + int(duration)
            #     obj.save()


            # print("After output",output)
            # requestEmailsFromEmployees('Leave', 'saddam.baig@kavmails.net')
            cc_employee=EmailRecipients.objects.filter(employee__organization=organization_id,level=2,is_active=True)

            if cc_employee.exists():
                leave_dates=", ".join(leave_dates)
                date=leave_dates
                ccobj=cc_employee.get()
                if team_lead is not None:
                    date=leave_dates
                    SimpleLeaveRequestEmailsFromEmployees(tl.name
                                                          ,emp.name,
                                                          'Leave Application Received',
                                                          leave_type_obj.title,
                                                          tl.official_email,
                                                          ccobj.employee.official_email,
                                                          date)
                # else:
                #     SimpleLeaveRequestEmailsFromEmployees(None,emp.name,'Leave Application Received',leave_type_obj.title,None,eobj.employee.official_email,eobj.employee.name,date)
                
           
            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)    
    
    def emp_leave_dates_calculation(self, emp_id, leave_dates, set_leave_duration_obj, current_date,duration):
        try: 
            result = {
                'status': 400, 
                'message': '', 
                'data': None,
                'system_error_message': '',
            }
            # print(current_date)
            query = EmployeeLeaveCalculations.objects.filter(
                employee=emp_id, 
                set_leave_duration=set_leave_duration_obj.id,
                is_active=True
            )
            is_new = 0
            # print(query)
            if not query.exists():
                # print("IN IF")
                employees = Employees.objects.filter(id=emp_id)
                emp = employees.get()
                
                current_year = datetime.date.today().year
                
                joining_year = emp.joining_date.year
                
                is_new = 1
                in_progress_leaves = 0
                under_review_leaves=0 
                approved_leaves= 0
                not_approved_leaves = 0
                
                 #calulation for new joining by joing date. 
                # first get the employee joining year
                # if year is current year then else we set the total leave as allowed_leaves
                # emp_yearly_leaves_count = allowed_leaves
                if joining_year < current_year:
                 emp_yearly_leaves_count=set_leave_duration_obj.allowed_leaves
                 remaining_leaves_count=set_leave_duration_obj.allowed_leaves
                 
                else:
                    joining_month = emp.joining_date.month - 1
                    # Calculate remaining months in the year
                    remaining_months = 12 - joining_month
                    count=round(set_leave_duration_obj.allowed_leaves/12 * remaining_months)
                    # print(count)
                    emp_yearly_leaves_count=count
                    remaining_leaves_count=count
                # first get the employee joining month from its joining date
                # then calculate that year months
                # emp_yearly_leaves_count = set_leave_duration_obj->allowed_leaves/12 * 4
                # set employee yearly leaves

                # return result
            else:
                # print("test2")
                obj = query.first()
                emp_yearly_leaves_count = obj.emp_yearly_leaves
                in_progress_leaves = leave_dates.filter(employee_leave__status='in-progress').count()
                under_review_leaves = leave_dates.filter(employee_leave__status='under-review').count()
                approved_leaves = leave_dates.filter(employee_leave__status='approved').count()
                not_approved_leaves = leave_dates.filter(employee_leave__status='not-approved').count()

            
            if approved_leaves+in_progress_leaves+int(duration)>emp_yearly_leaves_count:
                result['message'] = 'Your approved and in-progress leaves have exhausted your yearly quota.'
                return result

            remaining_leaves_count = emp_yearly_leaves_count - approved_leaves
            if remaining_leaves_count < 0:
                remaining_leaves_count = 0
            
            leaves_calculation_data = {
                'employee':emp_id,
                'in_progress_leaves': in_progress_leaves,
                'remaining_leaves': remaining_leaves_count,
                'approved_leaves': approved_leaves,
                'not_approved_leaves': not_approved_leaves,
                'underreview_leaves': under_review_leaves,
                'emp_yearly_leaves':emp_yearly_leaves_count,
                'date':current_date,
            }

            # print(leaves_calculation_data)

            # return "test"

            if is_new==1:
                serializer = EmployeeLeaveCalculationsSerializers(data=leaves_calculation_data)
            else:
                # print("Else")
                serializer = EmployeeLeaveCalculationsSerializers(obj,data=leaves_calculation_data, partial=True)
              
               
            if not serializer.is_valid():
                # print("Not valid")
                result['message'] = serializer.errors
                return result
            
            saved_object = serializer.save()

            # print("Test::::::",serializer)

            serialized_data = EmployeeLeaveCalculationsSerializers(saved_object).data

            # The serializer has been provided with data.

            result['data'] = saved_object


            result['status'] = 200
            result['message'] = 'Success'
            return result
        except Exception as e:
            result['message'] = e
            return result


    def date_validation(self, emp_id,leave_dates,leave_duration_object):
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
            for date in leave_dates:
                
                if isinstance(date, str):
                    date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
                else:
                    date = date

                emp_leaves = EmployeeLeaveDates.objects.filter(Q(status='approved')|Q(status__isnull=True),employee_leave__employee=emp_id,date=date,is_active=True)
                
                if emp_leaves.exists():
                        already_exists_dates.append(date)
                        continue
                
            # print("Dates")
                

            if already_exists_dates:
                    # print("Test1:",already_exists_dates)
                    result['message']=f"Leave already exists against these dates"
                    result['already_exists_dates']=already_exists_dates
                    return result

       
            result['status'] = 200
            # print("Data Validation End:")
            return result
        except Exception as e:
            result['message'] = e
            return result

    # def number_of_days_calculation(self, employee_leave, start_date, end_date, organization_id):
    #     try:
    #         result = {'status': 400, 'message': '', 'duration': None, 'error_list': ''}
    #         emp_leave_days_data = {
    #             'employee_leave': employee_leave.id,
    #             'date': None,
    #             'is_active': True 
    #         }
    #         total_days = 0
    #         duration = end_date - start_date

    #         if duration == 0:
    #             total_days = 1
    #         else:   
    #             duration = duration.days
    #             total_days = duration + 1


    #         holidays = EmployeesOfficialHolidays.objects.filter(
    #             organization=organization_id,
    #             is_active=True,
    #         )
    #         if not holidays.exists():
    #             return result
    #         holidays_date = [holiday.date.strftime('%Y-%m-%d') for holiday in holidays]
    #         error_list = []
    #         for i in range(duration + 1):
    #             current_date = start_date + datetime.timedelta(days=i)
    #             emp_leave_days_data['date'] = current_date
    #             if current_date.strftime('%A') == 'Saturday' or current_date.strftime('%A') == 'Sunday':
    #                 total_days -= 1
    #                 continue
    #             elif current_date.strftime('%Y-%m-%d') in holidays_date:
    #                 total_days -= 1
    #                 continue

    #             serializer = EmployeeLeaveDatesSerializers(data=emp_leave_days_data)
    #             if not serializer.is_valid():
    #                 error_list.append(serializer.errors)

                
    #             serializer.save()

    #         result = {'status': 200, 'message': 'success', 'duration': total_days, 'error_list': ''}
    #         return result
    #     except Exception as e:
    #         result = {'status': 400, 'message': str(e)}
    #         return result

    def number_of_days_calculation(self, employee_leave,leave_dates):
        try:
            result = {'status': 400, 'message': '', 'duration': None, 'error_list': ''}
            emp_leave_days_data = {
                'employee_leave': employee_leave.id,
                'date': None,
                'is_active': True 
            }
            # total_days = 0
            # # duration = end_date - start_date

            # if duration == 0:
            #     total_days = 1
            # else:   
            # duration = duration.days
            # total_days = duration 


            # holidays = EmployeesOfficialHolidays.objects.filter(
            #     organization=organization_id,
            #     is_active=True,
            # )
            # if not holidays.exists():
            #     return result
            # holidays_date = [holiday.date.strftime('%Y-%m-%d') for holiday in holidays]
            error_list = []
            for date in leave_dates:
                current_date =date 

                if isinstance(current_date, str):
                  current_date = datetime.datetime.strptime(current_date, '%Y-%m-%d').date()
                else:
                  current_date = current_date
                # print(current_date)
                emp_leave_days_data['date'] = current_date
                
                serializer = EmployeeLeaveDatesSerializers(data=emp_leave_days_data)
                if not serializer.is_valid():
                    error_list.append(serializer.errors)

                
                serializer.save()

            result = {'status': 200, 'message': 'success', 'error_list': ''}
            return result
        except Exception as e:
            result = {'status': 400, 'message': str(e)}
            return result




    def patch(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            # print(pk)
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('This employee has no leave allowance at this id')
            obj = query.get()

            if not obj.status == 'in-progress':
                return errorMessage('Request cannot be edited, once it reached stage other then the in-progress stage')

            if request.data:
                request.data.is_mutable = True

            if 'start_date' in request.data:
                start_date_str = request.data['start_date']
                
                date_check = self.is_date_greater_than_07_days(start_date_str)
                if date_check['status'] == 400:
                    return errorMessage(date_check['message'])

            serializer = UpdateEmployeesLeavesSerializers(obj, data = request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)

    def is_date_greater_than_07_days(self, start_date_str):
        try:
            result = {'status': 200, 'message': None}
            if isinstance(start_date_str, str):
                start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            else:
                start_date = start_date_str

            current_date = datetime.date.today()
            # Calculate the difference between the start date and the current date
            date_diff = start_date - current_date
            if date_diff.days < 7:
                result['status'] = 400
                result['message'] = 'Annual leave notice: 07 days. No requests for previous dates, please'

            return result
        except Exception as e:
            result['status'] = 400
            result['message'] = str(e)

    def get_pre_data(self,request,*args, **kwargs):
        try:
            print('i am here')
            organization_id=decodeToken(self,self.request)['organization_id']
            employee_id=decodeToken(self,self.request)['employee_id']
            year=request.data.get("year",None)
            if year is None:
                year=datetime.datetime.today().year
            query = Employees.objects.filter(id=employee_id,organization=organization_id, is_active=True)
            # print(query.values())
            serializer = ListEmployeeLeaveDateSerializers(query,context={
                'year':year
            }, many=True)
            # print(serializer.data)
            return success(serializer.data)
        except Exception as e:
            return None  
    
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
            if not obj.status == 'in-progress':
                return errorMessage('Request cannot be deleted, once it reached stage other then the in-progress stage')
            # print(obj)
            leaves_dates_query=EmployeeLeaveDates.objects.filter(employee_leave=obj,is_active=True)

            for leave_date in leaves_dates_query:
                leave_date.is_active = False
                leave_date.save()
            duration = obj.duration
            # print(obj)
            # print(obj.start_date.year)
            # print(duration)
            
            query = EmployeeLeaveCalculations.objects.filter(
                employee=obj.employee.id, 
                set_leave_duration=obj.set_leave_duration.id,
                is_active=True
            )

            # print(query.values())

            # print("Test")

            if query.exists():
                obj1 = query.get()
                # print(obj1)
                obj1.in_progress_leaves = max(obj1.in_progress_leaves - duration,0)
                obj1.save()

            
            
            obj.is_active = False
            obj.save()
            return successMessage("Deactivated Successfully")
        except Exception as e:
            return exception(e)
        

class LeavesStatusLogsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated] 
    queryset = LeavesStatusLogs.objects.all()
    serializer_class = LeavesStatusLogsSerializers

    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            pk = self.kwargs['pk']
            query = EmployeesLeaves.objects.filter(employee__organization=organization_id, id=pk).order_by('-id')
            if not query.exists():
                return errorMessage('No employee leave request exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('Leave request is deactivated at this id')
            
            queryset = self.queryset.filter(employee_leave=pk, is_active=True)
            serializer = self.serializer_class(queryset, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def pending_leaves(self,organization_id):
        try:
            current_date=datetime.datetime.today().date()
            current_month=current_date.month
            current_year=current_date.year
            query=EmployeesLeaves.objects.filter(employee__organization=organization_id,start_date__month=current_month,start_date__year=current_year,status='in-progress',is_active=True)
            # print(query.values())
            serializer =ListEmployeePendingLeaveSerializer(query, many=True)
            return serializer.data
        except Exception as e:
            return exception(e)
        
    
    def get_all_leaves_requests_new(self,request,*args, **kwargs):
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
                # print(current_date)
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
                # print(first_day_of_previous_month,last_day_of_current_month)
                query = EmployeesLeaves.objects.filter(
                        
                        Q(end_date__gte=first_day_of_previous_month, start_date__lte=last_day_of_current_month) |
                        Q(end_date__gte=first_day_of_previous_month, end_date__lte=last_day_of_current_month) |
                        Q(start_date__gte=first_day_of_previous_month, start_date__lte=last_day_of_current_month),
                        employee__organization=organization_id,
                        is_active=True,
                    ).order_by('-id')
                
                
            else:
                if year is None:
                    year=datetime.datetime.today().year

                query = EmployeesLeaves.objects.filter(
                        Q(start_date__month=month)| Q(end_date__month=month),
                        Q(start_date__year=month)| Q(end_date__year=year),
                        employee__organization=organization_id,
                        is_active=True,
                    ).order_by('-id')


            # print(query)
            if employee is not None:
                query=query.filter(employee=employee)
                

            serializer =EmployeesLeavesSerializers(query, many=True)
            return success(serializer.data)
            
            
        except Exception as e:
            return None
    
    def get_all_leaves_requests(self, organization_id):
        try:

            query=Employees.objects.filter(organization=organization_id,is_active=True)
            # print(query.values())
            serializer =ListEmployeeLeaveDateSerializers(query, many=True)

            return serializer.data
            
        except Exception as e:
            return None

    def patch(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            pk = self.kwargs['pk']
            if 'status' not in request.data:
                return errorMessage('status is a required field')
            query = EmployeesLeaves.objects.filter(employee__organization=organization_id, id=pk)
            if not query.exists():
                return errorMessage('No employee Leave request exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('Leave request is deactivated at this id')
            
            elif query.filter(status=request.data['status']).exists():
                return successMessage("Same status already set")
            
            obj = query.get()
            decision_reason = request.data.get('decision_reason', None)
            
            
            query1 = EmployeeLeaveCalculations.objects.filter(
                    employee=obj.employee.id, 
                    set_leave_duration=obj.set_leave_duration,
                    is_active=True
                )
                
            # print(query1)
            if not query1.exists():
                    return errorMessage('Ask admin to set employee specific leave first')
                
                # print(obj1.approved_leaves + obj.duration > obj1.emp_yearly_leaves)

                # print("Sum of approved leaves and duration:", obj1.approved_leaves + obj.duration)
                # print("Yearly leaves limit:", obj1.emp_yearly_leaves)
                # print("Condition result:", obj1.approved_leaves + obj.duration > obj1.emp_yearly_leaves)
            obj1 = query1.get()

            emp_leave_dates = EmployeeLeaveDates.objects.filter(employee_leave=obj,employee_leave__employee=obj.employee.id, is_active=True)

            if request.data['status']=='approved' and obj.status!='approved':

                if obj1.approved_leaves >= obj1.emp_yearly_leaves:
                    return errorMessage('Your yearly leaves limit is exhausted')
                
                if obj1.approved_leaves + obj.duration > obj1.emp_yearly_leaves:
                    return errorMessage('Your yearly leaves limit is exhausted')
                
                emp_leave_dates.update(status='approved')
                obj1.approved_leaves=obj1.approved_leaves+obj.duration
                obj1.remaining_leaves=max(obj1.remaining_leaves-obj.duration,0)
                obj1.save()

            

                
            
            if obj.status == 'approved'  and request.data['status']!='approved':
                # minus the duration from approved and add in the remaining
                # print(f"Before update - approved_leaves: {obj1.approved_leaves}, duration: {obj.duration}")
                obj1.approved_leaves=max(obj1.approved_leaves-obj.duration,0)
                obj1.remaining_leaves=obj1.remaining_leaves+obj.duration
                obj1.save()

            if request.data['status']=='not-approved':
                emp_leave_dates.update(status='not-approved')


            status = request.data['status']
            
            
            status_list = ['in-progress', 'under-review', 'not-approved', 'approved']
            if status not in status_list:
                return errorMessage(f'Status can only be {status_list}')
            # print(obj.employee.id)
            # emp_leave_dates = EmployeeLeaveDates.objects.filter(employee_leave=obj,employee_leave__employee=obj.employee.id, is_active=True)
            # print(emp_leave_dates.values())
            # return errorMessage(emp_leave_dates)
            # if emp_leave_dates:
            #     output = self.emp_leave_dates_calculations(
            #         obj.employee.id, 
            #         obj.duration,
            #         emp_leave_dates, 
            #         obj.set_leave_duration, 
            #         obj.start_date,
            #         obj1,
            #     )
            #     # print("Output:",output)
            #     if output['status'] == 400:
            #         return errorMessage(output['message'])
                
            # # print(obj)
            
            obj.status = status
            obj.decision_reason = decision_reason
            obj.save()
            label_update_status_list = ['in-progress', 'under-review', 'not-approved', 'approved']

        # Ensure the status is valid for processing
            if status in label_update_status_list:
                for date in emp_leave_dates:
                # Query for existing active attendance label
                    query = EmployeesAttendanceLabel.objects.filter(
                        employee=obj.employee, 
                        date=date.date, 
                        is_active=True
                    )
                    # Check if an active record exists
                    if query.exists():
                        # Update the record if the status is 'not-approved', 'in-progress', or 'under-review'
                        if status in ['not-approved', 'in-progress', 'under-review']:
                            attendance_label = query.get()  # Fetch the single matching record
                            attendance_label.is_active = False
                            attendance_label.save()
                    else:
                        # Create a new record if the status is 'approved'
                        if status == "approved":
                            EmployeesAttendanceLabel.objects.create(
                                employee=obj.employee,
                                date=date.date,
                                attendance_status='L',  # Assuming 'L' stands for 'Leave'
                                created_by=request.user,  # Assuming request is passed and valid
                                comments=obj.set_leave_duration.leave_types.title
                            )                 
                
            status_dict = {
                'employee_leave': pk,
                'status': status,
                'action_by': request.user.id,
                'action_on': datetime.date.today(), 
                'decision_reason': decision_reason,
            }


            serializer = self.serializer_class(data = status_dict)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            requestDecisionFromManagement(obj.employee.name,'Leave Status Update','Leaves',status,decision_reason, obj.employee.official_email)
            return successMessageWithData('Successfully updated', serializer.data)
        except Exception as e:
            return exception(e)
        

    def update_leave_status(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            # pk = self.kwargs['pk']
            # print(pk)
            if 'status' not in request.data:
                return errorMessage('status is a required field')
            
            status = request.data['status']
                
                
            status_list = ['in-progress', 'under-review', 'not-approved', 'approved']
            if status not in status_list:
                    return errorMessage(f'Status can only be {status_list}')
            
            if 'leave_array' not in request.data:
                return errorMessage('Leave array is required')
            
            decision_reason = request.data.get('decision_reason', None)

            leave_array=request.data['leave_array']
            count=0
            status_error=[]
            error_list=[]
            limit_error=[]
            
            for pk in leave_array:
                query = EmployeesLeaves.objects.filter(employee__organization=organization_id, id=pk)
                if not query.exists():
                    error_list.append(pk)
                    continue
                elif not query.filter(is_active=True):
                    # return errorMessage('Leave request is deactivated at this id')
                    error_list.append(pk)
                    continue
                
                elif query.filter(status=request.data['status']).exists():
                    status_error.append(pk)
                    continue
                
                obj = query.get()
                
                
                
                query1 = EmployeeLeaveCalculations.objects.filter(
                        employee=obj.employee.id, 
                        set_leave_duration=obj.set_leave_duration,
                        is_active=True
                    )
                    
                
                if not query1.exists():
                        error_list.append(pk)
                        continue
                obj1 = query1.get()

                emp_leave_dates = EmployeeLeaveDates.objects.filter(employee_leave=obj,employee_leave__employee=obj.employee.id, is_active=True)

                if request.data['status']=='approved' and obj.status!='approved':

                    if obj1.approved_leaves >= obj1.emp_yearly_leaves:
                        error_list.append(pk)
                        continue

                    if obj1.approved_leaves + obj.duration > obj1.emp_yearly_leaves:
                        error_list.append(pk)
                        continue
                    
                    emp_leave_dates.update(status='approved')
                    obj1.approved_leaves=obj1.approved_leaves+obj.duration
                    obj1.remaining_leaves=max(obj1.remaining_leaves-obj.duration,0)
                    obj1.save()

                
                if obj.status == 'approved'  and request.data['status']!='approved':
                    obj1.approved_leaves=max(obj1.approved_leaves-obj.duration,0)
                    obj1.remaining_leaves=obj1.remaining_leaves+obj.duration
                    obj1.save()

                if request.data['status']=='not-approved':
                    emp_leave_dates.update(status='not-approved')


                
        
                obj.status = status
                obj.decision_reason = decision_reason
                obj.save()

                
                status_dict = {
                    'employee_leave': pk,
                    'status': status,
                    'action_by': request.user.id,
                    'action_on': datetime.date.today(), 
                    'decision_reason': decision_reason,
                }

                serializer = self.serializer_class(data = status_dict)
                if not serializer.is_valid():
                    error_list.append(pk)

                serializer.save()

                requestDecisionFromManagement(obj.employee.name,'Leave Status Update','Leaves',status,decision_reason, obj.employee.official_email)

                count +=1

            data = {
                    'error_list': error_list, 
                    'status_error': status_error,
                }


            if count == len(leave_array):
                return successMessage('All Leave status is changed successfuly')
            elif count == 0:
                return errorMessageWithData('Failed to change Leave status', data) 
            elif count > 0:
                return successMessageWithData('Some of the data is processed successfully', data)
            
            
        except Exception as e:
            return exception(e)
        


    def emp_leave_dates_calculations(self, emp_id, duration, leave_dates, set_leave_duration_obj, current_date,obj):
        try:
            result = {
                'status': 400, 
                'message': '', 
                'data': None,
                'system_error_message': '',
            }
            # print(leave_dates)
            # query = EmployeeLeaveCalculations.objects.filter(
            #     employee=emp_id, 
            #     set_leave_duration=set_leave_duration_obj.id,
            #     is_active=True
            # )
            # print(query)
            print("Update")

            

            # obj = query.first()
            emp_yearly_leaves_count = obj.emp_yearly_leaves
            in_progress_leaves = leave_dates.filter(employee_leave__status='in-progress').count()
            under_review_leaves = leave_dates.filter(employee_leave__status='under-review').count()
            approved_leaves = leave_dates.filter(employee_leave__status='approved').count()
            not_approved_leaves = leave_dates.filter(employee_leave__status='not-approved').count()
            
            # return errorMessage(under_review_leaves)

        
            
            # print(f"Employee Yearly Leaves Count: {emp_yearly_leaves_count}\n"
            #     f"In-Progress Leaves: {in_progress_leaves}\n"
            #     f"Under Review Leaves: {under_review_leaves}\n"
            #     f"Approved Leaves: {approved_leaves}\n"
            #     f"Not Approved Leaves: {not_approved_leaves}")

           

            

            remaining_leaves_count = emp_yearly_leaves_count - approved_leaves
            if remaining_leaves_count < 0:
                remaining_leaves_count = 0


            leaves_calculation_data = {
                'in_progress_leaves': in_progress_leaves,
                'remaining_leaves': remaining_leaves_count,
                'approved_leaves': approved_leaves,
                'not_approved_leaves': not_approved_leaves,
                'underreview_leaves': under_review_leaves,
            }

            serializer = EmployeeLeaveCalculationsSerializers(obj, data=leaves_calculation_data, partial=True)
            # print(serializer)
            if not serializer.is_valid():
                result['message'] = serializer.errors
                return result
            serializer.save()

            result['data'] = obj
            result['status'] = 200
            result['message'] = 'Success'
            return result
        except Exception as e:
            result['message'] = e
            return result

    
# Script required to sync the data
class EmployeeLeaveCalculationScriptsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ] 
    queryset = EmployeeLeaveCalculations.objects.all()
    serializer_class = EmployeeLeaveCalculationsSerializers

    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            query = self.queryset.filter(employee__organization=organization_id, is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def sync_emp_leaves_dates(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            
            emp_leave = EmployeesLeaves.objects.filter(employee__organization=organization_id, is_active=True)
            output = []

            for emp_leave_obj in emp_leave:
                leave_dates = EmployeeLeaveDates.objects.filter(
                    employee_leave=emp_leave_obj.id, 
                    date__year = datetime.date.today().year,
                    is_active=True
                )
                if not leave_dates.exists():
                    start_date = emp_leave_obj.start_date
                    end_date = emp_leave_obj.end_date
                    emp_leave_days_data = {
                        'employee_leave': emp_leave_obj.id,
                        'date': None,
                        'is_active': True 
                    }
                    
                    duration = end_date - start_date

                    if duration == 0:
                        total_days = 1
                    else:   
                        duration = duration.days
                        total_days = duration + 1


                    holidays = EmployeesOfficialHolidays.objects.filter(
                        organization=organization_id,
                        is_active=True,
                    )
                    if not holidays.exists():
                        continue
                    holidays_date = [holiday.date.strftime('%Y-%m-%d') for holiday in holidays]
                    error_list = []
                    for i in range(duration + 1):
                        current_date = start_date + datetime.timedelta(days=i)
                        emp_leave_days_data['date'] = current_date
                        if current_date.strftime('%A') == 'Saturday' or current_date.strftime('%A') == 'Sunday':
                            total_days -= 1
                            continue
                        elif current_date.strftime('%Y-%m-%d') in holidays_date:
                            total_days -= 1
                            continue
                        
                        serializer = EmployeeLeaveDatesSerializers(data=emp_leave_days_data)
                        if not serializer.is_valid():
                            error_list.append(serializer.errors)
                        serializer.save()
                        output.append(serializer.data)

                        emp_leave_obj.duration = total_days
                        emp_leave_obj.save()
                else:
                    continue

            return successMessageWithData('success', output)
        except Exception as e:
            return exception(e)

    def sync_leave_calculation_data(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            
            current_date = datetime.date.today()
            current_year = current_date.year
            employees = Employees.objects.filter(organization=organization_id, is_active=True)
            missed_staff_classification = []
            missed_joining_date = []
            serializer_errors = []
            emp_data = []
            output = []

            leave_type = LeaveTypes.objects.filter(organization=organization_id, is_active=True)
            if not leave_type.exists():
                return errorMessage('Please set leave type first')
            
            leave_type_ids = [type.id for type in leave_type]

            set_leave_duration = SetLeavesDuration.objects.filter(
                leave_types__organization=organization_id,
                is_active=True
            )

            for ids in leave_type_ids:
                if not set_leave_duration.filter(leave_types=ids).exists():
                    return errorMessage(f'duration is not set against this id: {ids}') 

            for emp in employees:
                for leave_type_id in leave_type_ids:
                    emp_id = emp.id
                    
                    if not emp.staff_classification:
                        missed_staff_classification.append(emp_id)
                        continue
                    joining_date = emp.joining_date
                    if not joining_date:
                        missed_joining_date.append(emp_id)
                        continue

                    set_leave_duration_obj = set_leave_duration.filter(leave_types=leave_type_id)
                    if set_leave_duration_obj.filter(leave_types__is_staff_classification=True):
                        set_leave_duration_obj = set_leave_duration_obj.filter(
                            staff_classification=emp.staff_classification
                        )
                        if not set_leave_duration_obj.exists():
                            
                            continue
                        else:
                           set_leave_duration_obj = set_leave_duration_obj.get()
                    else:
                        set_leave_duration_obj = set_leave_duration_obj.get()

                    query = self.queryset.filter(
                        employee=emp_id, 
                        set_leave_duration=set_leave_duration_obj.id,
                        date__year=current_date.year, 
                        is_active=True
                    ) 
                    if not query.exists():
                        yearly_leaves = set_leave_duration_obj.allowed_leaves
                        if not set_leave_duration_obj.staff_classification or joining_date.year < current_year:
                            emp_yearly_leaves = yearly_leaves
                        else:
                            output = self.emp_leaves_based_on_staff_classification(joining_date, yearly_leaves)
                            if output['status'] == 400:
                                continue
                            emp_yearly_leaves = output['yearly_limit']

                        emp_leave_calculated_data = {
                            'employee': emp_id,
                            'set_leave_duration': set_leave_duration_obj.id,
                            'emp_yearly_leaves': emp_yearly_leaves,
                            'remaining_leaves': emp_yearly_leaves,
                            'date': current_date,
                        }
                    
                        serializer = EmployeeLeaveCalculationsSerializers(data = emp_leave_calculated_data)
                        if not serializer.is_valid():
                            serializer_errors.append(serializer.errors)
                        serializer.save()
                        output = []
                        output.append(serializer.data)
                    else:
                        obj = query.get()
                        print('before leave dates')
                        
                        if not LeaveTypes.objects.filter(id=leave_type_id).exists():
                            print('does not exists yay')
                            continue


                        leave_dates = EmployeeLeaveDates.objects.filter(
                            employee_leave__employee=emp_id,
                            employee_leave__leave_types=leave_type_id,
                            date__year = current_year,
                            is_active=True
                        )
                        if leave_dates.exists():
                            emp_yearly_leaves_count = obj.emp_yearly_leaves
                            in_progress_leaves = leave_dates.filter(employee_leave__status='in-progress').count()
                            under_review_leaves = leave_dates.filter(employee_leave__status='under-review').count()
                            approved_leaves = leave_dates.filter(employee_leave__status='approved').count()
                            not_approved_leaves = leave_dates.filter(employee_leave__status='not-approved').count()
                            remaining_leaves_count = emp_yearly_leaves_count - approved_leaves
                            if remaining_leaves_count < 0:
                                remaining_leaves_count = 0

                            leaves_calculation_data = {
                                'in_progress_leaves': in_progress_leaves,
                                'remaining_leaves': remaining_leaves_count,
                                'approved_leaves': approved_leaves,
                                'not_approved_leaves': not_approved_leaves,
                                'underreview_leaves_count': under_review_leaves,
                            }
                            serializer = EmployeeLeaveCalculationsSerializers(obj, data=leaves_calculation_data, partial=True)
                            if not serializer.is_valid():
                                print(serializer.errors)
                                continue
                            serializer.save()
                            output.append(serializer.data)
                        else:
                            print('Emp leave does not exists')
            return successMessageWithData('Success', output)

        except Exception as e:
            return exception(e)


    def emp_leaves_based_on_staff_classification(self, joining_date, yearly_leaves):
        try:
            result = {'status': 200, 'message': None, 'yearly_limit': yearly_leaves, 'system_error_message': ''}
            month = 12 - joining_date.month + 1
            result['yearly_limit'] = round(( yearly_leaves / 12 ) * month)
            return result
        except Exception as e:
            result['status'] = 400
            return result
        
    # This api will use only once
    def post_sync_previous_leaves(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']

            query = EmployeesAttendanceLabel.objects.filter(
                employee__organization=organization_id,
                is_active=True,
                attendance_status='L',
            )
            count = 0
            emp_leaves = EmployeesLeaves.objects.filter(
                employee__organization=organization_id, 
                is_active=True
            )

            emp_query = Employees.objects.filter(
                organization=organization_id,
                is_active=True
            )

            leave_duration_not_set = []
            leave_type_does_not_exists = []
            already_exists = []
            invalid_serializer = []
            result = []
            set_leave_duration = SetLeavesDuration.objects.filter(
                leave_types__organization=organization_id,
                is_active=True
            )
            
            for obj in emp_query:
                emp = obj
                emp_id = emp.id

                emp_leaves = query.filter(employee=emp_id)
                
                if emp_leaves.exists():
                    emp_leaves = emp_leaves.order_by('date')
                    dates = []
                    is_initial = True
                    individual_dates = []
                    previous_leave_types = []
                    iteration = 0
                    duration = 0
                    count = 0
                
                    for label in emp_leaves:
                        count += 1
                        if is_initial:
                            dates = label.date
                            start_date = dates
                            end_date = dates
                            start_month = dates.month
                            leave_type_title = label.comments
                            if label.comments.lower() in ['casual', 'sick', 'compensatory', 'emergency']:
                                leave_type_title = 'casual leaves'
                            elif label.comments.lower() in ['annual']:
                                leave_type_title = 'annual leaves'
                            elif label.comments.lower() in ['bereavement', 'breavement']:
                                leave_type_title = 'bereavement leaves'
                            elif label.comments.lower() in ['marriage']:
                                leave_type_title = 'marriage leaves'
                            elif label.comments.lower() in ['paternity']:
                                leave_type_title = 'paternity leaves'

                            leave_type = LeaveTypes.objects.filter(
                                organization=organization_id,
                                title__iexact=leave_type_title, 
                                is_active=True
                            )
                            if not leave_type.exists():
                                leave_type_does_not_exists.append(emp_id)
                                continue
                            
                            leave_type_id = leave_type.get().id
                            set_leave_duration_obj = set_leave_duration.filter(leave_types=leave_type_id)

                            if set_leave_duration_obj.filter(leave_types__is_staff_classification=True).exists():
                                set_leave_duration_obj = set_leave_duration_obj.filter(
                                    staff_classification=emp.staff_classification
                                )
                                if not set_leave_duration_obj.exists():
                                    leave_duration_not_set.append(emp_id)
                                    continue
                                else:
                                    set_leave_duration_obj = set_leave_duration_obj.get()
                            else:
                                set_leave_duration_obj = set_leave_duration_obj.get()
                            
                            individual_dates.append(dates)
                            previous_leave_types.append(leave_type_id)
                            is_initial = False
                            iteration += 1
                            duration += 1

                            if count < len(emp_leaves):
                                continue
                        
                        if (individual_dates[iteration - 1] + datetime.timedelta(days=1) == label.date
                                and leave_type_id == previous_leave_types[iteration-1]): 
                            end_date = label.date
                            individual_dates.append(end_date)
                            previous_leave_types.append(leave_type_id)
                            iteration += 1
                            duration += 1
                            if count < len(emp_leaves):
                                continue

                        
                        
                        elif label.date.strftime('%A') == 'Saturday' or label.date.strftime('%A') == 'Sunday':
                            end_date = label.date
                            continue
                        if start_month > 6:
                            status = 'under-review'
                        else:
                            status = 'approved'
                      
                        leave_query = EmployeesLeaves.objects.filter(
                            employee=emp_id,
                            employee__organization=organization_id,
                            start_date__lte=start_date,
                            end_date__gte=end_date,
                            is_active=True                            
                        )
                        if leave_query.exists():

                            already_exists.append(emp_id)
                            is_initial = True
                            individual_dates = []
                            previous_leave_types = []
                            iteration = 0
                            continue

                        leave_data = {
                            'employee': emp_id,
                            'leave_types': leave_type_id,
                            'set_leave_duration': set_leave_duration_obj.id,
                            'start_date': start_date,
                            'end_date': end_date,
                            'duration': duration,
                            'status': status
                        }
                        
                        serializer = EmployeesLeavesSerializers(data=leave_data)
                        print('after serializer')
                        if not serializer.is_valid():
                            invalid_serializer.append(serializer.errors)

                        serializer.save()
                        result.append(leave_data)
                        is_initial = False
                        individual_dates = [label.date]
                        iteration = 1
                        start_date = label.date
                        end_date = label.date
                        duration = 1

                        start_month = dates.month
                        leave_type_title = label.comments
                        if label.comments.lower() in ['casual', 'sick', 'compensatory', 'emergency']:
                            leave_type_title = 'casual leaves'
                        elif label.comments.lower() in ['annual']:
                            leave_type_title = 'annual leaves'
                        elif label.comments.lower() in ['bereavement', 'breavement']:
                            leave_type_title = 'bereavement leaves'
                        elif label.comments.lower() in ['marriage']:
                            leave_type_title = 'marriage leaves'
                        elif label.comments.lower() in ['paternity']:
                            leave_type_title = 'paternity leaves'
                        elif label.comments.lower() in ['umrah']:
                            leave_type_title = 'hajj/ umrah leaves'

                        leave_type = LeaveTypes.objects.filter(
                            organization=organization_id,
                            title__iexact=leave_type_title, 
                            is_active=True
                        )
                        if not leave_type.exists():
                            leave_type_does_not_exists.append(emp_id)
                            continue

                        leave_type_id = leave_type.get().id
                        previous_leave_types = [leave_type_id]

                        set_leave_duration_obj = set_leave_duration.filter(leave_types=leave_type_id)

                        if set_leave_duration_obj.filter(leave_types__is_staff_classification=True).exists():
                            set_leave_duration_obj = set_leave_duration_obj.filter(
                                staff_classification=emp.staff_classification
                            )
                            if not set_leave_duration_obj.exists():
                                leave_duration_not_set.append(emp_id)
                                continue
                            else:
                                set_leave_duration_obj = set_leave_duration_obj.get()
                        else:
                            set_leave_duration_obj = set_leave_duration_obj.get()

                        if count == len(emp_leaves):
                            leave_query = EmployeesLeaves.objects.filter(
                                employee=emp_id,
                                employee__organization=organization_id,
                                start_date__lte=start_date,
                                end_date__gte=end_date,
                                is_active=True                            
                            )
                            if leave_query.exists():
                                break

                            leave_data = {
                                'employee': emp_id,
                                'leave_types': leave_type_id,
                                'set_leave_duration': set_leave_duration_obj.id,
                                'start_date': start_date,
                                'end_date': end_date,
                                'duration': duration,
                                'status': status
                            }
                            
                            serializer = EmployeesLeavesSerializers(data=leave_data)
                            if not serializer.is_valid():
                                invalid_serializer.append(serializer.errors)

                            serializer.save()
                            result.append(leave_data)


                        continue

                
            result_data = {
                'result': result,
                'leave_type_does_not_exists': leave_type_does_not_exists,
                'already_exists': already_exists,
                'invalid_serializer': invalid_serializer,
                'leave_duration_not_set': leave_duration_not_set,
            }        
            return successMessageWithData('Success', result_data)

        except Exception as e:
            return exception(e)
        




   # in_progress_leaves = leave_dates.filter(employee_leave__status='in-progress')
                    # under_review_leaves = leave_dates.filter(employee_leave__status='under-review')
                    # approved_leaves = leave_dates.filter(employee_leave__status='approved')
                    # not_approved_leaves = leave_dates.filter(employee_leave__status='not-approved')
                    
                    # in_progress_leaves_count = in_progress_leaves.count()
                    # under_review_leaves_count = under_review_leaves.count()
                    # approved_leaves_count = approved_leaves.count()
                    # not_approved_leaves_count = not_approved_leaves.count()

                    # remaining_leaves_count = approved_leaves_count

                    # leaves_calculation_data = {
                    #     'in_progress_leaves': in_progress_leaves_count,
                    #     'remaining_leaves': remaining_leaves_count,
                    #     'approved_leaves': approved_leaves_count,
                    #     'not_approved_leaves': not_approved_leaves_count,
                    #     'under_review_leaves_count': under_review_leaves_count,
                    # }

                    # serializer = EmployeeLeaveCalculationsSerializers(data=leaves_calculation_data, partial=True)
                    # if not serializer.is_valid():
                    #     return serializerError(serializer.errors)
                    # serializer.save()



class NewJoiningEmployeesLeavePreViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsAdminOnly]

    def scripts_logs_data(self,request,*args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            pk=self.kwargs['pk']
            query = Employees.objects.filter(organization=organization_id, id=pk)
            if not query.exists():
                return errorMessage('No employee exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('Employee is deactivated at this id')
            obj = query.get()
            script_query=ScriptStatusLogs.objects.filter(employee=obj,is_completed=True,is_active=True)
            serializer = ScriptStatusLogsSerializers(script_query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def delete_employee_allowance(self,request,*args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            pk=self.kwargs['pk']
            query = Employees.objects.filter(organization=organization_id, id=pk)
            if not query.exists():
                return errorMessage('No employee exists at this id')
            elif not query.filter(is_active=True):
                return errorMessage('Employee is deactivated at this id')
            
            # elif query.filter(status=request.data['status']).exists():
            #     return successMessage("Same status already set")
            # print("test")
            obj = query.get()
            leaves_query = EmployeeLeaveCalculations.objects.filter(
                            employee=obj, 
                            is_active=True
                        )
            
            if leaves_query.exists():
                leaves_query.update(is_active=False)

            med_query = EmployeesRemainingMedicalAllowance.objects.filter(employee=obj, is_active=True)
            if med_query.exists():
                med_query.update(is_active=False)

            script_query=ScriptStatusLogs.objects.filter(employee=obj,is_completed=True,is_active=True)
            if script_query.exists():
               script_query.update(is_completed=False)

            return successMessage("Employee all allowances deactived successfully")

        except Exception as e:
            return exception(e)
    
    def list(self, request, *args, **kwargs):
        
        return successMessage('printed')



class CompensatoryLeavesViewset(viewsets.ModelViewSet):
 permission_classes = [IsAuthenticated]
 def create(self, request, *args, **kwrags):
    try:
        employee_id = decodeToken(request, self.request)['employee_id']
        emp=Employees.objects.get(id=employee_id)
        organization_id = decodeToken(request, self.request)['organization_id']
        request.data['employee'] = employee_id
        team_lead=request.data.get('team_lead',None)
        date=request.data.get('date',None)

        obj1=None
        if team_lead is not None:
                team_lead_query=Employees.objects.filter(id=team_lead,organization=organization_id,is_active=True)
                
                if not team_lead_query.exists():
                    return errorMessage('Team Lead not exists at this id')
                
                obj1=team_lead_query.get()
        
        serializer = CompensatoryLeavesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cc_employee=EmailRecipients.objects.filter(employee__organization=organization_id,level=2,is_active=True)

            if cc_employee.exists():
                eobj=cc_employee.get()
                LeaveRequestEmailsFromEmployees(obj1.name,emp.name,'Compensatory Application Received','Compensatory',obj1.official_email,eobj.employee.official_email,date)
            return successMessageWithData('Leave request added successfully', serializer.data)
        else:
                    return serializerError(serializer.errors)       
    except Exception as e:
            return exception(e)

 def view(self, request, *args, **kwargs):
     try:
         employee_id = decodeToken(request, self.request)['employee_id']
         emp_data = CompensatoryLeave.objects.filter(employee=employee_id, is_active=True)
         serializer =  CompensatoryLeavesSerializer(emp_data, many=True)
         return successMessageWithData('success', serializer.data)
     except Exception as e:
            return exception(e)
        
 def remove(self, request, *args, **kwargs):
    try:
       pk = self.kwargs['pk']
       claim_data = CompensatoryLeave.objects.get(id=pk, is_active=True)
       if claim_data.team_lead_approval == 'pending by team lead':
            claim_data.is_active = False
            claim_data.save()
            return successMessage('Successfully deleted')
       else:
           return errorMessage('You cannot delete at this moment')
    except Exception as e:
        return exception(e)
     
 def teamleadupdate(self, request, *args, **kwargs):
     try:
         pk = self.kwargs['pk']
         status = request.data.get('team_lead_approval')
         if status == 'pending by team lead':
            return errorMessage('Cannot set to pending state')
         
        #  employee_id = decodeToken(request, self.request)['employee_id']
         emp_data = CompensatoryLeave.objects.get(id=pk, is_active=True)
         if emp_data.hr_approval != 'pending by hr':
            return errorMessage('Unable to change state')
         emp_data.team_lead_approval = status
         emp_data.save()
         return successMessage('success')
        #  return successMessage('success')
     except Exception as e:
            return exception(e)
     
 
 def teamleadlist(self, request, *args, **kwargs):
    try:
         employee_id = decodeToken(request, self.request)['employee_id']
         emp_data = CompensatoryLeave.objects.filter(team_lead=employee_id, is_active=True).order_by('-id')
         serializer =  CompensatoryLeavesSerializer(emp_data, many=True)
         return successMessageWithData('success', serializer.data)
    except Exception as e:
            return exception(e)
     
class HRCompensatoryLeavesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOnly]
    def hrupdate(self, request, *args, **kwargs):
     try:
        # pk = self.kwargs['pk']
        organization_id = decodeToken(request, self.request)['organization_id']
        status = request.data.get('hr_approval')
        current_year = datetime.datetime.now().year
        if status == 'pending by hr':
            return errorMessage('Cannot set to pending state')
        
        # year = datetime.now().year
        #  employee_id = decodeToken(request, self.request)['employee_id']
        emp_data = CompensatoryLeave.objects.get(id=self.kwargs['pk'], is_active=True)


        # print(emp_data.hr_approval)
        # leave_calculation = EmployeeLeaveCalculations.objects.filter(employee=emp_data.employee, set_leave_duration__leave_types__title="Compensatory Leaves", is_active=True).first()
        # First, filter manually using related field lookup
        leave_calculation = EmployeeLeaveCalculations.objects.filter(
            employee=emp_data.employee,
            is_active=True,
            date__year=current_year,
            set_leave_duration__leave_types__title="Compensatory Leaves"  # Related lookup
        ).first()

        if leave_calculation:
            leave_calculation = leave_calculation # Use existing record ID
        else:
            # Get a valid `set_leave_duration` object
            set_leave_duration_obj = SetLeavesDuration.objects.filter(
                leave_types__title="Compensatory Leaves",
                year=current_year
            ).first()  

            leave_calculation, created = EmployeeLeaveCalculations.objects.get_or_create(
                employee=emp_data.employee,
                is_active=True,
                date=datetime.datetime.now().date(),
                set_leave_duration=set_leave_duration_obj  # Direct FK object, not a lookup
            )
        # print("Test",leave_calculation)
        leave_duration = SetLeavesDuration.objects.get(leave_types__title="Compensatory Leaves", leave_types__organization=organization_id, year=current_year,is_active=True)
        if emp_data.team_lead_approval == 'rejected by team lead':
            return errorMessage('You cannot approve because team lead has declined the request')
        if emp_data.team_lead_approval == 'pending by team lead':
            return errorMessage('Request is pending by team lead')
       
        if status == 'approved by hr' and emp_data.hr_approval == 'approved by hr':
            return errorMessage('Request already approved')
        if status == 'rejected by hr' and emp_data.hr_approval == 'pending by hr':
            emp_data.hr_approval = status
            emp_data.save()
            return successMessage('Success')
        if status == 'approved by hr':            
            # try:      
            if not leave_calculation is None:
                # print(leave_calculation)
                leave_calculation.emp_yearly_leaves, leave_calculation.remaining_leaves = (leave_calculation.emp_yearly_leaves or 0) + 1, (leave_calculation.remaining_leaves or 0) + 1
                leave_calculation.save()
                emp_data.hr_approval = status
                emp_data.save()
                return successMessage('success')
            else:
            # except EmployeeLeaveCalculations.DoesNotExist:
                data = {
                    'employee': emp_data.employee.id,
                    'set_leave_duration': leave_duration.id,
                    'emp_yearly_leaves': 1,
                    'remaining_leaves':1,
                    'date': datetime.date.today()
                }
                serializer = EmployeeLeaveCalculationsSerializers(data=data)
                if serializer.is_valid():
                    serializer.save()
                    emp_data.hr_approval = status
                    emp_data.save()
                    return successMessage('success')
                else:
                    print('here error')
                    return serializerError(serializer.errors)
        elif status == 'rejected by hr' and emp_data.hr_approval== 'approved by hr':
            #  print('here')
             if not leave_calculation is None:
                # print("test")
                leave_calculation.emp_yearly_leaves, leave_calculation.remaining_leaves = max(0, leave_calculation.emp_yearly_leaves - 1), max(0, leave_calculation.remaining_leaves - 1)
                leave_calculation.save()
                emp_data.hr_approval = status
                emp_data.save()
                return successMessage('success')
        elif status == 'rejected by hr' and emp_data.hr_approval == 'rejected by hr':
            return errorMessage('Request already rejected')
            
            
            
              
        
        #  emp_data.save()
        # serializer =  CompensatoryLeavesSerializer(emp_data)
      
        #  return successMessage('success')
     except Exception as e:
        return exception(e)
     

    def list(self, request, *args, **kwargs):
      try:
         organization_id = decodeToken(request, self.request)['organization_id']
         emp_data = CompensatoryLeave.objects.filter(
    employee__organization=organization_id,
    is_active=True
).exclude(team_lead_approval='rejected by team lead').order_by('-id')
         serializer =  CompensatoryLeavesSerializer(emp_data, many=True)
         return successMessageWithData('success', serializer.data)
      except Exception as e:
            return exception(e)  
