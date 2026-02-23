from employees.models import Employees
from rest_framework.response import Response
from logs.views import UserLoginLogsViewset



def preEmployeeDataChecks(self, request, emp_uuid):
    user_id = request.user.id
    is_admin = request.user.is_admin
    is_superuser = request.user.is_superuser
    # if user is superuser
    if is_superuser==True:
        return {'status': 400, 'system_status': 400, 'data': '', 'message': 'Superuser do not have previlages ', 'system_status_message': ''}


    user_organization_obj = UserLoginLogsViewset().userOrganization(request.user)
    if user_organization_obj is None:
        return {'status':400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''}
            
    user_organization_id = user_organization_obj.id
    
    # if employee does not exists or is inactive checks
    employee_query = Employees.objects.filter(uuid=emp_uuid)
    if not employee_query.exists():
        return {'status': 400, 'system_status': 400, 'data': '', 'message': 'Employee does not exists', 'system_status_message': ''}

    if request.method != 'PATCH':
        if not employee_query.filter(is_active=True).exists():
            return {'status': 400, 'system_status': 400, 'data': '', 'message': 'Employee is not active', 'system_status_message': ''}
 
    # This will get the employee organization id
    emp = Employees.objects.get(uuid=emp_uuid)
    emp_org_id = emp.organization.id



    # if user is admin
    if is_admin == True or request.user.is_employee == True:           
        admin_organization = user_organization_id
        if admin_organization != emp_org_id:
            return {'status': 400, 'system_status': 400, 'data': '', 'message': 'Admin user does not belong to this organization', 'system_status_message': ''}
  
        return {'status': 202, 'code': 202, 'type': 'admin', 'org': user_organization_obj, 'org_id': admin_organization, 'user_id': user_id, 'emp_org_id': emp_org_id}
    
    # #TODO if user is employee
    # elif request.user.is_employee == True:
    #     return {'status': 400, 'system_status': 400, 'message': "Employee Don't have any assign roles right now", 'data': '', 'system_status_message': ''}

    #TODO if user is of some other type   
    return {'status': 400, 'system_status': 400, 'data': '', 'message': 'Not allowed right now', 'system_status_message': ''}