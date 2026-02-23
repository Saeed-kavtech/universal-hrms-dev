# from rest_framework.response import Response
# from rest_framework import status
# from employees.serializers import EmployeesLoginData
# from employees.models import Employees, SystemRoles, EmployeeProjects, EmployeeRoles

# from navigations.views import LoginUserNavigationList
# from .models import HrmsUsers
# from rest_framework.views import APIView
# from .serializers import HrmsUserLoginSerializer, HrmsUserProfileSerializer, HrmsUserChangePasswordSerializer, LoginOrganizationModuleAccessSerializer, SendPasswordResetEmailSerializer, HrmsUserPasswordResetSerializer, HrmsUserLogoutSerializer
# from .serializers import HrmsUsersSerializer
# from helpers.status_messages import *
# from helpers.image_uploads import upload_to
# from django.contrib.auth import authenticate
# from rest_framework_simplejwt.tokens import AccessToken
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.permissions import IsAuthenticated
# from employees.models import SystemRoles
# from logs.views import UserLoginLogsViewset
# from organizations.models import Organization, OrganizationModuleAccess
# from organizations.serializers import OrganizationAndLocationSerializers
# from employees.models import Employees
# from employees.serializers import EmployeesLoginData
# from .models import HrmsUsers
# from navigations.models import RolesNavigations
# from navigations.serializers import LoginRolesNavigationsViewsetSerializers
# from .serializers import HrmsUserProfileSerializer
# # Create your views here.

# def get_tokens_for_user(user, organization_id=None, role_id=None, employee_id=None):
#     try:
#         access_token_payload = {}
#         if organization_id:
#             access_token_payload['organization_id'] = organization_id
#         if role_id:
#             access_token_payload['role_id'] = role_id
#         if employee_id:
#             access_token_payload['employee_id'] = employee_id
#         # if permission_id and len(permission_id) > 0:
#         #    access_token_payload['permission_id'] = permission_id

        
#         access_token = AccessToken.for_user(user)
#         access_token['payload'] = access_token_payload
#         refresh = RefreshToken.for_user(user)
#         return {
#             'refreshToken': str(refresh),
#             'accessToken': str(access_token),
#         }
#     except Exception as e:
#         print(e)
#         return None
    

# class HrmsUserLogin(APIView):
    
    
#     # def post(self, request, format=None):
#     #     try:
#     #         serializer = HrmsUserLoginSerializer(data=request.data)
#     #         if serializer.is_valid():
#     #             email = serializer.data.get('email')
#     #             password = serializer.data.get('password')
                
#     #             user = authenticate(email=email.lower(), password=password)
#     #             loginLogArray = {'user':None, 'organization':None}

#     #             if user is not None:
#     #                 token = get_tokens_for_user(user)
#     #                 org_id = None
                    
#     #                 #TODO check if user has multi organizations then send the list of organization to select
#     #                 is_admin = user.is_admin
#     #                 is_employee = user.is_employee
#     #                 is_superuser=user.is_superuser
#     #                 is_privileged=user.is_privileged
#     #                 is_subadmin=user.is_subadmin
#     #                 employee_id = None
#     #                 organization=None
#     #                 user_serializer=None
#     #                 # if user.is_superuser:
#     #                 #     return Response({'status': 200, 'superuser': user.is_superuser, 'token': token}) 
                    
                    
                    
                    
#     #                 if is_admin or is_employee:              
#     #                     user_log = UserLoginLogsViewset().userLogin(user.id)
#     #                     if user_log['status'] != 200 and user_log['status'] != 202:
#     #                         return errorMessage(user_log['message'])
                        
                        
#     #                     organization = user_log['data']

#     #                     hrmsuser = user_log['current_hrmsuser']
#     #                     user_serializer = HrmsUserProfileSerializer(hrmsuser).data
#     #                     if user_log['status'] == 202:
#     #                         org_id = None
#     #                     else:
#     #                         org_id = organization.id
                            
#     #                         if is_employee:
#     #                             if not organization.is_active:
#     #                                 return errorMessage("This organization is currently deactivated. Please contact the administrator")

#     #                             user_data = user_log['current_employee']
#     #                             user_serializer = EmployeesLoginData(user_data).data
#     #                             employee = user_data
#     #                             employee_id = employee.id
                                
#     #                 role = SystemRoles.objects.filter(user=user.id, is_active=True)
#     #                 role_id = None
#     #                 permission_serializer=[]
#     #                 if role.exists():
#     #                     role_obj = role.first()
#     #                     role_id = role_obj.role.id
#     #                     # print(role_id)

