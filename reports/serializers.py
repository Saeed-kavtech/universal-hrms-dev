from rest_framework import serializers
from employees.models import Employees, EmployeeProjects
from employees.serializers import EmployeeProjectsViewsetSerializers
from departments.models import Departments
from projects.models import Projects
from employees.models import EmployeeRoles

class OrganogramDepartmentSerializers(serializers.ModelSerializer):
    employees = serializers.SerializerMethodField()

    class Meta:
        model = Departments
        fields = [
            'id',
            'title',
            'employees',
        ]
    
    def get_employees(self, obj):
        try:
            emp = self.context.get('employees')
            emp = emp.filter(department=obj.id)
            serializer = OrganogramEmployeesDepartmentSerializers(emp, many=True)
            return serializer.data    
        except Exception as e:
            print(str(e))
            return None


class OrganogramEmployeesDepartmentSerializers(serializers.ModelSerializer):
    projects = serializers.SerializerMethodField()    
    staff_classification_title = serializers.SerializerMethodField()
    staff_classification_level = serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = [
            'id',
            'name',
            'profile_image',
            'staff_classification',
            'staff_classification_title',
            'staff_classification_level',
            'projects',
        ]

    def get_staff_classification_level(self, obj):
        try:
            return obj.staff_classification.level
        except Exception as e:
            return None

    def get_projects(self, obj):
        try:
            query = EmployeeProjects.objects.filter(employee=obj.id, is_active=True)
            serializer = EmployeeProjectsViewsetSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            print(str(e))
            return None
    
    def get_staff_classification_title(self, obj):
        try:
            return obj.staff_classification.title
        except Exception as e:
            print(str(e))
            return None
    

# Serializers for Project based Organogram
class OrganogramProjectsSerializers(serializers.ModelSerializer):
    employee_projects = serializers.SerializerMethodField()
    class Meta:
        model = Projects
        fields = [
            'id',
            'name',
            'employee_projects',
        ]

    def get_employee_projects(self, obj):
        try:
            # emp_projects = self.context.get('emloyee_projects')
            emp_projects = EmployeeProjects.objects.filter()
            emp_projects = emp_projects.filter(project=obj.id)
            serializer = OrganogramEmployeeProjectsSerializers(emp_projects, many=True)
            return serializer.data
            
        except Exception as e:
            print(str(e))
            return None
        

class OrganogramEmployeeProjectsSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    employee_project_roles = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeProjects
        fields = [
            'id',
            'employee_name',
            'profile_image',
            'employee_project_roles',
        ]
        
    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None
        
    def get_profile_image(self, obj):
        try:
            return obj.employee.profile_image.url
        except Exception as e:
            return None
        
    def get_employee_project_roles(self, obj):
        try:
            query = EmployeeRoles.objects.filter(employee_project=obj.id, is_active=True)
            serializer = OrganogramEmployeeProjectsRolesSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            print(str(e))
            return None 
        
class OrganogramEmployeeProjectsRolesSerializers(serializers.ModelSerializer):
    role_title = serializers.SerializerMethodField()
    class Meta:
        model = EmployeeRoles
        fields = [
            'role',
            'role_title',
        ]
        
    def get_role_title(self, obj):
        try:
            return obj.role.title
        except Exception as e:
            print(str(e))
            return None 