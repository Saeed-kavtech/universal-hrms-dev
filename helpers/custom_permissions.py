from rest_framework.permissions import BasePermission
from organizations.models import Organization
from profiles_api.models import HrmsUsers
from logs.views import UserLoginLogsViewset
from helpers.decode_token import decodeToken
# from employees.models import Employees

# If User is not assign to any organization

class TokenDataPermissions(BasePermission): 
    message = {'status':400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''}
    
    def has_permission(self, request, view):
        token = decodeToken(self, request)
        organization_id = token['organization_id']
        if organization_id is None:
            return False
        request.data['current_organization'] = organization_id
        return True



SA_SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']
class CheckUserOrganization(BasePermission):
    message = 'This user is not assigned to any Organization'

    # def has_permission(self, request, view):

    #     pk = request.user.id
    #     query = Organization.objects.get(user__id=pk)
    #     organization_count = query.count()
    #     print(organization_count)
    #     if organization_count == 0:
    #         return False
    #     return True

    def has_permission(self, request, view):
        # checks if active organization exists or not
        user_id = request.user.id
        if (request.method in SA_SAFE_METHODS and request.user.is_superuser==True):
            return True
        elif request.user.is_superuser==True:
            message = 'Super Admin has no access to perform any actions'
            return False

        organization = Organization.objects.filter(is_active=True)
        

        if request.user.is_admin == True:
            if not organization.filter(user__id=user_id).exists():
                message = 'Admin does not belong to this organization'
                return False
        
        elif request.user.is_employee == True:
            return False
            # employee = Employees.objects.filter(hrmsuser__id=user_id)
            # if employee.exists():
            #     employee = employee[0]
            #     if not organization.filter(user__id=employee.hrmsuser).exists():
            #         message = 'Employee does not belong to this organization'
            #         return False
            # else:
            #     message = 'Employee does not belong to this organization'
            #     return False

        return True
        

class IsAuthenticated(BasePermission):
    message = {'status': 400, 'system_status': 403, 'data': '', 'msg': 'Authentication credential were not provided', 'system_status_message': ''}

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)



class DoesOrgExists(BasePermission): 
    message = {'status':400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''}
    
    def has_permission(self, request, view):
        user_organization = UserLoginLogsViewset().userOrganization(request.user)
        if user_organization is None:
            return False
        request.data['organization_profile'] = user_organization
        return True



# checks if user is a superuser or not
class IsSuperUser(BasePermission):
    message = 'The User is not a superuser'

    def has_permission(self, request, view):

        pk = request.user.id
        hrmsuser = HrmsUsers.objects.get(id=pk)
        if hrmsuser.is_superuser == True:
            return True
        return False

# Admin only


class IsAdminOnly(BasePermission):
    message = 'Only admin has the previleges'

    def has_permission(self, request, view):

        pk = request.user.id
        hrmsuser = HrmsUsers.objects.get(id=pk)
        if hrmsuser.is_admin == True:
            return True
        return False

# Only Employee


class IsEmployeeOnly(BasePermission):
    message = 'Only Employee has the previleges'

    def has_permission(self, request, view):
        pk = request.user.id
        hrmsuser = HrmsUsers.objects.get(id=pk)
        if hrmsuser.is_admin == False and hrmsuser.is_employee == True:
            return True
        return False


class IsSuperUserOrAdmin(BasePermission):
    message = 'Only SuperUser or Admin has the previleges'

    def has_permission(self, request, view):
        pk = request.user.id
        hrmsuser = HrmsUsers.objects.get(id=pk)
        if hrmsuser.is_superuser == True or hrmsuser.is_admin == True:
            return True
        return False