#     #                     permission_query=RolesNavigations.objects.filter(role=role_id,role__organization=org_id,is_active=True)
#     #                     # print(permission_query.values())
#     #                     if permission_query.exists():
#     #                         permission_serializer=LoginRolesNavigationsViewsetSerializers(permission_query,many=True).data

#     #                     #     permission_id = list(permission_query.values_list('id', flat=True))
                           
                        

#     #                 token = get_tokens_for_user(user, organization_id=org_id, role_id=role_id, employee_id=employee_id)
#     #                 organization_name = None
#     #                 if org_id is not None:
#     #                     organization_name = organization.name
#     #                 org_serializer = None
#     #                 organization_logo = None
#     #                 if organization:
#     #                     if organization.id:
#     #                         organization_logo = organization.logo.url



#     #                 elif not is_admin and not is_employee:
#     #                     return errorMessage('User is not admin or employee')
                    

#     #                 modules={}

#     #                 # Fetch default modules (default=True)
#     #                 default_modules_query = OrganizationModuleAccess.objects.filter(is_default=True,organization__isnull=True, is_active=True)

#     #                 # Fetch organization-specific modules (organization=org_id and default=False)
#     #                 organization_access_module_query = OrganizationModuleAccess.objects.filter(organization=org_id, is_default=False, is_active=True)

#     #                 # Check if either query has results
#     #                 if default_modules_query.exists() or organization_access_module_query.exists():
#     #                     # Serialize both default and organization-specific modules
#     #                     default_modules = LoginOrganizationModuleAccessSerializer(default_modules_query, many=True).data
#     #                     organization_modules = LoginOrganizationModuleAccessSerializer(organization_access_module_query, many=True).data

#     #                     # Combine both serialized data
#     #                     modules = {
#     #                         "default_modules": default_modules,
#     #                         "organization_modules": organization_modules
#     #                     }

#     #                 # nav=LoginUserNavigationList(org_id,user.id,is_admin,is_subadmin,is_employee)
                    
#     #                 role_data = None
#     #                 if role.exists():
#     #                     role_obj = role.first()
#     #                     role_id = role_obj.role.id
#     #                     role_data = {
#     #                         'role_id': role_obj.role.id,
#     #                         'role_title': role_obj.role.title,
#     #                         'role_code': role_obj.role.code,
#     #                         'role_type_title': role_obj.role.role_type.title if role_obj.role.role_type else None
#     #                     }
                    


#     #                 return Response({'status': 200, 'system_status': 200, 'token': token,'is_privileged':is_privileged,'super_user':is_superuser,'admin': is_admin,'is_subadmin':is_subadmin,'is_employee': is_employee, 'user_id':user.id, 'org_id':org_id, 'organization_name':organization_name, 'organization_logo': organization_logo,'modules':modules,'permissions':permission_serializer, 'role': role_data, 'user': user_serializer, 'message':'Login Successfully', 'system_error_message': ''}) #, , })
#     #             else: 
#     #                 return errorMessage('Email or Password is not valid')
#     #         else:
#     #             return serializerError(serializer.errors)
               
#     #     except Exception as e:
#     #         return exception(e)









#     def post(self, request, format=None):
#         try:
#             serializer = HrmsUserLoginSerializer(data=request.data)
#             serializer.is_valid(raise_exception=True)

#             email = serializer.validated_data['email'].lower()
#             password = serializer.validated_data['password']

#             user = authenticate(email=email, password=password)
#             if not user:
#                 return errorMessage('Email or Password is not valid')

#             # --------------------------------------------------
#             # BASIC FLAGS
#             # --------------------------------------------------
#             is_admin = user.is_admin
#             is_employee = user.is_employee
#             is_superuser = user.is_superuser
#             is_privileged = user.is_privileged
#             is_subadmin = user.is_subadmin

#             org_id = None
#             organization = None
#             employee = None
#             employee_id = None

#             user_roles = []
#             project_roles = []
#             permission_serializer = []
#             position_data = None
#             department_data = None

#             # --------------------------------------------------
#             # ORGANIZATION + EMPLOYEE (SINGLE QUERY PATH)
#             # --------------------------------------------------
#             if is_admin or is_employee:
#                 login_log = UserLoginLogsViewset().userLogin(user.id)
#                 if login_log['status'] not in (200, 202):
#                     return errorMessage(login_log['message'])

#                 organization = login_log.get('data')
#                 org_id = organization.id if organization else None

#                 if is_employee:
#                     employee = login_log.get('current_employee')
#                     employee_id = employee.id

#                     if not organization.is_active:
#                         return errorMessage("This organization is currently deactivated.")

#                     # Position & Department (NO EXTRA QUERIES)
#                     if employee.position:
#                         position_data = {
#                             'id': employee.position.id,
#                             'title': employee.position.title,
#                             'code': employee.position.code
#                         }

