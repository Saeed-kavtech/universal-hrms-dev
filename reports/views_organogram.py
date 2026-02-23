from rest_framework import viewsets
from departments.views import DepartmentsViewset
from helpers.custom_permissions import IsAuthenticated
from helpers.status_messages import exception, errorMessage, success
from helpers.decode_token import decodeToken
from employees.models import Employees, EmployeeProjects
from departments.models import Departments
from projects.models import Projects
from .serializers import OrganogramDepartmentSerializers, OrganogramProjectsSerializers
from organizations.models import StaffClassification

class OrganogramViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def post_department_based_organogram(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            department_id = request.data.get('department_id', None)
            
            departments = Departments.objects.filter(grouphead__organization=organization_id, is_active=True)
            employees = Employees.objects.filter(organization = organization_id, is_active=True)

            if department_id:
                departments = departments.filter(id = department_id)
                if not departments.exists():
                    return errorMessage('Projects does not exists at this id')
                
            serializer = OrganogramDepartmentSerializers(
                            departments, 
                            context = {'employees': employees},
                            many=True
                         )
            

            return success(serializer.data)
        except Exception as e:
            return exception(e)
    
    def new_post_department_based_organogram(self, request, *args, **kwargs):
     try:
        organization_id = decodeToken(self, self.request)['organization_id']
        department_id = request.data.get('department_id', None)
       
        departments = Departments.objects.filter(grouphead__organization=organization_id, is_active=True)
        employees = Employees.objects.filter(organization=organization_id, is_active=True)
        staffclassification = StaffClassification.objects.filter(organization = organization_id, is_active=True)
        if department_id:
            departments = departments.filter(id=department_id, is_active=True)
            if not departments.exists():
                return errorMessage('Projects do not exist at this id')
        # print(staffclassification.values())  
        organized_data = {}
        for department in departments:

            department_name = department.title
            organized_data[department_name] = {}
            processed_levels = set()
            for staff in staffclassification:
            #  print(staff.level)
             levels=staff.level
             if levels in processed_levels:  # Skip if level already processed
                    continue
            #  print(levels)
             staff_title =  staff.title
             processed_levels.add(levels)
             if levels is not None:
                emp = employees.filter(staff_classification__level=levels, department=department, is_active=True)
                # if department_name == 'Software Development':
                #    print(levels)
                #    print(emp.values())
                # print(emp.values())
                emp_with_title = list(emp.values())  # Copy all previous fields
                for employee_data in emp_with_title:
                 employee_data['staff_classification_title'] = staff_title
                #  organized_data[department_name][levels] = employee_data
                 organized_data[department_name].setdefault(levels, []).append(employee_data)
                 


        return success(organized_data)
     except Exception as e:
        return exception(e)

   
    def post_project_based_organogram(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            project_id = request.data.get('project_id', None)
            projects = Projects.objects.filter(organization=organization_id, is_active=True)
            emp_projects = EmployeeProjects.objects.filter(employee__organization=organization_id, is_active=True)
            
            if project_id:
                projects = projects.filter(id=project_id)
                if not projects.exists():
                    return errorMessage('Projects does not exists at this id')

            if emp_projects.exists():
                serializer = OrganogramProjectsSerializers(
                    projects, 
                    context = {'emp_projects': emp_projects},
                    many=True
                )

            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def predata(self,request,*args, **kwargs):
       try:
          organization_id = decodeToken(self, self.request)['organization_id']
          departments=DepartmentsViewset().pre_data(organization_id)
          return success(departments)
          
       except Exception as e:
          return exception(e)
        
