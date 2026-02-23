import json
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .serializers import *
from helpers.status_messages import *
from .models import *
from django.db import connection
from organizations.models import Organization
from .views_emp_routers import *
from departments.models import Departments
from departments.serializers import DepartmentsSerializers
from positions.models import Positions
from positions.serializers import PositionsSerializers
from organizations.models import StaffClassification
from organizations.serializers import StaffClassificationSerializers
from helpers.get_org import userOrganizationChecks
from helpers.decode_token import decodeToken
from companies.models import EmployeeWorkExperience
from companies.serializers import EmployeeWorkExperienceViewsetSerializers
from skills.models import EmployeeSkills
from skills.serializers import EmployeeSkillsViewsetSerializers
from institutes.models import EmployeeEducations
from institutes.serializers import EmployeeEducationsViewsetSerializers
from banks.models import EmployeeBankDetails
from banks.serializers import EmployeeBankDetailsViewsetSerializers
from logs.views import UserLoginLogsViewset
from profiles_api.serializers_users import HrmsUserEmployeesRegisterationSerializers
from profiles_api.utils import Util
import uuid
from django.db.models import Max
from profiles_api.models import HrmsUsers
from django.contrib.auth.hashers import make_password
from profiles_api.serializers import HrmsUserChangePasswordSerializer
from reimbursements.models import *
from reimbursements.serializers import *
from email_templates.models import EmailTemplates, TemplateVariables
import csv
import os
import datetime
# Create your views here.


class EmployeeViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def employee_report(self,request,*args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            data=custom_query(organization_id)
            return successMessageWithData('Success',data)

        except Exception as e:
            return exception(e)   

    # only admin could list all the employee
    def list(self, request, *args, **kwargs):
        try:      
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
            org_id = user_organization.id

            query = Employees.objects.filter(organization=org_id).order_by('id')
            active_employees = query.filter(is_active = True)
            deactive_employees = query.filter(is_active = False)
            
            active_serializer = ListEmployeeViewsetSerializers(active_employees, many=True)
            deactive_serializer = ListEmployeeViewsetSerializers(deactive_employees, many=True)

            data = {'active_employees': active_serializer.data, 'deactive_employees': deactive_serializer.data}
            return success(data)
        except Exception as e:
            return exception(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            org_obj = UserLoginLogsViewset().userOrganization(request.user)
            org_id = org_obj.id

            # checks if organization exists at this id or not
            emp_uuid = self.kwargs['uuid']
            emp_query =  Employees.objects.filter(uuid=emp_uuid)
            if not emp_query.exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Employee does not exists', 'system_status_message': ''})

            if emp_query.filter(is_active=False):
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Employee is deactive', 'system_status_message': ''})

            if not emp_query.filter(organization = org_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Admin and Employee does not belong to the same organization', 'system_status_message': ''})

            emp = Employees.objects.get(uuid=emp_uuid, is_active=True)

            serializer = ListEmployeeViewsetSerializers(emp, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def emp_required_fields(self, request, *args, **kwargs):
        try:
            org_obj = UserLoginLogsViewset().userOrganization(request.user)
            org_id = org_obj.id

            # checks if organization exists at this id or not
            pk = self.kwargs['pk']
            emp_query =  Employees.objects.filter(id=pk)
            if not emp_query.exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Employee does not exists', 'system_status_message': ''})

            if emp_query.filter(is_active=False):
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Employee is deactive', 'system_status_message': ''})

            if not emp_query.filter(organization = org_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Admin and Employee does not belong to the same organization', 'system_status_message': ''})

            emp = Employees.objects.get(id=pk, is_active=True)

            serializer = ListEmployeeRequiredFieldsViewsetSerializers(emp, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def create(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            org_obj = UserLoginLogsViewset().userOrganization(request.user)
            org_id = org_obj.id
            errors = '' 
            
            if 'cnic_no' in request.data and 'first_name' in request.data and 'last_name' in request.data:
                request.data._mutable = True
                request.data['created_by'] = user_id
                request.data['is_active'] = True
                request.data['organization'] = org_id
                
                # code should be unique organization based
                is_unique = False
                iteration = 0
                while is_unique != True:
                    unique_code = str(uuid.uuid4())[:8]  
                    if not Employees.objects.filter(code=unique_code, organization=org_id).exists(): 
                        request.data['code'] = unique_code
                        is_unique=True
                        break    
                    iteration = iteration + 1
                    if iteration == 100:
                        break
                
                if is_unique == False:
                    return errorMessage('Employee unique code cannot be generated')

                # generation unique employee id:
                seed = 1000
                max_code = Employees.objects.filter(organization=org_id).aggregate(max_code=Max('emp_code'))['max_code']
                if max_code == None:
                    max_code = seed
                max_emp_code = max_code + 1
                request.data['emp_code'] = max_emp_code

                request.data['name'] = request.data['first_name'] + ' ' + request.data['last_name']
                
                
                request.data._mutable = False

            else:
                return errorMessage("CNIC number, first name and last name is required field check if you are missing something")
      
    
            # Getting CNIC from the user
            cnic = None
            if 'cnic_no' in request.data:
                cnic = request.data.get('cnic_no')

            # if employees cnic or email already exists in that particular organization
            if Employees.objects.filter(organization=org_id, cnic_no=cnic).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Employee already exists. CNIC already in use', 'system_status_message': ''})

            # Employee Data
            serializer = PersonalEmployeeViewsetSerializers(data=request.data)

            if not serializer.is_valid():
                return serializerError(serializer.errors)

            
            
            emp = serializer.save()
            emp_id = emp.id

            # Both variables will be used for the response messages
            cnic_error = 0
            passport_error = 0

            # cnic data
            cnic_data_array = self.cnicFieldsArray(request.data)
            cnic_data_array['employee'] = emp_id
            cnic_data_array['cnic'] = emp.cnic_no
            serializer_cnic = EmployeeCnicSerializers(data=cnic_data_array)
            if not serializer_cnic.is_valid():
                errors = str(serializer_cnic.errors) 
                cnic_error = 1
            if cnic_error == 0:
                serializer_cnic.save()

            # passport data
            passport_no = None
            if 'passport_no' in request.data:
                passport_no = request.data.get('passport_no')
            if passport_no is not None:
                passport_data_array = self.passportFieldsArray(request.data)
                passport_data_array['employee'] = emp_id
                serializer_passport = EmployeePassportSerializers(data=passport_data_array)
                # if passport data is invalid
                if not serializer_passport.is_valid():
                    errors += str(serializer_passport.errors)
                    passport_error = 1

                if passport_error == 0:
                    serializer_passport.save()
            elif passport_no is None:
                passport_error = 2

            # Getting the appropriate message
            if errors is not None:
                message = self.isDataProcessed(cnic_error, passport_error)   
            else:
                message = self.isDataProcessed(cnic_error, passport_error)
            # Getting the Employee Data
            emp = Employees.objects.get(id=emp_id)
            emp_serializer = ListEmployeeViewsetSerializers(emp, many=False)
            data = {'emp_data': emp_serializer.data}

            return Response({'status': 200, 'system_status': 201, 'data': data, 'message': message, 'system_status_message': errors})

        except Exception as e:
            return exception(e)

    def patch(self, request, *args, **kwargs):
        try:
            uuid = self.kwargs['uuid']
            org_obj = UserLoginLogsViewset().userOrganization(request.user)
            org_id = org_obj.id
            # checks if employee exists at this id or not
            if not Employees.objects.filter(uuid=uuid).exists():
                return nonexistent(var='Employee')
            if not Employees.objects.filter(uuid=uuid, organization=org_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'message': 'Employee and admin does not belong to the same organization', 'data': '', 'system_status_message': ''})


            obj = Employees.objects.get(uuid=uuid)
            official_email = None
            emp_id = None
            module = 'office'
            if 'module' in request.data:
                module = request.data.get('module')

            if module == 'office':
                if 'emp_code' in request.data:
                    emp_code = request.data['emp_code']
                    if Employees.objects.filter(emp_code=emp_code, organization=org_id).exists(): 
                       return errorMessage('This employee code already exists')

                if 'official_email' in request.data:
                    official_email = request.data['official_email'].lower()
                    request.data['official_email'] = official_email

                office_serializer = OfficeEmployeeViewsetSerializers(obj, data=request.data, partial=True)
                if not office_serializer.is_valid():
                    return serializerError(office_serializer.errors)
                
                # Register employee in HRM system and saving data
                if official_email:
                    if obj.official_email != official_email:
                        registered_user = isEmployeeRegisteredHrmsUser(self, obj, request.data)
                        if registered_user['status'] == 400:
                            return Response(registered_user)
                        obj.hrmsuser = registered_user['data']
                        obj.save()
                 
                
                emp = office_serializer.save()
                emp_id = emp.id
            elif module == 'personal':
                # Editing personal data
                personal_serializer = PersonalEmployeeViewsetSerializers(obj, data=request.data, partial=True)
                if not personal_serializer.is_valid():
                    return serializerError(personal_serializer.errors)
                emp = personal_serializer.save()
                emp_id = emp.id

                #TODO in a function
                if 'first_name' or 'last_name' in request.data:
                    # updating the name of employee
                    if 'first_name' in request.data and 'last_name' in request.data:
                        emp.name = request.data['first_name'] + ' ' + request.data['last_name']
                    elif 'first_name' in request.data and 'last_name' not in request.data:
                        emp.name = request.data['first_name'] + ' ' + emp.last_name
                    elif 'first_name' not in request.data and 'last_name' in request.data:
                        emp.name = emp.first_name + ' ' + request.data['last_name']

                    emp.save()

                    # Updating first name or last name of hrmsuser
                    hrmsuser = HrmsUsers.objects.filter(email=obj.official_email)
                    if hrmsuser.exists():
                        hrmsuser_obj = hrmsuser.first()
                        if 'first_name' in request.data:
                            hrmsuser.first_name = request.data['first_name']
                        if 'last_name' in request.data:
                            hrmsuser.last_name = request.data['last_name']
                        hrmsuser_obj.save()

                # cnic data
                try:
                    cnic_obj = EmployeeCnic.objects.get(employee_id=emp_id)
                except EmployeeCnic.DoesNotExist:
                    cnic_obj = None
                
                if cnic_obj is None:
                    request.data._mutable = True
                    request.data['cnic'] = request.data['cnic_no']
                    request.data['employee'] = emp_id
                    serializer_cnic = EmployeeCnicSerializers(data=request.data)
                else: 
                    serializer_cnic = EmployeeCnicSerializers(cnic_obj, data=request.data, partial=True)
                if not serializer_cnic.is_valid():
                    return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Employee CNIC SerializerError', 'system_status_message': serializer_cnic.errors})
                serializer_cnic.save()

                # passport data
                passport_obj = None
                
                if EmployeePassports.objects.filter(employee=emp_id, is_active=True).exists():
                    passport_obj = EmployeePassports.objects.get(employee=emp_id, is_active=True)
                passport_no = None
                if 'passport_no' in request.data:
                    passport_no = request.data.get('passport_no')
                    

                # This will update passport data
                if passport_obj is not None:
                    serializer_passport = EmployeePassportSerializers(
                        passport_obj, data=request.data, partial=True)
                    if not serializer_passport.is_valid():
                        return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Employee Passport SerializerError', 'system_status_message': serializer_passport.errors})
                    serializer_passport.save()

                # if passport data does not exists
                elif passport_obj is None:
                    # This will create the passport data
                    if passport_no is not None:
                        passport_data_array = self.passportFieldsArray(request.data)
                        passport_data_array['employee'] = emp_id
                        serializer_passport = EmployeePassportSerializers(data=passport_data_array)
                        if not serializer_passport.is_valid():
                            return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Employee Passport SerializerError', 'system_status_message': serializer_passport.errors})
                        serializer_passport.save()
                    else:
                        print('passport no is none')
            # Getting the Employee Data
            emp = Employees.objects.get(id=emp_id)
            emp_serializer = ListEmployeeViewsetSerializers(emp, many=False)

            data = {'emp_data': emp_serializer.data}

            return Response({'status': 200, 'system_status': 200, 'data': data, 'message': 'Successfully updated', 'system_status_message': ''})

        except Exception as e:
            return exception(e)

    def delete(self, request, *args, **kwargs):
        try:
            org_obj = UserLoginLogsViewset().userOrganization(request.user)
            org_id = org_obj.id
            
            if request.user.is_admin == False:
                return errorMessage('User is not an admin user')


            # checks if employee exists
            emp_uuid = self.kwargs['uuid']
            emp_query = Employees.objects.filter(uuid=emp_uuid)
            if not emp_query.exists():
                return nonexistent(var='Employee')
            if not emp_query.filter(uuid=emp_uuid, organization=org_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Admin and employee does not belong to the same organization', 'system_status_message': ''})
                
            emp = Employees.objects.get(uuid=emp_uuid)

            org_id = emp.organization.id

            # if Employee is already deactivated
            if emp.is_active == False:
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Employee is already deactivated', 'system_status_message': ''})

            emp.is_active = False
            # hrms user will get deactivated if employee get deactivated
            hrmsuser = HrmsUsers.objects.filter(email=emp.official_email)
            if hrmsuser.exists():
                hrmsuser_obj = hrmsuser.first()
                hrmsuser_obj.is_active = False
                hrmsuser_obj.save()
            emp.save()

            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT, 'data': '', 'message': 'Employee got deactivated successfully', 'system_status_message': ''})
        except Exception as e:
            return exception(e)

    def activate(self, request, *args, **kwargs):
        try:
            org_obj = UserLoginLogsViewset().userOrganization(request.user)
            org_id = org_obj.id
            
            if request.user.is_admin == False:
                return errorMessage('User is not an admin user')


            # checks if employee exists
            emp_uuid = self.kwargs['uuid']
            emp_query = Employees.objects.filter(uuid=emp_uuid)
            if not emp_query.exists():
                return nonexistent(var='Employee')
            if not emp_query.filter(uuid=emp_uuid, organization=org_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Admin and employee does not belong to the same organization', 'system_status_message': ''})
                
            emp = Employees.objects.get(uuid=emp_uuid)

            org_id = emp.organization.id

            # if Employee is already deactivated
            if emp.is_active == True:
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Employee is already activated', 'system_status_message': ''})

            emp.is_active = True
            # hrms user will get deactivated if employee get deactivated
            hrmsuser = HrmsUsers.objects.filter(email=emp.official_email)
            if hrmsuser.exists():
                hrmsuser_obj = hrmsuser.first()
                hrmsuser_obj.is_active = True
                hrmsuser_obj.save()
            emp.save()

            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT, 'data': '', 'message': 'Employee activated successfully', 'system_status_message': ''})
        except Exception as e:
            return exception(e)



    def organizationCheck(self, user_id, org_id):
        # checks if active organization exists or not
        try: 
            organization = Organization.objects.filter(id=org_id, is_active=True)
            if not organization.exists():
                return {'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Organization does not exist', 'system_status_message': ''}

            hrmsuser = HrmsUsers.objects.get(id=user_id)

            if hrmsuser.is_admin == True:
                if not organization.filter(user__id=user_id).exists():
                    return {'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Admin does not belong to this organization', 'system_status_message': ''}

            return {'status': 200, 'data': organization}
        except Exception as e:
            return {'status': 400, 'message': str(e)}
    # This function is used to get appropriate status messages

    def isDataProcessed(self, cnic_err, passport_err):
        try:
            msg = ''
            if cnic_err == 1 and passport_err == 1:
                msg = 'Cnic data and Passort data is unprocessed'
            elif cnic_err == 1 and passport_err == 0:
                msg = 'Passport and Employee data processed Successfully. Cnic data is unprocessed'
            elif cnic_err == 0 and passport_err == 1:
                msg = 'Cnic and Employee data processed successfully. Passort data is unprocessed'
            elif cnic_err == 0 and passport_err == 0:
                msg = 'All data processed successfully'
            elif cnic_err == 0 and passport_err == 2:
                msg = 'All data processed successfully. No Passport data is inserted'

            return msg
        except Exception as e:
            return str(e)

    def passportFieldsArray(self, passport_data):
        try:
            passport_data_dict = {
                'employee': '',
                'passport_no': '',
                # 'date_of_issue': None,
                'date_of_expiry': None,
                # 'tracking_no': '',
                # 'booklet_no': '',
                # 'country_code': '',
                # 'passport_type': '',
                # 'issuing_authority': '',
                # 'attachment': None
            }

            for key in passport_data_dict:
                if passport_data.get(key):
                    if passport_data.get(key) != '':
                        passport_data_dict[key] = passport_data.get(key, None)

            return passport_data_dict
        except Exception as e:
            return str(e)

    def cnicFieldsArray(self, cnic_data):
        try:
            cnic_data_dict = {
                'employee': '',
                'cnic': '',
                # 'date_of_issue': None,
                # 'front_image': None,
                # 'back_image': None
            }

            for key in cnic_data_dict:
                if cnic_data.get(key):
                    if cnic_data.get(key) != '':
                        cnic_data_dict[key] = cnic_data.get(key, None)

            return cnic_data_dict
        except Exception as e:
            return str(e)

    



# This API returns org data, staff data, position data and employ type data against organization
class PreEmployeesDataView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            org_id = self.kwargs['org_id']
            
            if org_id is not None:
                if Organization.objects.filter(id=org_id).exists():
                    org = Organization.objects.get(id=org_id)
                    if org.is_active == False:
                        return Response({'status': 400, 'system_status': 400, 'data': '', 'message': "Activate the Organization first", 'system_error_message': ''})

                    position_obj = Positions.objects.filter(staff_classification__organization__id=org_id, is_active=True)
                    if not position_obj.exists():
                        return Response({'status': 400, 'system_status': 400, 'data': '', 'message': "No active Position exists", 'system_error_message': ''})
                    position_serializer = PositionsSerializers(position_obj, many=True)

                    department_obj = Departments.objects.filter(grouphead__organization__id=org_id, is_active=True)
                    if not department_obj.exists():
                        return Response({'status': 400, 'system_status': 400, 'data': '', 'message': "No active Department exists", 'system_error_message': ''})
                    department_serializer = DepartmentsSerializers(department_obj, many=True)

                    staff_obj = StaffClassification.objects.filter(organization__id=org_id, is_active=True)
                    if not staff_obj.exists():
                        return Response({'status': 400, 'system_status': 400, 'data': '', 'message': "No active Staff Classification exists", 'system_error_message': ''})
                    staff_serializer = StaffClassificationSerializers(staff_obj, many=True)
                    
                    emp_types_obj = EmployeeTypes.objects.filter(is_active=True)
                    emp_types_serializer = EmployeeTypesViewsetSerializers(emp_types_obj, many=True)
                    
                    data = {'staff_classification': staff_serializer.data, 'department': department_serializer.data, 'position': position_serializer.data, 'employee_types': emp_types_serializer.data}
                    return Response({'status': 200, 'system_status': 200, 'data': data, 'message': "Success", 'system_error_message': ''})
            else:
                return Response({'status': 400, 'system_status': 404, 'data': '', 'message': "Organization does not exist at this index", 'system_error_message': ''})

        except Exception as e:
            return exception(e)

    def pre_data(self, organization_id, user_id, role):
        try:
            # data = HrmsUsers.objects.filter(is_active=True, is_admin=True, pk=request.user.id)
            data = HrmsUsers.objects.filter(is_active=True, is_admin=True, id=user_id)
            serializer = PreDataEmployeeSerializers(data, many=True)
            return serializer.data
        except Exception as e:
            return []



class EmployeeImportDataView(viewsets.ModelViewSet):

    def update_import_employee_data(self, request, *args, **kwargs):
        try:
            # file_name = "kavtech-employee-updated-data.csv"
            # file_path = os.path.join('static/import/employees/', file_name)
            # emp_active = Employees.objects.filter(organization=4, is_active=True).count()
            # emp_deactive = Employees.objects.filter(organization=4, is_active=False).count()
            # with open(file_path, 'r') as csvfile:
            #     reader = csv.reader(csvfile)
            #     i=0
            #     for row in reader:
            #         if i==0:
            #             i+=1
            #             continue

            #         emp = Employees.objects.filter(cnic_no=row[7].strip(), organization=4, is_active=True)
            #         if not emp.exists():
            #             continue
            #         emp = emp.first()

            #         staff_classification = StaffClassification.objects.filter(title=row[3].strip(), organization=4)
            #         if staff_classification.exists():
            #             staff_classification = staff_classification.first()
            #             staff_classification_id = staff_classification.id
            #         else:
            #             continue

            #         employee_type = EmployeeTypes.objects.filter(title=row[4].strip())
            #         if employee_type.exists():
            #             employee_type = employee_type.first()
            #             employee_type_id = employee_type.id
            #         else:
            #             continue

            #         employee_data = {
            #             'staff_classification': staff_classification_id,
            #             'employee_type': employee_type_id,
            #             'current_salary': 1,
            #         }

            #         serializer = OfficeEmployeeViewsetSerializers(emp, data = employee_data, partial=True)
            #         if serializer.is_valid():
            #             serializer.save()
            #         else:
            #             continue
                    
            
            # data = {
            #     'employee_data': employee_data,
            #     'emp_active': emp_active,
            #     'emp_deactive': emp_deactive

                    
            # }
            # return success(data)    
            pass

        except Exception as e:
            return exception(e)

    
    def temp_queries(self, request, *args, **kwargs):
        try:
            # return successMessage('This API is for temp queries')
            organization_id = 4
            
            print('Success Message')
            emp = Employees.objects.filter(
                official_email = 'tayyab.sarwar@kavmails.net',
                organization=organization_id, 
                
            )

            # hrmsuser = HrmsUsers.objects.get(email='tayyab.sarwar@kavmails.net')

            emp = emp.first()
            temp_password = str(uuid.uuid4())[:8]   
            user_data_array = {
                'first_name': emp.first_name,
                'last_name': emp.last_name,
                'email': emp.official_email,
                'password': temp_password,
                'password2': temp_password
            }
            user_serializer = HrmsUserEmployeesRegisterationSerializers(data=user_data_array)
            if not user_serializer.is_valid():
                return serializerError(user_serializer.errors)
            hrms_user_data = user_serializer.save()

            emp.hrmsuser = hrms_user_data
            emp.save()

            change_password = {
                'password': temp_password,
                'password2': temp_password,
            }

            serializer = HrmsUserChangePasswordSerializer(data=change_password, context={'hrms_user':hrms_user_data})
            if not serializer.is_valid():
                return serializerError(serializer.errors)

            body = 'Your temporary password is ' + temp_password + '. Your email is ' + emp.official_email 
            data = {
                'subject': 'Account Created',
                'body':  body,
                'to_email': 'asma.zahid@kavmails.net',
            }
        
            Util.send_email(data)

            return Response({
                'status': 200,
                'message': 'success'
            })



            # file_name = "haly-tower-employees.csv"
            # file_path = os.path.join('static/import/employees/', file_name)

            # with open(file_path, 'r') as csvfile:
            #     reader = csv.reader(csvfile)
            #     i=0
            #     for row in reader:
            #         if i==0:
            #             i+=1
            #             continue

                    # official_email = None #row[0]

            # email_templates = EmailTemplates.objects.filter(uuid="12bfd0ec-dd71-4057-a4bc-9e3e1fef3cfb")
            # email_template = email_templates.get()

            # emp_query = Employees.objects.filter(
            #     uuid = '365d5193-b7df-4174-91a1-751c9d01fbd4',
            #     # official_email = official_email,
            #     organization = 12,  
            #     is_active = True
            # )
        
            # if emp_query.exists():
            #     emp = emp_query.get()
            #     if not emp.last_name:
            #         emp.last_name = ''
                
            #     temp_password = str(uuid.uuid4())[:8]   
            #     user_data_array = {
            #         'first_name': emp.first_name,
            #         'last_name': emp.last_name,
            #         'email': emp.official_email,
            #         'password': temp_password,
            #         'password2': temp_password
            #     }
            #     user_serializer = HrmsUserEmployeesRegisterationSerializers(data=user_data_array)
            #     if not user_serializer.is_valid():
            #         return serializerError(user_serializer.errors)
            #     hrms_user_data = user_serializer.save()

                # send email to the employee with the temporary password
                
            # data = {
            #     'subject': email_template.subject_line,
            #     'body':  email_template.body,
            #     'to_email': 'testemail@mailinator.com',
            # }
            # Util.send_email(data)
            # # emp.hrmsuser = hrms_user_data 
            # return success('Successfully email created')
            # else:
            #     return errorMessage('Employee does not exists')




            # emp_query = Employees.objects.filter(organization=4, is_active=True)
            # if not emp_query.exists():
            #     return errorMessage('Employee does not exists')
            
           
            # for emp in emp_query:
            #     pass
                    
        
            # emp = Employees.objects.get(official_email='haider.cheema@kavmails.net', organization=4)
            # emp.hrmsuser = hrmsuser
            # emp.save()
            

            # temp_password = str(uuid.uuid4())[:8]   
            # user_data_array = {
            #     'first_name': emp_data.first_name,
            #     'last_name': emp_data.last_name,
            #     'email': emp_data.official_email,
            #     'password': temp_password,
            #     'password2': temp_password
            # }
            # user_serializer = HrmsUserEmployeesRegisterationSerializers(data=user_data_array)
            # if not user_serializer.is_valid():
            #     return serializerError(user_serializer.errors)
            # hrms_user_data = user_serializer.save()

            # # send email to the employee with the temporary password
            # body = 'Your temporary password is ' + temp_password + '. Your email is ' + emp_data.official_email
            # data = {
            #     'subject': 'Congratulations, You are now part of hrms user.',
            #     'body':  body,
            #     'to_email': emp_data.official_email,
            # }
            # Util.send_email(data)
            # emp_data.hrmsuser = hrms_user_data 
            # return success(hrms_user_data)



            
            # temp_password = str(uuid.uuid4())[:8]   
            # user_data_array = {
            #     'first_name': emp_data.first_name,
            #     'last_name': emp_data.last_name,
            #     'email': emp_data.official_email,
            #     'password': temp_password,
            #     'password2': temp_password
            # }
            # user_serializer = HrmsUserEmployeesRegisterationSerializers(data=user_data_array)
            # if not user_serializer.is_valid():
            #     return serializerError(user_serializer.errors)
            # hrms_user_data = user_serializer.save()

            # # send email to the employee with the temporary password
            # body = 'Your temporary password is ' + temp_password + '. Your email is ' + emp_data.official_email
            # data = {
            #     'subject': 'Congratulations, You are now part of hrms user.',
            #     'body':  body,
            #     'to_email': emp_data.official_email,
            # }
            # Util.send_email(data)
            # emp_data.hrmsuser = hrms_user_data 
            # return success(hrms_user_data)
            # return successMessage('Successfully updated')



















            # changing status:


            # changed_status = 'in-progress'
            # prev_status = 'un-processed'

            # emp_gym = EmployeesGymAllowance.objects.filter(status=prev_status)
            # emp_gym_count = emp_gym.count()
            # a = 0 ; b = 0
            # for gym in emp_gym:
            #     if gym.status == prev_status:
            #         gym.status = changed_status
            #         gym.save()
            #         a+=1

            # emp_medical = EmployeesMedicalAllowance.objects.filter(status=prev_status)
            # emp_medical_count = emp_medical.count()

            # for medical in emp_medical:
            #     if medical.status == prev_status:
            #         medical.status = changed_status
            #         medical.save()
            #         b+=1

            # emp_loan = EmployeesLoan.objects.filter(status=prev_status)
            # emp_loan_count = emp_loan.count()

            # for loan in emp_loan:
            #     if loan.status == prev_status:
            #         loan.status = changed_status
            #         loan.save()

            # emp_pf = EmployeeProvidentFunds.objects.filter(status=prev_status)
            # emp_pf_count = emp_pf.count()

            # for pf in emp_pf:
            #     if pf.status == prev_status:
            #         pf.status = changed_status
            #         pf.save()

            # emp_leaves = EmployeesLeaves.objects.filter(status=prev_status)
            # emp_leaves_count = emp_leaves.count()

            # for leaves in emp_leaves:
            #     if leaves.status == prev_status:
            #         leaves.status = changed_status
            #         leaves.save()
                    
            # data = {
            #     'emp_gym_count': emp_gym_count, 
            #     'emp_medical_count': emp_medical_count,
            #     'emp_loan_count': emp_loan_count,
            #     'emp_pf_count': emp_pf_count,
            #     'emp_leaves_count': emp_leaves_count,
            #     'a': a,
            #     'b': b
            # }

            # return success(data)

            # change password API:


            # hrmsuser = HrmsUsers.objects.get(email = "ahmed.amjad@kavmails.net")
            # # return successMessageWithData('data', hrmsuser)
            # # new_password = request.data.get('password')
            # # hashed_password = make_password(new_password)
            # # hrmsuser.password = hashed_password
            # # hrmsuser.save()
            # # return successMessageWithData('success', hashed_password)
            
            # serializer = HrmsUserChangePasswordSerializer(data=request.data, context={'hrms_user':hrmsuser})
            # if serializer.is_valid():
            #     return successMessage('Password changed successfully')
            # else:
            #     return serializerError(serializer.errors)
            
            
            # changing email address to lower case
                 
            # hrmsuser = HrmsUsers.objects.filter()
            # hrmsuser_list = []
            # lowercase_email = []
            # for hrms in hrmsuser:
            #     is_capital = False
            #     if hrms.email:
            #         for letter in hrms.email:
            #             if 64 < ord(letter) <= 90:
            #                 hrmsuser_list.append(hrms.email)
            #                 is_capital = True
            #                 break
                        
            #         if is_capital:
            #             hrms.email = hrms.email.lower()
            #             lowercase_email.append(hrms.email)
            #             hrms.save()


            # data = {'hrmsuser_list': hrmsuser_list, 'hrmsuser_lower_list': lowercase_email}
            # return successMessageWithData(data, 'hrmsuser email')
       

        # password and email

        #    emp = Employees.objects.get(official_email=hrmsuser.email)

        #    hrmsuser.email = 'asmazahid394394@gmaik.net'
        #    emp.official_email = hrmsuser.email
        #    hrmsuser.save()
        #    emp.save()
        #    return successMessage('Changed Successfully')
            # hrmsuser_null = emp.filter(hrmsuser__isnull=True).count()
            # hrmsuser_not_null = emp.filter(hrmsuser__isnull=False)
            # hrmsuser_not_null_count = hrmsuser_not_null.count()
            # hrmsuser_not_null_emails = []
            # for email in hrmsuser_not_null:
            #     if email.hrmsuser:
            #         hrmsuser_not_null_emails.append(email.hrmsuser.email)

            # emp_data_query = Employees.objects.filter(organization=4, official_email='hammad.ansar@kavmails.net', is_active=True)
            # if not emp_data_query.exists():
            #     return errorMessage('Employee does not exists')
            # emp_data = emp_data_query.get()

            # if HrmsUsers.objects.filter(email=emp_data.official_email).exists():
            #     return errorMessage('This employee is already part of hrms system')

            # hrmsuser = HrmsUsers.objects.get(email='hammad.ansar@kavmails.net')
        
            # emp = Employees.objects.get(official_email='hammad.ansar@kavmails.net', organization=4)
            # emp.hrmsuser = hrmsuser
            # emp.save()
            # hrmsuser.email = 'asma_zahid9876543210@hrms.com'
            # hrmsuser.save()
            # hrmsuser = HrmsUsers.objects.get(email='hammad.ansar@kavmails.net')
            # hrmsuser.email = 'hammad_ansar@mailinator.net'
            # hrmsuser.save()
            
            
            # temp_password = str(uuid.uuid4())[:8]   
            # user_data_array = {
            #     'first_name': emp_data.first_name,
            #     'last_name': emp_data.last_name,
            #     'email': emp_data.official_email,
            #     'password': temp_password,
            #     'password2': temp_password
            # }
            # user_serializer = HrmsUserEmployeesRegisterationSerializers(data=user_data_array)
            # if not user_serializer.is_valid():
            #     return serializerError(user_serializer.errors)
            # hrms_user_data = user_serializer.save()

            # # send email to the employee with the temporary password
            # body = 'Your temporary password is ' + temp_password + '. Your email is ' + emp_data.official_email
            # data = {
            #     'subject': 'Congratulations, You are now part of hrms user.',
            #     'body':  body,
            #     'to_email': emp_data.official_email,
            # }
            # Util.send_email(data)
            # emp_data.hrmsuser = hrms_user_data 
            # return success(hrms_user_data)
            # return successMessage('Successfully updated')
        except Exception as e:
            return exception(e)

    def import_employee(self, request, *args, **kwargs):
        try:
            pass
            # file_name = "kavtech-employee-data.csv"
            # file_path = os.path.join('static/import/employees/', file_name)

            # with open(file_path, 'r') as csvfile:
            #     reader = csv.reader(csvfile)
            #     i=0
            #     for row in reader:
            #         if i==0:
            #             i+=1
            #             continue

            #         user_id = request.user.id
            #         org_obj = UserLoginLogsViewset().userOrganization(request.user)
            #         org_id = org_obj.id
            #         errors = ''
            #         if Employees.objects.filter(organization=org_id, cnic_no=row[7]).exists():
            #             continue

            #         # generation unique employee id:
            #         seed = 1000
            #         max_code = Employees.objects.filter(organization=org_id).aggregate(max_code=Max('emp_code'))['max_code']
            #         if max_code == None:
            #             max_code = seed
            #         max_emp_code = max_code + 1

            #         gender = row[3]
                    
            #         if gender=='Male':
            #             gender_choice = 1
            #         else:
            #             gender_choices = 2  
                    
            #         martial_str = row[8]
            #         if martial_str=='Single':
            #             martial_status = 1
            #         else:
            #             martial_status = 2

            #         str_dob = row[2]
            #         dob = datetime.datetime.strptime(str_dob, '%m/%d/%Y').date()
            #         str_join = row[9]
            #         joining_date = datetime.datetime.strptime(str_join, '%m/%d/%Y').date()
            #         employee_data = {
            #             'organization': org_id,
            #             'created_by': user_id,
            #             'first_name': row[0].strip(), 
            #             'last_name':'', 
            #             'cnic_no':row[7].strip(), 
            #             'father_name':row[5].strip(), 
            #             'gender':gender_choice, 
            #             'dob': dob, 
            #             'emp_code':max_emp_code, 
            #             'official_email':row[6].strip(),
            #             'personal_email':row[6].strip(), 
            #             'marital_status':martial_status, 
            #             'joining_date':joining_date
            #         }
            #         # ImportEmployeeSerializers
            #         serializer = ImportEmployeeSerializers(data = employee_data)
            #         if serializer.is_valid():
            #             serializer.save()
            #         else:
            #             print(row[7])

            # return successMessage('successfully read')
        except Exception as e:
            return exception(e)


    # def update_employee_data(self, request, *args, **kwargs):
    #     try:
    #         # user_id = request.user.id
    #         # org_obj = UserLoginLogsViewset().userOrganization(request.user)
    #         # org_id = org_obj.id

    #         # employees = Employees.objects.filter(organization=org_id, is_active=True)
    
    #         # for emp in employees:
    #         #     if emp.first_name is None:
    #         #         continue
    #         #     name = emp.first_name
    #         #     if emp.last_name is not None:
    #         #         name += ' '+emp.last_name
    #         #     emp.name = name
    #         #     emp.save()
    #         user_id = request.user.id
    #         org_obj = UserLoginLogsViewset().userOrganization(request.user)
    #         org_id = org_obj.id
    #         emp_query = Employees.objects.filter(is_active=True, organization=org_id)
            
    #         i=0
    #         j=0
    #         for emp in emp_query:
    #             if EmployeeCnic.objects.filter(employee=emp.id, cnic=emp.cnic_no).exists():
    #                 print("hellow")
    #                 i+=1
    #                 continue
    #             emp_cnic_data = EmployeeCnic.objects.create(
    #                 employee = emp,
    #                 cnic = emp.cnic_no,
    #                 is_active=True
    #             )
    #             emp_cnic_data.save()
    #             j+=1

    #         return successMessage(str(i) + " " + str(j))

    #     except Exception as e:
    #         return exception(e)



class PreEmployeesCompleteDataView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]


    

    def get(self, request, *args, **kwargs):
        try:
            result_data = {'employee':[], 'employee_contacts': None, 'employee_bank': None, 'employee_dependents': None, 'employee_companies': None, 'employee_education': None, 'employee_skills': None, 'employee_project_roles': None}
            emp_uuid = self.kwargs['emp_uuid']
            organization_id = decodeToken(self, request)['organization_id']
            
            if not Employees.objects.filter(uuid=emp_uuid).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Employee does not exists', 'system_status_message': ''})
            
            if not Employees.objects.filter(uuid=emp_uuid, is_active=True).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Employee is not active', 'system_status_message': ''})
            
            emp = Employees.objects.get(uuid=emp_uuid)

            emp_org_id = self.get_org_id_from_emp(emp_uuid)

            if emp_org_id != organization_id:
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Admin user does not belong to this organization', 'system_status_message': ''})

            # This will fetch employee personal, office, cnic and passport data 
            emp_obj = Employees.objects.filter(uuid=emp_uuid, organization__id=organization_id, is_active=True)
            if emp_obj.exists(): 
                emp_obj_data =  Employees.objects.get(uuid=emp_uuid, organization__id=organization_id, is_active=True)
                emp_serializer = ListEmployeeViewsetSerializers(emp_obj_data)
                result_data['employee'] = emp_serializer.data

            emp_contact_obj = EmployeeEmergencyContacts.objects.filter(employee=emp.id, employee__organization__id=organization_id, is_active=True).order_by('-id')
            if emp_contact_obj.exists():
                emp_contact_serializer = EmployeeEmergencyContactsViewsetSerializers(emp_contact_obj, many=True)
                result_data['employee_contacts'] = emp_contact_serializer.data    
                
            emp_bank_obj = EmployeeBankDetails.objects.filter(employee=emp.id, employee__organization__id=organization_id, is_active=True).order_by('bank__name')
            if emp_bank_obj.exists():
                emp_bank_serializer = EmployeeBankDetailsViewsetSerializers(emp_bank_obj, many=True)
                result_data['employee_bank'] = emp_bank_serializer.data


            emp_dependent_obj = EmployeeDependent.objects.filter(employee=emp.id, employee__organization__id=organization_id, is_active=True).order_by('-id')
            if emp_dependent_obj.exists():
                emp_dependent_serializer = EmployeeDependentViewsetSerializers(emp_dependent_obj, many=True)
                result_data['employee_dependents'] = emp_dependent_serializer.data
                
            emp_companies_obj = EmployeeWorkExperience.objects.filter(employee=emp.id , employee__organization__id=organization_id, is_active=True).order_by('-id')
            if emp_companies_obj.exists():
                emp_companies_serializer = EmployeeWorkExperienceViewsetSerializers(emp_companies_obj, many=True)
                result_data['employee_companies'] = emp_companies_serializer.data
                

            emp_institutes_obj = EmployeeEducations.objects.filter(employee=emp.id , employee__organization__id=organization_id, is_active=True).order_by('-id')
            if emp_institutes_obj.exists():
                emp_institutes_serializer = EmployeeEducationsViewsetSerializers(emp_institutes_obj, many=True)
                result_data['employee_education'] = emp_institutes_serializer.data
                

            emp_skills_obj = EmployeeSkills.objects.filter(employee=emp.id, employee__organization__id=organization_id, is_active=True).order_by('skill__title')
            if emp_skills_obj.exists():
                emp_skills_serializer = EmployeeSkillsViewsetSerializers(emp_skills_obj, many=True)
                result_data['employee_skills'] = emp_skills_serializer.data
                
            emp_role_query = EmployeeRoles.objects.filter(employee_project__employee__uuid = emp_uuid, employee_project__employee__organization=organization_id, is_active=True)
            if emp_role_query.exists():
                emp_role_serializer = EmployeeRolesViewsetSerializers(emp_role_query, many=True) 
                result_data['employee_project_roles'] = emp_role_serializer.data
            

            return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': result_data, 'message': 'Success', 'system_error_message': ''})

        except Exception as e:
            return exception(e)

    def get_org_id_from_emp(self, emp_uuid):
        try:
            obj = Employees.objects.get(uuid=emp_uuid)
            if obj.organization is not None:
                return obj.organization.id

            return None
        except Exception as e:
            return None


def isEmployeeRegisteredHrmsUser(self, emp, data):
    try:
        response = {'status': 200, 'system_status': '', 'data': '', 'message': '', 'system_error_message': ''}
        # employee previous information
        first_name = emp.first_name
        last_name = emp.last_name
        official_email  = data['official_email'].lower()
        
        if HrmsUsers.objects.filter(email = official_email).exists():
            return ({'status': 400, 'message': 'Employee is already part of the hrmsuser system' })
        # if official email is updated
        if emp.official_email is not None:
            hrms_user = HrmsUsers.objects.filter(email = emp.official_email)
            if hrms_user.exists():
                hrms_user = hrms_user.first()
                hrms_user.email = official_email
                hrms_user.save()
                hrms_user_data = hrms_user
                response['message'] = 'Hrmsuser email updated successfully'
                response['data'] = hrms_user_data
                return response

        temp_password = str(uuid.uuid4())[:8]   
        user_data_array = {
            'first_name': first_name,
            'last_name': last_name,
            'email': official_email,
            'password': temp_password,
            'password2': temp_password
        }
        user_serializer = HrmsUserEmployeesRegisterationSerializers(data=user_data_array)
        if not user_serializer.is_valid():
            response['status'] = 400
            response['system_status'] = 400
            response['message'] = 'ValidationError'
            response['system_error_message'] = user_serializer.errors
            return response
        hrms_user_data = user_serializer.save()

        # send email to the employee with the temporary password

        
        

        body = 'Your temporary password is ' + temp_password + '. Your email is ' + official_email
        data = {
            'subject': 'Congratulations, You are now part of hrms user.',
            'body':  body,
            'to_email': official_email,
        }
        
        Util.send_email(data)
        response['status'] = 200
        response['data'] = hrms_user_data
        return response
    except Exception as e:
        response['system_error_message'] = str(e)
        response['status'] = 400
        return response

class EmployeeResumeView(viewsets.ModelViewSet):
 
 def create(self, request, *args, **kwrags):
    try:
        employee_id = decodeToken(request, self.request)['employee_id']
        employee = Employees.objects.get(id=employee_id, is_active=True)
        request.data['employee'] = employee_id
        emp_resume_query = EmployeeResume.objects.filter(employee=employee_id, is_active =True)
        if not emp_resume_query.exists():
            serializer = EmployeeResumeSerializer(data=request.data)
            if serializer.is_valid():
                    serializer.save()
                    return successMessageWithData('Resume data added successfully', serializer.data)
            else:
                    return serializerError(serializer.errors)
        else:
            obj=emp_resume_query.get()
            obj.is_active = False
            obj.save()
            serializer = EmployeeResumeSerializer(data=request.data)
            if serializer.is_valid():
                    serializer.save()
                    return successMessageWithData('Resume data added successfully', serializer.data)
            else:
                    return serializerError(serializer.errors)
            
    except exception as e:
        return exception(e)

 def view(self, request, *args, **kwargs):
     try:
         employee_id = decodeToken(request, self.request)['employee_id']
        # employee = Employees.objects.get(id=employee_id, is_active=True)
         print(employee_id)
         if employee_id is None:
             employee_id = request.data.get('employee_id')
         emp_data = EmployeeResume.objects.filter(employee=employee_id, is_active=True)
         if not emp_data.exists():
             return errorMessage('No resume data found for the employee')
             
        #  print("Test",emp_data.values())
        #  serializer =  EmployeeResumeSerializer(emp_data)
        #  print(serializer.data)
         return successMessageWithData('success', emp_data.values())
    #  except EmployeeResume.DoesNotExist:
    #     return errorMessage('No resume data found for the employee')
     except exception as e:
         return exception(e)
     
def custom_query(organization_id):
    # print(ep_yearly_segmentation, ep_batch,organization_id)
    with connection.cursor() as cursor:
        cursor.execute("""
WITH employee_data AS (
    SELECT 
        e.id,
        CASE e.gender
            WHEN 1 THEN 'Male'
            WHEN 2 THEN 'Female'
            ELSE 'Unknown'
        END AS gender,
        e.name AS employee_name,
        e.dob,
        e.official_email AS email,
        COALESCE(e.department_id, 0) AS department_id, -- Set department_id to 0 if NULL
        e.joining_date,
        CAST(
            CASE
                WHEN e.is_active = true AND e.leaving_date IS NULL THEN 
                    CAST(FLOOR((DATE(CURRENT_DATE) - e.joining_date) / 365) AS FLOAT) + 
                    CAST((FLOOR(MOD((DATE(CURRENT_DATE) - e.joining_date) / 30, 12)) / 100.0) AS FLOAT)
                WHEN e.is_active = true AND e.leaving_date IS NOT NULL THEN 
                    CAST(FLOOR((e.leaving_date - e.joining_date) / 365) AS FLOAT) + 
                    CAST((FLOOR(MOD((e.leaving_date - e.joining_date) / 30, 12)) / 100.0) AS FLOAT)
                WHEN e.is_active = false AND e.leaving_date IS NULL THEN 
                    CAST(FLOOR((DATE(e.updated_at) - e.joining_date) / 365) AS FLOAT) + 
                    CAST((FLOOR(MOD((DATE(e.updated_at) - e.joining_date) / 30, 12)) / 100.0) AS FLOAT)
                WHEN e.is_active = false AND e.leaving_date IS NOT NULL THEN 
                    CAST(FLOOR((e.leaving_date - e.joining_date) / 365) AS FLOAT) + 
                    CAST((FLOOR(MOD((e.leaving_date - e.joining_date) / 30, 12)) / 100.0) AS FLOAT)
                ELSE 0.0
            END AS FLOAT
        ) AS tenure,
        e.current_salary AS salary,
        stf.title AS designation,
        ept.title AS status,
        project_data.projects,
        edu.degree_title,
        CASE e.is_active
            WHEN true THEN 'Active'
            WHEN false THEN 'Inactive'
            ELSE 'Unknown'
        END AS is_active,    
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.dob)) AS age,
        e.organization_id
    FROM 
        employees_employees AS e
    LEFT JOIN (
        SELECT ARRAY_AGG(DISTINCT CONCAT(pp.id, ':', pp.name)) AS projects, eep.employee_id
        FROM employees_employeeprojects AS eep  
        JOIN projects_projects AS pp ON eep.project_id = pp.id
        WHERE eep.is_active = TRUE AND pp.is_active = TRUE
        GROUP BY eep.employee_id
    ) AS project_data ON e.id = project_data.employee_id
    LEFT JOIN organizations_staffclassification AS stf ON e.staff_classification_id = stf.id AND stf.is_active = TRUE
    LEFT JOIN employees_employeetypes AS ept ON e.employee_type_id = ept.id AND ept.is_active = TRUE
    LEFT JOIN (
        SELECT 
            ed.employee_id,
            ed.degree_title,
            ROW_NUMBER() OVER (PARTITION BY ed.employee_id ORDER BY id DESC) AS row_num
        FROM 
            institutes_employeeeducations AS ed
        WHERE ed.is_active = TRUE
    ) AS edu ON e.id = edu.employee_id AND edu.row_num = 1
    WHERE e.is_active = TRUE AND e.organization_id = %s
)
SELECT 
    COALESCE(dd.id, 0) AS department_id,
    COALESCE(dd.title, 'No Department') AS title,
    COUNT(DISTINCT ed.id) AS total_employee_count,
    ROUND(AVG(ed.age))::INT AS average_employee_age,
    ROUND(AVG(CAST(ed.tenure AS DOUBLE PRECISION))::numeric, 1) AS tenure,
    STRING_AGG(
        DISTINCT JSON_BUILD_OBJECT(
            'department', COALESCE(dd.title, 'No Department'),
            'emp_id', ed.id,
            'employee_name', ed.employee_name,
            'dob', ed.dob,
            'email', ed.email,
            'gender', ed.gender,
            'joining_date', ed.joining_date,
            'salary', ed.salary,
            'designation', ed.designation,
            'status', ed.status,
            'projects', ed.projects,
            'degree_title', ed.degree_title,
            'age', ed.age,
            'tenure', ed.tenure,
            'is_active', ed.is_active
        )::TEXT, 
        ',' 
    ) AS employees_data
FROM 
    employee_data AS ed
LEFT JOIN 
    departments_departments AS dd ON ed.department_id = dd.id
GROUP BY 
    COALESCE(dd.id, 0), COALESCE(dd.title, 'No Department')
HAVING 
    COUNT(DISTINCT ed.id) > 0;
        """, [organization_id])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Parse the employees_data field into a list of dictionaries
        for row in rows:
            row['employees_data'] = parse_employees_data(row['employees_data'])

        return rows

def parse_employees_data(employees_data):
    # Parse the employees_data string into a list of dictionaries
    return json.loads("[" + employees_data + "]")