#                     if employee.department:
#                         department_data = {
#                             'id': employee.department.id,
#                             'title': employee.department.title,
#                             'code': getattr(employee.department, 'code', None)
#                         }

#             # --------------------------------------------------
#             # SYSTEM ROLES (SINGLE QUERY)
#             # --------------------------------------------------
#             system_roles = SystemRoles.objects.filter(
#                 is_active=True
#             ).select_related('role', 'role__role_type')

#             if employee:
#                 system_roles = system_roles.filter(employee=employee)
#             else:
#                 system_roles = system_roles.filter(user=user)

#             role_id = None
#             for sr in system_roles:
#                 user_roles.append({
#                     'id': sr.role.id,
#                     'title': sr.role.title,
#                     'code': sr.role.code,
#                     'role_type': sr.role.role_type.title if sr.role.role_type else None,
#                     'role_type_id': sr.role.role_type.id if sr.role.role_type else None
#                 })
#                 if role_id is None:
#                     role_id = sr.role.id

#             # --------------------------------------------------
#             # PROJECT ROLES (FIXED N+1 ISSUE 🔥)
#             # --------------------------------------------------
#             if employee:
#                 employee_roles = EmployeeRoles.objects.filter(
#                     employee_project__employee=employee,
#                     is_active=True
#                 ).select_related(
#                     'role',
#                     'role__role_type',
#                     'employee_project__project'
#                 )

#                 for er in employee_roles:
#                     project_roles.append({
#                         'id': er.role.id,
#                         'title': er.role.title,
#                         'code': er.role.code,
#                         'role_type': er.role.role_type.title if er.role.role_type else None,
#                         'role_type_id': er.role.role_type.id if er.role.role_type else None,
#                         'project': {
#                             'id': er.employee_project.project.id,
#                             'name': er.employee_project.project.name,
#                             'code': er.employee_project.project.code
#                         },
#                         'start_date': er.start_date,
#                         'end_date': er.end_date
#                     })

#             # --------------------------------------------------
#             # PERMISSIONS (ONLY IF ROLE EXISTS)
#             # --------------------------------------------------
#             if role_id:
#                 permissions = RolesNavigations.objects.filter(
#                     role_id=role_id,
#                     role__organization=org_id,
#                     is_active=True
#                 )
#                 permission_serializer = LoginRolesNavigationsViewsetSerializers(
#                     permissions, many=True
#                 ).data

#             # --------------------------------------------------
#             # MODULE ACCESS (MINIMAL)
#             # --------------------------------------------------
#             modules = {}
#             default_modules = OrganizationModuleAccess.objects.filter(
#                 is_default=True,
#                 organization__isnull=True,
#                 is_active=True
#             )

#             org_modules = OrganizationModuleAccess.objects.filter(
#                 organization=org_id,
#                 is_default=False,
#                 is_active=True
#             )

#             if default_modules.exists() or org_modules.exists():
#                 modules = {
#                     'default_modules': LoginOrganizationModuleAccessSerializer(
#                         default_modules, many=True
#                     ).data,
#                     'organization_modules': LoginOrganizationModuleAccessSerializer(
#                         org_modules, many=True
#                     ).data
#                 }

#             # --------------------------------------------------
#             # TOKEN (LAST STEP)
#             # --------------------------------------------------
#             token = get_tokens_for_user(
#                 user,
#                 organization_id=org_id,
#                 role_id=role_id,
#                 employee_id=employee_id
#             )

#             organization_name = organization.name if organization else None
#             organization_logo = organization.logo.url if organization and organization.logo else None

#             user_data = (
#                 EmployeesLoginData(employee).data if employee
#                 else HrmsUserProfileSerializer(user).data
#             )

#             return Response({
#                 'status': 200,
#                 'system_status': 200,
#                 'token': token,
#                 'is_privileged': is_privileged,
#                 'super_user': is_superuser,
#                 'admin': is_admin,
#                 'is_subadmin': is_subadmin,
#                 'is_employee': is_employee,
#                 'user_id': user.id,
#                 'org_id': org_id,
#                 'organization_name': organization_name,
#                 'organization_logo': organization_logo,
#                 'modules': modules,
#                 'permissions': permission_serializer,
#                 'user': user_data,
#                 'user_roles': user_roles,
#                 'project_roles': project_roles,
#                 'position': position_data,
#                 'department': department_data,
#                 'message': 'Login Successfully',
#                 'system_error_message': ''
#             })

#         except Exception as e:
#             return exception(e)





#     # def post(self, request, format=None):
#     #     try:
#     #         serializer = HrmsUserLoginSerializer(data=request.data)
#     #         if serializer.is_valid():
#     #             email = serializer.data.get('email')
#     #             password = serializer.data.get('password')
                
