from rest_framework import viewsets
from rest_framework.response import Response
from helpers.custom_permissions import IsAuthenticated, IsAdminOnly
from helpers.decode_token import decodeToken
from .models import SystemRoles, Employees
from .serializers import SystemRolesViewsetSerializers,PreDataEmployeeSerializers,PreEmployeesDataSerializers,PreHRMSDataSerializers
from helpers.status_messages import errorMessage, successMessage, exception, success, serializerError
from roles.models import Roles 
from profiles_api.models import HrmsUsers
from navigations.models import Navigations, RolesNavigations
from navigations.serializers import RolesNavigationsViewsetSerializers
import datetime
from organizations.models import Organization,SubadminOrganization
class SystemRolesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOnly]

    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            role_id = self.kwargs['role_id']
            role_query = Roles.objects.filter(id=role_id, organization=organization_id)
            if not role_query.exists():
                return errorMessage('No role exists at this id')
            elif not role_query.filter(is_active=True):
                return errorMessage('This role is currently deactivated')
            elif not role_query.filter(role_type__title__iexact='system roles'):
                return errorMessage('The role type selected is not a system role')
            
            system_roles = SystemRoles.objects.filter(role=role_id, is_active=True)
            serializer = SystemRolesViewsetSerializers(system_roles, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def create(self, request, *args, **kwargs):
        try:
            token = decodeToken(self, request)
            organization_id = token['organization_id']
            
            if 'user' not in request.data:
                return errorMessage('User id is a required field')    
            if 'role' not in request.data:
                return errorMessage('Role is a required field')

            user_id = request.data['user']
            role_id = request.data['role']
            
            checks = self.userRoleCheck(user_id, role_id, organization_id)
            # print("Test",checks)
            if checks['code'] == 400:
                return Response({'status': 400, 'message': checks['message'], 'system_error_message': checks['system_error']}) 

            print("Test1",checks)
            system_role_query = checks['data']
            request.data['assigned_by'] = request.user.id
            request.data['start_date'] = datetime.date.today()

            if system_role_query is not None:
                for system_role in system_role_query:
                    system_role.is_active=False
                    system_role.end_date=datetime.date.today()
                    system_role.save()

            serializer = SystemRolesViewsetSerializers(data=request.data)
            if serializer.is_valid():
                system_role = serializer.save()
            else:
                return serializerError(serializer.errors)
            
            if system_role_query is not None:
                for system_role in system_role_query.exclude(id=system_role.id):
                    system_role.is_active=False
                    system_role.end_date=datetime.date.today()
            
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Employee is successfully assigned this role', 'system_error_message': ''})
        except Exception as e:
            return exception(e)
        

    def predata(self, request, *args, **kwargs):
        try:
            token = decodeToken(self, request)
            organization_id = token['organization_id']
            # emp_query = Employees.objects.filter(organization=organization_id, is_active=True)
            sub_admin_query=SubadminOrganization.objects.filter(organization=organization_id,is_active=True).values_list('user_id',flat=True)
            emp_query = HrmsUsers.objects.filter(id__in=sub_admin_query,is_admin=True,is_subadmin=True,is_active=True)
            serializer = PreDataEmployeeSerializers(emp_query, many=True)

            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def delete(self, request, *args, **kwargs):
        try:
            token = decodeToken(self, request)
            organization_id = token['organization_id']
            user_id = self.kwargs['user_id']

            emp_query = HrmsUsers.objects.filter(id=user_id)
            if not emp_query.exists():
                return errorMessage('No user not exists at this id')
            if not emp_query.filter(is_active=True).exists():
                return errorMessage('User is deactivated at this id. Activate the user first')
            
            system_role_query = SystemRoles.objects.filter(user=user_id)
            if not system_role_query.exists():
                return errorMessage('No role exists against this user')
            if not system_role_query.filter(is_active=True):
                return errorMessage('This user is already deactivated')
            
            obj = system_role_query.filter(is_active=True).get()
            obj.is_active=False
            obj.end_date = datetime.date.today()
            obj.save()
            return successMessage('Employee is successfully deactivated')
        except Exception as e:
            return exception(e)

    def empRoleCheck(self, emp_id, role_id, org_id):
        try:
            response = {'code': 400, 'message': '', 'system_error': '', 'data': ''}

            emp_query = Employees.objects.filter(id=emp_id, organization=org_id)
            if not emp_query.exists():
                response['message']='Employee does not exists'
                return response
            elif not emp_query.filter(is_active=True):
                response['message']='Employee is deactivated. Activate the employee first'
                return response
            
            role_query = Roles.objects.filter(id=role_id, organization=org_id)
            if not role_query.exists():
                response['message'] = 'No role exists at this id'
                return response
            elif not role_query.filter(is_active=True).exists():
                response['message'] = 'Role is deactivate at this id. Activate the roles first'
                return response
            elif not role_query.filter(role_type__title__iexact='system roles'):
                response['message'] = 'Role type is not system roles'
                return response

            role_obj = role_query.get()
            role_type = role_obj.role_type.title
            if role_type.lower() != 'system roles':
                response['message'] = 'System role does not exists at this id'
                return response
            
            system_role_query = SystemRoles.objects.filter(employee=emp_id, employee__organization=org_id, is_active=True)
            if system_role_query.filter(role=role_id).exists():
                response['message'] = 'Employee is already assigned to this role'
                return response

            return {'code': 200, 'data': system_role_query}
        except Exception as e:
            return str(e)
        

    def userRoleCheck(self, user_id, role_id, org_id):
        try:
            response = {'code': 400, 'message': '', 'system_error': '', 'data': ''}

            emp_query = HrmsUsers.objects.filter(id=user_id,is_active=True)
            if not emp_query.exists():
                response['message']='User does not exists'
                return response
            elif not emp_query.filter(is_active=True):
                response['message']='User is deactivated. Activate the User first'
                return response
            
            role_query = Roles.objects.filter(id=role_id, organization=org_id)
            if not role_query.exists():
                response['message'] = 'No role exists at this id'
                return response
            elif not role_query.filter(is_active=True).exists():
                response['message'] = 'Role is deactivate at this id. Activate the roles first'
                return response
            elif not role_query.filter(role_type__title__iexact='system roles'):
                response['message'] = 'Role type is not system roles'
                return response

            role_obj = role_query.get()
            role_type = role_obj.role_type.title
            if role_type.lower() != 'system roles':
                response['message'] = 'System role does not exists at this id'
                return response
            
            system_role_query = SystemRoles.objects.filter(user=user_id, is_active=True)
            if system_role_query.filter(role=role_id).exists():
                response['message'] = 'Employee is already assigned to this role'
                return response

            return {'code': 200, 'data': system_role_query}
        except Exception as e:
            return str(e)
        


    # def empRoleCheck(self, emp_id, role_id, org_id):emp_id is hrms_user_id
    #     try:
    #         response = {'code': 400, 'message': '', 'system_error': '', 'data': ''}
            
    #         # emp_query = HrmsUsers.objects.filter(id=emp_id)
    #         emp_query = Organization.objects.filter(id=org_id,user__id=emp_id, is_active=True)
    #         if not emp_query.exists():
    #             # print(emp_query)
    #             suborg=SubadminOrganization.objects.filter(user__id=emp_id,organization__id=org_id,is_active=True)
    #             if not suborg.exists():
    #                 response['message'] = 'Employee does not exists in this organization'
    #                 return response

    #             # response['message'] = 'Employee does not exists in this organization'
    #             # return response
    #         elif not emp_query.filter(is_active=True):
    #             response['message'] ='Employee is deactivated. Activate the employee first'
    #             return response
            
    #         role_query = Roles.objects.filter(id=role_id, organization=org_id)
    #         if not role_query.exists():
    #             response['message'] = 'No role exists at this id'
    #             return response
    #         elif not role_query.filter(is_active=True).exists():
    #             response['message'] = 'Role is deactivate at this id. Activate the roles first'
    #             return response
    #         elif not role_query.filter(role_type__title__iexact='system roles'):
    #             response['message'] = 'Role type is not system roles'
    #             return response

    #         role_obj = role_query.get()
    #         role_type = role_obj.role_type.title
    #         if role_type.lower() != 'system roles':
    #             response['message'] = 'System role does not exists at this id'
    #             return response
            
    #         system_role_query = SystemRoles.objects.filter(user=emp_id, is_active=True)
    #         # print(emp_id)
    #         if system_role_query.filter(role=role_id).exists():
    #             response['message'] = 'Employee is already assigned to this role'
    #             return response
            
    #         return {'code': 200, 'data': system_role_query}
    #     except Exception as e:
    #         return str(e)
        
    # assign admin role
    def admin_role(self, request, *args, **kwargs):
        try:
            token = decodeToken(self, request)
            organization_id = token['organization_id']
            
            request.data['user'] = request.user.id

            if not request.user.is_admin == True:
                return errorMessage("User is not an admin user")
            
            role_query = Roles.objects.filter(is_active=True)
            is_admin_role_exists = False
            role_obj = None
            for role in role_query:
                if role.title.lower() == 'admin':
                    role_obj = role.id
                    is_admin_role_exists=True
                    break
            
            if is_admin_role_exists == False:
                return errorMessage("Admin role does not exists")
            
            nav_query = Navigations.objects.filter(organization=organization_id, is_active=True)
            role_nav_query = RolesNavigations.objects.filter(role=role_obj.id, role__organization=organization_id)

            nav_count = nav_query.count()
            role_nav_query = role_nav_query.filter(is_active=True).count()
            if nav_count == role_nav_query:
                return successMessage("This user is already assigned all the permissions")
            elif nav_count == role_nav_query.count():
                for role_nav in role_nav_query.filter(is_active=False):
                    role_nav.is_active=True
                    role_nav.save() 
                return successMessage('Successfully assigned the permissions')

            permission_data = []
            for nav in nav_query:

                if role_nav_query.filter(navigation=nav.id).exists():
                    role_nav_obj = role_nav_query.filter(navigation=nav.id).get()
                    role_nav_obj.is_active=True
                    role_nav_obj.save()
                else:
                    create_admin_nav = RolesNavigations.objects.create(
                        role = role_obj,
                        navigation = nav,
                        can_view = True,
                        can_update = True,
                        can_delete = True,
                        can_add = True, 
                        is_active=True
                    )
                    create_admin_nav.save()
                    serializer = RolesNavigationsViewsetSerializers(create_admin_nav, many=False).data
                    permission_data.append(serializer)
            
            return Response({'status': 200, 'system_status': 200, 'data': permission_data, 'message': 'Employee is successfully assigned this role', 'system_error_message': ''})
        except Exception as e:
            return exception(e)
    
