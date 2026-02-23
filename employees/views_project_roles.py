from django.shortcuts import render
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import viewsets
from .serializers import *
from .models import *
from helpers.status_messages import *
from helpers.custom_permissions import IsAuthenticated, DoesOrgExists
import datetime
from roles.serializers import PreDataRolesSerializers
from projects.serializers import PreProjectDataViewSerializers

class EmployeeProjectsRolesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    # List employee project and roles employees based 
    def list(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            emp_uuid = self.kwargs['emp_uuid']

            emp_query = Employees.objects.filter(uuid = emp_uuid, organization=user_organization.id).order_by('-id')
            if not emp_query.exists():
                return errorMessage('Employee does not exists at this id')
            elif not emp_query.filter(is_active=True):
                return errorMessage('employee is deactivated')

            emp_role_query = EmployeeRoles.objects.filter(employee_project__employee__uuid = emp_uuid, employee_project__employee__organization=user_organization.id)
            emp_role_serializer = EmployeeRolesViewsetSerializers(emp_role_query, many=True) 

            return success(emp_role_serializer.data)


        except Exception as e:
            return exception(e)
        
    # retrieve specific project based emp project id
    def retrieve(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            emp_role_id = self.kwargs['emp_role_id']
        
            emp_role_query = EmployeeRoles.objects.filter(id = emp_role_id, employee_project__employee__organization=user_organization.id)
            if not emp_role_query.exists():
                return errorMessage('No employee role exists at this id')
            if not emp_role_query.filter(is_active=True).exists():
                return errorMessage('No active employee project role exists at this id')
            
            
            emp_role_serializer = EmployeeRolesViewsetSerializers(emp_role_query, many=True)
          
            return success(emp_role_serializer.data)
        except Exception as e:
            return exception(e)
        
    def pre_data(self,emp_id,organization_id,is_active):
        try:        
            if is_active:     
                queryset = EmployeeProjects.objects.filter(employee=emp_id,employee__organization=organization_id, is_active=is_active)

            else:
                queryset = EmployeeProjects.objects.filter(employee=emp_id,employee__organization=organization_id)

            serializer = LoginEmployeeProjectsViewsetSerializers(queryset, many=True)
            serialized_data = serializer.data
            # print(serialized_data)
            return serialized_data
        except Exception as e:
            return None
        
    def project_role(self,emp_id,organization_id,project_id):
        try:        
            
            queryset = EmployeeRoles.objects.filter(employee_project__project=project_id,employee_project__employee=emp_id,employee_project__employee__organization=organization_id,is_active=True,employee_project__is_active=True,employee_project__project__is_active=True)

            serializer = PreEmployeeRolesSerializers(queryset, many=True)
            serialized_data = serializer.data
            # print(serialized_data)
            return serialized_data
        except Exception as e:
            return None

        

    # def pre_data_hr(self,organization_id):
    #     try:        
    #         queryset = EmployeeProjects.objects.filter(employee__organization=organization_id, is_active=True)
    #         serializer = LoginEmployeeProjectsViewsetSerializers(queryset, many=True)
    #         serialized_data = serializer.data
    #         # print(serialized_data)
    #         return serialized_data
    #     except Exception as e:
    #         return None

    # create project, roles and their time log
    def create(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            user_id = request.user.id
            method = request.method
            data = {'employee_project': None, 'employee_role': None}

            # checks if the required fields are entered or not
            if not 'employee' in request.data:
                return errorMessage('employee is a required field')
            if not 'project' in request.data:
                return errorMessage('Project is a required field')   
            

            # checks if emp exists at this id or not
            emp_id = request.data['employee']
            emp_query = Employees.objects.filter(id = emp_id, organization=user_organization.id)
            if not emp_query.exists():
                return errorMessage('Employee does not exists')
            if not emp_query.filter(is_active=True).exists():
                return errorMessage('Employee is deactivated')

            # checks if emp project exists at this id or not
            project_id = request.data['project']
            project_query = Projects.objects.filter(id=project_id, organization=user_organization.id)
            if not project_query.exists():
                return errorMessage("project does not exists")
            if not project_query.filter(is_active=True).exists():
                return errorMessage('projects are deactivated')

            # checks if active employee project already exists 
            is_project_exists = False
            emp_project_query = EmployeeProjects.objects.filter(employee = emp_id, project=project_id)
            if emp_project_query.filter(is_active=True).exists():
                is_project_exists=True
                emp_project = emp_project_query.first()           
                emp_project.jira_account_id = request.data.get('jira_account_id', None)
                emp_project.save()

            if is_project_exists == False:
                request.data['project_assigned_by'] = user_id
                serializer = EmployeeProjectsViewsetSerializers(data=request.data)

                if not serializer.is_valid():
                    return serializerError(serializer.errors)
                
                # The employee has been assigned to the project
                emp_project = serializer.save()

            # employee project log created
            emp_project_logs = self.employeeProjectsLogs(user_id, method, emp_project)
            # if emp_project_logs['status'] == 400:
            #     print('Logs not updated successfully')
            # else:
            #     data['employee_project']['project_logs'] = emp_project_logs['data']
            
            emp_project_id = emp_project.id
            request.data['employee_project'] = emp_project_id

            if not 'role' in request.data:
                return successMessage('The Employee is assigned to a project Successfully. However, no role is passed.')
            
            # checks if role exists at this id or not
            role_id = request.data['role']
            role_query = Roles.objects.filter(id=role_id, organization=user_organization.id)
            if not role_query.exists():
                return errorMessage('The Employee is assigned to a project Successfully. However, no role exists at this id')
            if not role_query.filter(is_active=True).exists():
                return errorMessage('The Employee is assigned to a project Successfully. However, the role is deactivated')
            if not role_query.filter(role_type__title__iexact='project roles').exists():
                return errorMessage('This role type is not a project roles. If role type is project then make sure the spelling is exactly "project roles".')

            # checks if employee is already assigned to this role or not
            emp_role_exists = EmployeeRoles.objects.filter(role=role_id, employee_project__employee= emp_project.employee.id, employee_project__project = emp_project.project.id, employee_project__employee__organization=user_organization.id)
            if emp_role_exists.filter(is_active=True).exists():
                return errorMessage('The Employee is assigned to a project Successfully. This employee is already assigned to this project role')
                

            request.data['start_date'] = datetime.date.today()
            request.data['role_assigned_by'] = user_id
            role_serializer = EmployeeRolesViewsetSerializers(data=request.data)
            if not role_serializer.is_valid():
                return errorMessage('The Employee is assigned to a project Successfully. However, something went wrong while processing assigning the role')

            emp_role = role_serializer.save()
            
            # employee role log    
            emp_role_logs = self.employeeRolesLogs(user_id, method, emp_role)
            # if emp_role_logs['status'] == 400:
            #     print('Logs not updated successfully')   
            # else:
            #     data['employee_role']['role_logs'] = emp_role_logs['data']
            
            return successfullyCreated(role_serializer.data)
        except Exception as e:
            return exception(e)
        

    def patch(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            emp_role_id = self.kwargs['emp_role_id']
            user_id = request.user.id
            method = request.method
            
            # does employee project id exists or not
            emp_project_role = EmployeeRoles.objects.filter(id=emp_role_id, employee_project__employee__organization=user_organization.id)
            if not emp_project_role.exists():
                return errorMessage("Employee Role does not exists at this id")
            if not emp_project_role.filter(is_active=True).exists():
                return errorMessage('No active project exists against this employee at this id')
            
            # first obj of the instance
            emp_project_role_obj = emp_project_role.first()
            emp_project_id = emp_project_role_obj.employee_project.id
            employee_role_id = emp_project_role_obj.role.id

            # does employee project exists or not at this id
            emp_project_query = EmployeeProjects.objects.filter(id = emp_project_id, employee__organization=user_organization.id)
            if not emp_project_query.exists():
                return errorMessage('No project exists against this employee at this id')
            if not emp_project_query.filter(is_active=True).exists():
                return errorMessage('No active project exists against this employee at this id')
            
            
            emp_project_obj = emp_project_query.first()
            # checks if active employee and project exists or not
            if not emp_project_obj.employee.is_active:
                return errorMessage('Activate the employee first')
            elif not emp_project_obj.project.is_active:
                return errorMessage('Activate the project first')

           
            serializer = UpdateEmployeeProjectsViewsetSerializers(emp_project_obj, data=request.data, partial=True)

            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            emp_project = serializer.save()
            return successMessageWithData('Success', serializer.data)
            # employee_project_id = emp_project.id


            # employee project log created
            # emp_project_logs = self.employeeProjectsLogs(user_id, method, emp_project)
            # # if emp_project_logs['status'] == 400:
            # #     print('Logs not updated successfully')
            # # else:
            # #     data['employee_project']['project_logs'] = emp_project_logs['data']
            
            
         
            # if 'role' in request.data:
            #     role_id = request.data['role']
                
            #     role_query = Roles.objects.filter(id=role_id, organization=user_organization.id)
            #     if not role_query.exists():
            #         return errorMessage('No role exists at this id')
            #     if not role_query.filter(is_active=True).exists():
            #         return errorMessage('The role is deactivated')
            #     if not role_query.filter(role_type__title__iexact='project roles').exists():
            #         return errorMessage('This role type is not a project roles. If role type is project then make sure the spelling is exactly "project roles".')
            

            #     # checks if role already exists or not, if not then it would create a new role
            #     emp_role_query = EmployeeRoles.objects.filter(employee_project=emp_project_id, role=role_id, employee_project__employee__organization=user_organization.id)
            #     if emp_role_query.filter(is_active=True).exists():
            #         return errorMessage("Active Role already exists at this id")
            #     else:
            #         emp_project_role_obj.is_active=False
            #         emp_project_role_obj.end_date = datetime.date.today()
            #         emp_project_role_obj.save()
            #         request.data['role_assigned_by'] = user_id
            #         request.data['employee_project'] = employee_project_id
            #         request.data['start_date'] = datetime.date.today()
            #         emp_role_serializer = EmployeeRolesViewsetSerializers(data=request.data)
            #         if not emp_role_serializer.is_valid():
            #             print(emp_role_serializer.errors)
            #         else:
            #             emp_role = emp_role_serializer.save()
            # else:
            #     emp_role_serializer = EmployeeRolesViewsetSerializers(emp_project_role, data=request.data, partial=True)
            #     if not emp_role_serializer.is_valid():
            #         print(emp_role_serializer.errors)
            #     else:
            #         emp_role = emp_role_serializer.save()


            # # Employee role log    
            # emp_role_logs = self.employeeRolesLogs(user_id, method, emp_role)
            # if emp_role_logs['status'] == 400:
            #     print('Logs not updated successfully')  
            # else:
            #     data['employee_role']['role_logs'] = emp_role_logs['data']

            # return successfullyUpdated(emp_role_serializer.data)
        except Exception as e:
            return exception(e)
        

    # def delete(self, request, *args, **kwargs):
    #     try:
    #         user_organization = request.data.get('organization_profile')
    #         emp_project_id = self.kwargs['emp_project_id']
    #         user_id = request.user.id
    #         method = request.method
            
    #         # does employee project exists or not at this id
    #         emp_project_query = EmployeeProjects.objects.filter(id = emp_project_id, employee__organization=user_organization.id)
    #         if not emp_project_query.exists():
    #             return errorMessage('No project exists against this employee at this id')
    #         if not emp_project_query.filter(is_active=True).exists():
    #             return errorMessage('No active project exists against this employee at this id')
        
    #         # first instance of the object
    #         emp_project_obj = emp_project_query.first()   
    #         if emp_project_obj.employee.is_active==False:
    #             return errorMessage('Employee is deactivated. Activate the employee first') 
    #         emp_project_obj.is_active=False  
    #         emp_project_obj.save()  

    #         # employee project log created
    #         emp_project_logs = self.employeeProjectsLogs(user_id, method, emp_project_obj)
    #         if emp_project_logs['status'] == 400:
    #             print('Logs not updated successfully')
            
    #         message = "Employee Project successfully deactivated "
    #         emp_role_query = EmployeeRoles.objects.filter(employee_project = emp_project_id, employee_project__employee__organization=user_organization.id)
    #         for emp_role in emp_role_query:
    #             emp_role.is_active=False
    #             emp_role.save()
    #             message+= "and all the Employee project role deactivated succussfully"

    #          # TODO create employee role log    
    #         emp_logs = self.employeeRolesLogs(user_id, method, emp_role)
    #         if emp_logs['status'] == 400:
    #             print('Logs not updated successfully')

    #         return successMessage(message)
    #     except Exception as e:
    #         return exception(e)
        
    
    def delete(self, request, *args, **kwargs):
        try:    
            user_organization = request.data.get('organization_profile')
            emp_role_id = self.kwargs['emp_role_id']
            user_id = request.user.id
            method = request.method
            
            # does employee project exists or not at this id
            emp_role_query = EmployeeRoles.objects.filter(id = emp_role_id, employee_project__employee__organization=user_organization.id)
            if not emp_role_query.exists():
                return errorMessage('No role exists against this employee at this id')
            if not emp_role_query.filter(is_active=True).exists():
                return errorMessage('Employee role is already deactivated')
            
            # first instance of the object
            emp_role_obj = emp_role_query.first()   
            if emp_role_obj.is_active == False:
                return errorMessage('Employee role is already deactivated')
            
            # print(emp_role_obj.employee_project.id)
            
            employee_project_query=EmployeeProjects.objects.filter(id = emp_role_obj.employee_project.id,employee__organization=user_organization.id)

            if employee_project_query.exists():

                if  employee_project_query.filter(is_active=True).exists():
                    obj=employee_project_query.get()
                    obj.is_active=False  
                    obj.save()  

           
            emp_role_obj.end_date= datetime.date.today()
            emp_role_obj.is_active=False  
            emp_role_obj.save()  

            # TODO create employee role log    
            emp_logs = self.employeeRolesLogs(user_id, method, emp_role_obj)
            if emp_logs['status'] == 400:
                print('Logs not updated successfully')

            return successMessage("Employee role is successfully deactivated")
        except Exception as e:
            return exception(e)
        

    def get_emp_projects(self, request, *args, **kwargs):
        try:    
            user_organization = request.data.get('organization_profile')
            project_id = self.kwargs['project_id']

            # checks if emp project exists at this id or not
            project_query = Projects.objects.filter(id=project_id, organization=user_organization.id).order_by('-id')
            if not project_query.exists():
                return errorMessage("project does not exists")
            if not project_query.filter(is_active=True).exists():
                return errorMessage('projects is deactivated')


            query = EmployeeRoles.objects.filter(employee_project__project = project_id, employee_project__project__organization=user_organization.id)
            serializer = EmployeeRolesViewsetSerializers(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)


    

    def employeeProjectsLogs(self, user_id, request_method, employee_project):
        try:    
            logs_data = {
                'employee_project': employee_project.id,
                'employee': employee_project.employee.id,
                'project': employee_project.project.id,
                'request_type': request_method,
                'action_by': user_id,
                'emp_project_is_active': employee_project.is_active,
                'is_active': True
            }
            logs_serializer = EmployeeProjectsLogsViewsetSerializers(data=logs_data)
            if not logs_serializer.is_valid():
                return {'status': 400, 'system_status': 400, 'data': '', 'message': logs_serializer.errors, 'system_status_message': ''}  
            logs_serializer.save()
            return {'status': 200, 'system_status': 200, 'data': logs_serializer.data, 'message': 'Logs created successfully', 'system_status_message': ''}
        except Exception as e:
            return {'status': 400, 'system_status': 400, 'data': '', 'message': 'Exception Error', 'system_status_message': str(e)}


    def employeeRolesLogs(self, user_id, request_method, employee_role):
        try:
            role_logs = {
                'employee_role': employee_role.id,
                'employee_project': employee_role.employee_project.id,
                'role': employee_role.role.id,
                'start_date':  employee_role.start_date,
                'end_date': employee_role.end_date,
                'action_by': user_id,
                'request_type': request_method,
                'emp_role_is_active': employee_role.is_active,
                'is_active': True
            }
            logs_serializer = EmployeeRolesLogsViewsetSerializers(data=role_logs)
            if not logs_serializer.is_valid():
                print(logs_serializer.errors)
                return {'status': 400, 'system_status': 400, 'data': '', 'message': logs_serializer.errors, 'system_status_message': ''}
            logs_serializer.save()
            print(logs_serializer.data)
            return {'status': 200, 'system_status': 200, 'data': logs_serializer.data, 'message': 'Logs created successfully', 'system_status_message': ''}
            
        except Exception as e:
            return {'status': 400, 'system_status': 400, 'data': '', 'message': 'Exception Error', 'system_status_message': str(e)}
        

# This API returns the pre data of project, role and emp
class PreEmployeesProjectRoleDataView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def get(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')

            emp_query = Employees.objects.filter(organization=user_organization.id, is_active=True)
            emp_serializer = PreEmployeesDataSerializers(emp_query, many=True)

            project_query = Projects.objects.filter(organization=user_organization.id, is_active=True)
            project_serializer = PreProjectDataViewSerializers(project_query, many=True)

            role_query = Roles.objects.filter(organization=user_organization.id, role_type__title__iexact='project roles', is_active=True)
            role_serializer = PreDataRolesSerializers(role_query, many=True)
            
            data = {'employees': emp_serializer.data, 'project': project_serializer.data, 'role': role_serializer.data}
            return success(data)
        except Exception as e:
            return exception(e)