#     #             user = authenticate(email=email.lower(), password=password)
#     #             loginLogArray = {'user':None, 'organization':None}
                
#     #             if user is not None:
#     #                 token = get_tokens_for_user(user)
#     #                 org_id = None
                    
#     #                 #TODO check if user has multi organizations then send the list of organization to select
#     #                 is_admin = user.is_admin
#     #                 is_employee = user.is_employee
#     #                 employee_id = None
#     #                 if user.is_superuser == True:
#     #                     return Response({'status': 200, 'superuser': user.is_superuser, 'token': token}) 
                    
#     #                 elif is_admin==True or is_employee==True:
                                      
#     #                     user_log = UserLoginLogsViewset().userLogin(user.id)
#     #                     if user_log['status']!=200 and user_log['status']!=202:
#     #                         return errorMessage(user_log['message'])
#     #                     organization = user_log['data']

#     #                     hrmsuser = HrmsUsers.objects.filter(id=user.id)
#     #                     hrmsuser = hrmsuser.get()
#     #                     user_serializer = HrmsUserProfileSerializer(hrmsuser)

#     #                     if user_log['status']==202:
#     #                         org_id = None
#     #                     else:
#     #                         org_id = organization.id
#     #                         if is_employee == True:
#     #                             if organization.is_active == False:
#     #                                 return errorMessage("This organization is currently deactivated. Please contact the administrator")

#     #                             user_data = Employees.objects.filter(hrmsuser=user.id, organization=org_id)
#     #                             if not user_data.exists():
#     #                                 return errorMessage("Employee does not exists")
#     #                             elif user_data.filter(is_active=False):
#     #                                 return errorMessage("Employee is no longer active. Please contact the administrator")
#     #                             user_serializer = EmployeesLoginData(user_data, many=True)
#     #                             employee = user_data.get()
#     #                             employee_id = employee.id
                                
#     #                 role = SystemRoles.objects.filter(employee__hrmsuser=user.id, is_active=True)
#     #                 role_id = None
#     #                 if role.exists():
#     #                     role_obj = role.first()
#     #                     role_id = role_obj.role.id
          
#     #                 token = get_tokens_for_user(user, organization_id=org_id, role_id=role_id, employee_id=employee_id)
#     #                 organization_name = None
#     #                 if org_id is not None:
#     #                     organization_name = organization.name

#     #                 org_serializer = None
#     #                 if organization:
#     #                     if organization.id:
#     #                         serializer = OrganizationAndLocationSerializers(organization)
#     #                         org_serializer = serializer.data


#     #                 return Response({'status': 200, 'system_status': 200, 'token': token, 'admin': is_admin, 'is_employee': is_employee, 'user_id':user.id, 'org_id':org_id, 'organization_name':organization_name, 'organization': org_serializer, 'user': user_serializer.data, 'message':'Login Successfully', 'system_error_message': ''})
#     #             else: 
#     #                 return errorMessage('Email or Password is not valid')
#     #         else:
#     #             return serializerError(serializer.errors)
               
#     #     except Exception as e:
#     #         return exception(e)







# class HrmsUserProfile(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         try:
#             serializer = HrmsUserProfileSerializer(request.user)
#             return success(serializer.data)
#         except Exception as e:
#             return exception(e)


# class HrmsUserChangePassword(APIView):

#     def post(self, request):
#         try:
#             serializer = HrmsUserChangePasswordSerializer(data=request.data, context={'hrms_user':request.user})
#             if serializer.is_valid():
#                 return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': '' ,'message':'Password Changed Successfully', 'system_error_message': ''})
#             else:
#                 return serializerError(serializer.errors)            
#         except Exception as e:
#             return exception(e)


# class SendPasswordResetEmail(APIView):
   
#     def post(self, request):
#         try:
#             serializer = SendPasswordResetEmailSerializer(data = request.data)
#             if serializer.is_valid():
#                 return Response({'status':200, 'system_status': status.HTTP_200_OK, 'data': '','message': 'Password Reset link send. Please check your email', 'system_error_message': ''})
#             else:
#                 return serializerError(serializer.errors)
#         except Exception as e:
#             return exception(e)

# class HrmsUserResetPassword(APIView):

#     def post(self, request, uid, token):
#         try:
#             serializer = HrmsUserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
#             if serializer.is_valid():
#                 return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'message': 'password is reset successfully', 'system_error_message': ''})
#             else:
#                 return serializerError(serializer.errors)
#         except Exception as e:
#             return exception(e)

# class HrmsUserLogout(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def post(self, request, format=None):
#         try:
#             serializer = HrmsUserLogoutSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT, 'data': serializer.data, 'message': 'Successfully Logout', 'system_error_message': ''})
#             else:
#                 return serializerError(serializer.errors)
#         except Exception as e:
#             return exception(e)


# class HrmsUserUpdate(APIView):
#     permission_classes = [IsAuthenticated]

#     def put(self, request, format=None):
#         try:  
#             pk=request.user.id
            
#             if HrmsUsers.objects.filter(id=pk).exists():
#                 obj = HrmsUsers.objects.get(id=pk)    
                
#                 serializer = HrmsUsersSerializer(obj, data = request.data, partial=True)
#                 if serializer.is_valid():
#                     serializer.save()
#                     return successfullyUpdated(serializer.data)
#                 else:
#                     return serializerError(serializer.errors)
#             else:
#                 return nonexistent(var = 'user')              
#         except Exception as e:
#             return exception(e)
    


from rest_framework.response import Response
from rest_framework import status
from employees.serializers import EmployeesLoginData
from employees.models import Employees, SystemRoles, EmployeeProjects, EmployeeRoles

from navigations.views import LoginUserNavigationList
from .models import HrmsUsers
from rest_framework.views import APIView
from .serializers import HrmsUserLoginSerializer, HrmsUserProfileSerializer, HrmsUserChangePasswordSerializer, LoginOrganizationModuleAccessSerializer, SendPasswordResetEmailSerializer, HrmsUserPasswordResetSerializer, HrmsUserLogoutSerializer
from .serializers import HrmsUsersSerializer
from helpers.status_messages import *
from helpers.image_uploads import upload_to
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from employees.models import SystemRoles
from logs.views import UserLoginLogsViewset
from organizations.models import Organization, OrganizationModuleAccess
from organizations.serializers import OrganizationAndLocationSerializers
from employees.models import Employees
from employees.serializers import EmployeesLoginData
from .models import HrmsUsers
from navigations.models import RolesNavigations
from navigations.serializers import LoginRolesNavigationsViewsetSerializers
from .serializers import HrmsUserProfileSerializer
# Create your views here.

def get_tokens_for_user(user, organization_id=None, role_id=None, employee_id=None):
    try:
        access_token_payload = {}
        if organization_id:
            access_token_payload['organization_id'] = organization_id
        if role_id:
            access_token_payload['role_id'] = role_id
        if employee_id:
            access_token_payload['employee_id'] = employee_id
        # if permission_id and len(permission_id) > 0:
        #    access_token_payload['permission_id'] = permission_id

        
        access_token = AccessToken.for_user(user)
        access_token['payload'] = access_token_payload
        refresh = RefreshToken.for_user(user)
        return {
            'refreshToken': str(refresh),
            'accessToken': str(access_token),
        }
    except Exception as e:
        print(e)
        return None
    

class HrmsUserLogin(APIView):
    
    
    # def post(self, request, format=None):
    #     try:
    #         serializer = HrmsUserLoginSerializer(data=request.data)
    #         if serializer.is_valid():
    #             email = serializer.data.get('email')
    #             password = serializer.data.get('password')
                
    #             user = authenticate(email=email.lower(), password=password)
    #             loginLogArray = {'user':None, 'organization':None}

    #             if user is not None:
    #                 token = get_tokens_for_user(user)
    #                 org_id = None
                    
    #                 #TODO check if user has multi organizations then send the list of organization to select
    #                 is_admin = user.is_admin
    #                 is_employee = user.is_employee
    #                 is_superuser=user.is_superuser
    #                 is_privileged=user.is_privileged
    #                 is_subadmin=user.is_subadmin
    #                 employee_id = None
    #                 organization=None
    #                 user_serializer=None
    #                 # if user.is_superuser:
    #                 #     return Response({'status': 200, 'superuser': user.is_superuser, 'token': token}) 
                    
                    
                    
                    
    #                 if is_admin or is_employee:              
    #                     user_log = UserLoginLogsViewset().userLogin(user.id)
    #                     if user_log['status'] != 200 and user_log['status'] != 202:
    #                         return errorMessage(user_log['message'])
                        
                        
    #                     organization = user_log['data']

    #                     hrmsuser = user_log['current_hrmsuser']
    #                     user_serializer = HrmsUserProfileSerializer(hrmsuser).data
    #                     if user_log['status'] == 202:
    #                         org_id = None
    #                     else:
    #                         org_id = organization.id
                            
    #                         if is_employee:
    #                             if not organization.is_active:
    #                                 return errorMessage("This organization is currently deactivated. Please contact the administrator")

    #                             user_data = user_log['current_employee']
    #                             user_serializer = EmployeesLoginData(user_data).data
    #                             employee = user_data
    #                             employee_id = employee.id
                                
    #                 role = SystemRoles.objects.filter(user=user.id, is_active=True)
    #                 role_id = None
    #                 permission_serializer=[]
    #                 if role.exists():
    #                     role_obj = role.first()
    #                     role_id = role_obj.role.id
    #                     # print(role_id)

    #                     permission_query=RolesNavigations.objects.filter(role=role_id,role__organization=org_id,is_active=True)
    #                     # print(permission_query.values())
    #                     if permission_query.exists():
    #                         permission_serializer=LoginRolesNavigationsViewsetSerializers(permission_query,many=True).data

    #                     #     permission_id = list(permission_query.values_list('id', flat=True))
                           
                        

    #                 token = get_tokens_for_user(user, organization_id=org_id, role_id=role_id, employee_id=employee_id)
    #                 organization_name = None
    #                 if org_id is not None:
    #                     organization_name = organization.name
    #                 org_serializer = None
    #                 organization_logo = None
    #                 if organization:
    #                     if organization.id:
    #                         organization_logo = organization.logo.url



    #                 elif not is_admin and not is_employee:
    #                     return errorMessage('User is not admin or employee')
                    

    #                 modules={}

    #                 # Fetch default modules (default=True)
    #                 default_modules_query = OrganizationModuleAccess.objects.filter(is_default=True,organization__isnull=True, is_active=True)

    #                 # Fetch organization-specific modules (organization=org_id and default=False)
    #                 organization_access_module_query = OrganizationModuleAccess.objects.filter(organization=org_id, is_default=False, is_active=True)

    #                 # Check if either query has results
    #                 if default_modules_query.exists() or organization_access_module_query.exists():
    #                     # Serialize both default and organization-specific modules
    #                     default_modules = LoginOrganizationModuleAccessSerializer(default_modules_query, many=True).data
    #                     organization_modules = LoginOrganizationModuleAccessSerializer(organization_access_module_query, many=True).data

    #                     # Combine both serialized data
    #                     modules = {
    #                         "default_modules": default_modules,
    #                         "organization_modules": organization_modules
    #                     }

    #                 # nav=LoginUserNavigationList(org_id,user.id,is_admin,is_subadmin,is_employee)
                    
    #                 role_data = None
    #                 if role.exists():
    #                     role_obj = role.first()
    #                     role_id = role_obj.role.id
    #                     role_data = {
    #                         'role_id': role_obj.role.id,
    #                         'role_title': role_obj.role.title,
    #                         'role_code': role_obj.role.code,
    #                         'role_type_title': role_obj.role.role_type.title if role_obj.role.role_type else None
    #                     }
                    


    #                 return Response({'status': 200, 'system_status': 200, 'token': token,'is_privileged':is_privileged,'super_user':is_superuser,'admin': is_admin,'is_subadmin':is_subadmin,'is_employee': is_employee, 'user_id':user.id, 'org_id':org_id, 'organization_name':organization_name, 'organization_logo': organization_logo,'modules':modules,'permissions':permission_serializer, 'role': role_data, 'user': user_serializer, 'message':'Login Successfully', 'system_error_message': ''}) #, , })
    #             else: 
    #                 return errorMessage('Email or Password is not valid')
    #         else:
    #             return serializerError(serializer.errors)
               
    #     except Exception as e:
    #         return exception(e)









    def post(self, request, format=None):
        try:
            serializer = HrmsUserLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data['email'].lower()
            password = serializer.validated_data['password']

            user = authenticate(email=email, password=password)
            if not user:
                return errorMessage('Email or Password is not valid')

            # --------------------------------------------------
            # BASIC FLAGS
            # --------------------------------------------------
            is_admin = user.is_admin
            is_employee = user.is_employee
            is_superuser = user.is_superuser
            is_privileged = user.is_privileged
            is_subadmin = user.is_subadmin

            org_id = None
            organization = None
            employee = None
            employee_id = None

            user_roles = []
            project_roles = []
            permission_serializer = []
            position_data = None
            department_data = None

            # --------------------------------------------------
            # ORGANIZATION + EMPLOYEE (SINGLE QUERY PATH)
            # --------------------------------------------------
            if is_admin or is_employee:
                login_log = UserLoginLogsViewset().userLogin(user.id)
                if login_log['status'] not in (200, 202):
                    return errorMessage(login_log['message'])

                organization = login_log.get('data')
                org_id = organization.id if organization else None

                if is_employee:
                    employee = login_log.get('current_employee')
                    employee_id = employee.id

                    if not organization.is_active:
                        return errorMessage("This organization is currently deactivated.")

                    # Position & Department (NO EXTRA QUERIES)
                    if employee.position:
                        position_data = {
                            'id': employee.position.id,
                            'title': employee.position.title,
                            'code': employee.position.code
                        }

                    if employee.department:
                        department_data = {
                            'id': employee.department.id,
                            'title': employee.department.title,
                            'code': getattr(employee.department, 'code', None)
                        }

            # --------------------------------------------------
            # SYSTEM ROLES (SINGLE QUERY)
            # --------------------------------------------------
            system_roles = SystemRoles.objects.filter(
                is_active=True
            ).select_related('role', 'role__role_type')

            if employee:
                system_roles = system_roles.filter(employee=employee)
            else:
                system_roles = system_roles.filter(user=user)

            role_id = None
            for sr in system_roles:
                user_roles.append({
                    'id': sr.role.id,
                    'title': sr.role.title,
                    'code': sr.role.code,
                    'role_type': sr.role.role_type.title if sr.role.role_type else None,
                    'role_type_id': sr.role.role_type.id if sr.role.role_type else None
                })
                if role_id is None:
                    role_id = sr.role.id

            # --------------------------------------------------
            # PROJECT ROLES (FIXED N+1 ISSUE 🔥)
            # --------------------------------------------------
            if employee:
                employee_roles = EmployeeRoles.objects.filter(
                    employee_project__employee=employee,
                    is_active=True
                ).select_related(
                    'role',
                    'role__role_type',
                    'employee_project__project'
                )

                for er in employee_roles:
                    project_roles.append({
                        'id': er.role.id,
                        'title': er.role.title,
                        'code': er.role.code,
                        'role_type': er.role.role_type.title if er.role.role_type else None,
                        'role_type_id': er.role.role_type.id if er.role.role_type else None,
                        'project': {
                            'id': er.employee_project.project.id,
                            'name': er.employee_project.project.name,
                            'code': er.employee_project.project.code
                        },
                        'start_date': er.start_date,
                        'end_date': er.end_date
                    })

            # --------------------------------------------------
            # PERMISSIONS (ONLY IF ROLE EXISTS)
            # --------------------------------------------------
            if role_id:
                permissions = RolesNavigations.objects.filter(
                    role_id=role_id,
                    role__organization=org_id,
                    is_active=True
                )
                permission_serializer = LoginRolesNavigationsViewsetSerializers(
                    permissions, many=True
                ).data

            # --------------------------------------------------
            # MODULE ACCESS (MINIMAL)
            # --------------------------------------------------
            modules = {}
            default_modules = OrganizationModuleAccess.objects.filter(
                is_default=True,
                organization__isnull=True,
                is_active=True
            )

            org_modules = OrganizationModuleAccess.objects.filter(
                organization=org_id,
                is_default=False,
                is_active=True
            )

            if default_modules.exists() or org_modules.exists():
                modules = {
                    'default_modules': LoginOrganizationModuleAccessSerializer(
                        default_modules, many=True
                    ).data,
                    'organization_modules': LoginOrganizationModuleAccessSerializer(
                        org_modules, many=True
                    ).data
                }

            # --------------------------------------------------
            # TOKEN (LAST STEP)
            # --------------------------------------------------
            token = get_tokens_for_user(
                user,
                organization_id=org_id,
                role_id=role_id,
                employee_id=employee_id
            )

            organization_name = organization.name if organization else None
            organization_logo = organization.logo.url if organization and organization.logo else None

            user_data = (
                EmployeesLoginData(employee).data if employee
                else HrmsUserProfileSerializer(user).data
            )

            return Response({
                'status': 200,
                'system_status': 200,
                'token': token,
                'is_privileged': is_privileged,
                'super_user': is_superuser,
                'admin': is_admin,
                'is_subadmin': is_subadmin,
                'is_employee': is_employee,
                'user_id': user.id,
                'org_id': org_id,
                'organization_name': organization_name,
                'organization_logo': organization_logo,
                'modules': modules,
                'permissions': permission_serializer,
                'user': user_data,
                'user_roles': user_roles,
                'project_roles': project_roles,
                'position': position_data,
                'department': department_data,
                'message': 'Login Successfully',
                'system_error_message': ''
            })

        except Exception as e:
            return exception(e)





    # def post(self, request, format=None):
    #     try:
    #         serializer = HrmsUserLoginSerializer(data=request.data)
    #         if serializer.is_valid():
    #             email = serializer.data.get('email')
    #             password = serializer.data.get('password')
                
    #             user = authenticate(email=email.lower(), password=password)
    #             loginLogArray = {'user':None, 'organization':None}
                
    #             if user is not None:
    #                 token = get_tokens_for_user(user)
    #                 org_id = None
                    
    #                 #TODO check if user has multi organizations then send the list of organization to select
    #                 is_admin = user.is_admin
    #                 is_employee = user.is_employee
    #                 employee_id = None
    #                 if user.is_superuser == True:
    #                     return Response({'status': 200, 'superuser': user.is_superuser, 'token': token}) 
                    
    #                 elif is_admin==True or is_employee==True:
                                      
    #                     user_log = UserLoginLogsViewset().userLogin(user.id)
    #                     if user_log['status']!=200 and user_log['status']!=202:
    #                         return errorMessage(user_log['message'])
    #                     organization = user_log['data']

    #                     hrmsuser = HrmsUsers.objects.filter(id=user.id)
    #                     hrmsuser = hrmsuser.get()
    #                     user_serializer = HrmsUserProfileSerializer(hrmsuser)

    #                     if user_log['status']==202:
    #                         org_id = None
    #                     else:
    #                         org_id = organization.id
    #                         if is_employee == True:
    #                             if organization.is_active == False:
    #                                 return errorMessage("This organization is currently deactivated. Please contact the administrator")

    #                             user_data = Employees.objects.filter(hrmsuser=user.id, organization=org_id)
    #                             if not user_data.exists():
    #                                 return errorMessage("Employee does not exists")
    #                             elif user_data.filter(is_active=False):
    #                                 return errorMessage("Employee is no longer active. Please contact the administrator")
    #                             user_serializer = EmployeesLoginData(user_data, many=True)
    #                             employee = user_data.get()
    #                             employee_id = employee.id
                                
    #                 role = SystemRoles.objects.filter(employee__hrmsuser=user.id, is_active=True)
    #                 role_id = None
    #                 if role.exists():
    #                     role_obj = role.first()
    #                     role_id = role_obj.role.id
          
    #                 token = get_tokens_for_user(user, organization_id=org_id, role_id=role_id, employee_id=employee_id)
    #                 organization_name = None
    #                 if org_id is not None:
    #                     organization_name = organization.name

    #                 org_serializer = None
    #                 if organization:
    #                     if organization.id:
    #                         serializer = OrganizationAndLocationSerializers(organization)
    #                         org_serializer = serializer.data


    #                 return Response({'status': 200, 'system_status': 200, 'token': token, 'admin': is_admin, 'is_employee': is_employee, 'user_id':user.id, 'org_id':org_id, 'organization_name':organization_name, 'organization': org_serializer, 'user': user_serializer.data, 'message':'Login Successfully', 'system_error_message': ''})
    #             else: 
    #                 return errorMessage('Email or Password is not valid')
    #         else:
    #             return serializerError(serializer.errors)
               
    #     except Exception as e:
    #         return exception(e)







class HrmsUserProfile(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            serializer = HrmsUserProfileSerializer(request.user)
            return success(serializer.data)
        except Exception as e:
            return exception(e)


class HrmsUserChangePassword(APIView):

    def post(self, request):
        try:
            serializer = HrmsUserChangePasswordSerializer(data=request.data, context={'hrms_user':request.user})
            if serializer.is_valid():
                return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': '' ,'message':'Password Changed Successfully', 'system_error_message': ''})
            else:
                return serializerError(serializer.errors)            
        except Exception as e:
            return exception(e)


class SendPasswordResetEmail(APIView):
   
    def post(self, request):
        try:
            serializer = SendPasswordResetEmailSerializer(data = request.data)
            if serializer.is_valid():
                return Response({'status':200, 'system_status': status.HTTP_200_OK, 'data': '','message': 'Password Reset link send. Please check your email', 'system_error_message': ''})
            else:
                return serializerError(serializer.errors)
        except Exception as e:
            return exception(e)

class HrmsUserResetPassword(APIView):

    def post(self, request, uid, token):
        try:
            serializer = HrmsUserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
            if serializer.is_valid():
                return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'message': 'password is reset successfully', 'system_error_message': ''})
            else:
                return serializerError(serializer.errors)
        except Exception as e:
            return exception(e)

class HrmsUserLogout(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        try:
            serializer = HrmsUserLogoutSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT, 'data': serializer.data, 'message': 'Successfully Logout', 'system_error_message': ''})
            else:
                return serializerError(serializer.errors)
        except Exception as e:
            return exception(e)


class HrmsUserUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        try:  
            pk=request.user.id
            
            if HrmsUsers.objects.filter(id=pk).exists():
                obj = HrmsUsers.objects.get(id=pk)    
                
                serializer = HrmsUsersSerializer(obj, data = request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return successfullyUpdated(serializer.data)
                else:
                    return serializerError(serializer.errors)
            else:
                return nonexistent(var = 'user')              
        except Exception as e:
            return exception(e)
    