from rest_framework import serializers
from .models import *
import regex

class ContactRelationsViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = ContactRelations
        fields = [
            'id',
            'relation',
        ]


class EmployeesLoginData(serializers.ModelSerializer):
    class Meta:
        model = Employees
        fields = [
            'id',
            'uuid',
            'emp_code',
            'profile_image',
            'name'
        ]


class AttachmentTypesViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = AttachmentTypes
        fields = [
            'id',
            'title',
            'is_degree',
            'is_letter',
            'is_active',
        ]


class EmployeeTypesViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeeTypes
        fields = [
            'id',
            'title',
            'level'
        ]


class EmployeePassportSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    class Meta:
        model = EmployeePassports
        fields = [
            'id',
            'employee',
            'employee_name',
            'passport_no',
            # 'date_of_issue',
            'date_of_expiry',
            # 'tracking_no',
            # 'booklet_no',
            # 'country_code',
            # 'passport_type',
            # 'issuing_authority',
            # 'attachment'
        ]
    
    def get_employee_name(self, obj):
        try:
            if obj.employee is not None:
                return obj.employee.name
            return None
        except Exception as e:
            print(e)
            return None


class EmployeeCnicSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    class Meta:
        model = EmployeeCnic
        fields = [
            'id',
            'employee',
            'employee_name',
            'cnic',
            # 'date_of_issue',
            # 'front_image',
            # 'back_image'
        ]

    def get_employee_name(self, obj):
        try:
            if obj.employee is not None:
                return obj.employee.name
            return None
        except Exception as e:
            print(e)
            return None

class EmployeePreDataSerializers(serializers.ModelSerializer):
    staff_classification_title  = serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = [
            'id',
            'uuid',
            'first_name',
            'last_name',
            'name',
            'code',
            'emp_code',
            'official_email',
            'hrmsuser',
            'staff_classification',
            'staff_classification_title',
            'profile_image'
        ]
    def get_staff_classification_title(self, obj):
        try:
           if obj.staff_classification:
                return obj.staff_classification.title
           else :
               return None
        except Exception as e:
            print(str(e))
            return None



class LoginEmployeeProjectsViewsetSerializers(serializers.ModelSerializer):
    project_title = serializers.SerializerMethodField()
    class Meta:
        model = EmployeeProjects
        fields = [
            'id',
            'project',
            'project_title' 
        ]

    def get_project_title(self, obj):
        try:
            return obj.project.name
        except Exception as e:
            print(str(e))
            return None

    


class PersonalEmployeeViewsetSerializers(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False)
    class Meta:
        model = Employees
        fields = [
            'id',
            'created_by',
            'name',
            'first_name',
            'last_name',
            'code',
            'emp_code',
            'profile_image',
            'father_name',
            'personal_email',
            'dob',
            'cnic_no',
            'gender',
            'marital_status',
            'blood_group',
            'organization',
            'is_active'
        ]

    def validate(self, data):
        cnic_no = data.get('cnic_no') or None
        # validation for CNIC Number
        
        if cnic_no is not None:
            cnic_pattern = "^[0-9]{5}-[0-9]{7}-[0-9]$"
            is_cnic_format_valid = regex.match(cnic_pattern, cnic_no)
            if not is_cnic_format_valid:
                raise serializers.ValidationError("Number of characters enter must be 15 and in the following format: *****-*******-*")
        

        return data


class ImportEmployeeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Employees
        fields = [
                    'first_name', 'last_name', 'cnic_no', 'father_name', 'gender', 'dob', 'emp_code', 'official_email',
                    'personal_email', 'marital_status', 'joining_date', 'organization', 'created_by'
                ]


class OfficeEmployeeViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = Employees
        fields = [
            'id',
            'code', 
            'emp_code',
            'department', 
            'staff_classification',
            'position',
            'employee_type',
            'official_email',
            'skype',
            'joining_date',
            'leaving_date',
            'status',
            'current_salary',
            'starting_salary',
            'hiring_comment',
            'leaving_reason'
        ]


# class CnicDataRelatedList(RelatedField):
#     def get_queryset(self):
#         return EmployeeCnic.objects.filter(is_active=True)

#     def to_representation(self, instance):
#         return {'employee': instance.employee, 'cnic':instance.cnic, 'is_active': instance.is_active}

class ListEmployeeRequiredFieldsViewsetSerializers(serializers.ModelSerializer):
    gender_type = serializers.SerializerMethodField()
    staff_classification_title = serializers.SerializerMethodField()
    employee_type_title = serializers.SerializerMethodField()

    class Meta:
        model = Employees
        fields = [
            'id',
            'name',
            'staff_classification',
            'staff_classification_title',
            'employee_type',
            'employee_type_title',
            'work_mode',
            'gender',
            'gender_type',
            'joining_date',
            'is_active',       
        ]


    def get_gender_type(self, obj):
        try:
            return gender_choices[obj.gender-1][1]
        except Exception as e:
            print(e)
            return None
        
    def get_staff_classification_title(self, obj):
        try:
            if obj.staff_classification is not None:
                return obj.staff_classification.title
            return None
        except Exception as e:
            print(e)
            return None
        
    def get_employee_type_title(self, obj):
        try:
            if obj.employee_type is not None:
                return obj.employee_type.title
            return None
        except Exception as e:
            print(e)
            return None




class ListEmployeeViewsetSerializers(serializers.ModelSerializer):
    cnic_data = EmployeeCnicSerializers(many=True)
    passport_data = EmployeePassportSerializers(many=True)
    organization_name  = serializers.SerializerMethodField()
    department_title = serializers.SerializerMethodField()
    staff_classification_title = serializers.SerializerMethodField()
    staff_classification_level = serializers.SerializerMethodField()
    position_title  = serializers.SerializerMethodField()
    employee_type_title = serializers.SerializerMethodField()
    gender_type = serializers.SerializerMethodField()
    marital_status_type = serializers.SerializerMethodField()

    class Meta:
        model = Employees
        fields = [
            'id',
            'name',
            'uuid', 
            'code', 
            'emp_code',
            'hrmsuser',
            'organization',
            'organization_name',
            'department', 
            'department_title',
            'staff_classification',
            'staff_classification_title',
            'staff_classification_level',
            'position',
            'position_title',
            'first_name',
            'last_name',
            'personal_email',
            'official_email',
            'profile_image',
            'father_name',
            'dob',
            'cnic_no',
            'gender',
            'gender_type',
            'marital_status',
            'marital_status_type',
            'blood_group',
            'employee_type',
            'employee_type_title',
            'work_mode',
            'skype',
            'joining_date',
            'status',
            'is_active',
            'leaving_date',
            'current_salary',
            'starting_salary',
            'hiring_comment',
            'leaving_reason',
            'cnic_data',
            'passport_data',
                        
        ]


    def get_organization_name(self, obj):
        try:
            if obj.organization is not None:
                return obj.organization.name
            return None
        except Exception as e:
            print(e)
            return None
    
    def get_department_title(self, obj):
        try:
            if obj.department is not None:
                return obj.department.title
            return None
        except Exception as e:
            print(e)
            return None

    def get_staff_classification_title(self, obj):
        try:
            if obj.staff_classification is not None:
                return obj.staff_classification.title
            return None
        except Exception as e:
            print(e)
            return None
        
    def get_staff_classification_level(self, obj):
        try:
            if obj.staff_classification is not None:
                return obj.staff_classification.level
            return None
        except Exception as e:
            print(e)
            return None


    def get_position_title(self, obj):
        try:
            if obj.position is not None:
                return obj.position.title
            return None
        except Exception as e:
            print(e)
            return None

    def get_employee_type_title(self, obj):
        try:
            if obj.employee_type is not None:
                return obj.employee_type.title
            return None
        except Exception as e:
            print(e)
            return None

    def get_gender_type(self, obj):
        try:
            return gender_choices[obj.gender-1][1]
        except Exception as e:
            print(e)
            return None

    def get_marital_status_type(self, obj):
        try:
            return marital_choices[obj.marital_status-1][1]
        except Exception as e:
            print(e)
            return None


class EmployeeEmergencyContactsViewsetSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    relation_name = serializers.SerializerMethodField()
    class Meta:
        model = EmployeeEmergencyContacts
        fields = [
            'id',
            'employee',
            'employee_name',
            'relation',
            'relation_name',
            'name',
            'mobile_no',
            'landline',
            'address',
            'email',
            'imid',
            'is_active'
        ]

    def get_employee_name(self, obj):
        try:
            if obj.employee is not None:
                return obj.employee.name
            return None
        except Exception as e:
            print(e)
            return None

    def get_relation_name(self, obj):
        try:
            if obj.relation is not None:
                return obj.relation.relation
            return None
        except Exception as e:
            print(e)
            return None


class ListEmployeeEmergencyContactsViewsetSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = EmployeeEmergencyContacts
        fields = [
            'id',
            'employee',
            'relation',
            'name',
            'mobile_no',
            'landline',
            'address',
            'email',
            'imid',
            'is_active'
        ]

    def validate(self, data):


        return data




class DependentViewsetSerializers(serializers.ModelSerializer):

    class Meta:
        model = Dependent
        fields = [
            'id',
            'relationship',
            'is_active'
        ]

class EmployeeDependentViewsetSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    relationship_name = serializers.SerializerMethodField()
    class Meta:
        model = EmployeeDependent
        fields = [
            'id',
            'employee',
            'employee_name',
            'name',
            'relationship',
            'relationship_name',
            'date_of_birth',
            'is_active'
        ]
    
    def get_employee_name(self, obj):
        try:
            if obj.employee is not None:
                return obj.employee.name
            return None
        except Exception as e:
            print(e)
            return None

    def get_relationship_name(self, obj):
        try:
            if obj.relationship is not None:
                return obj.relationship.relationship
            return None
        except Exception as e:
            print(e)
            return None
    


class ListEmployeeCompleteDataSerializers(serializers.ModelSerializer):
    cnic_data = EmployeeCnicSerializers(many=True)
    passport_data = EmployeePassportSerializers(many=True)

    staff_classification_title = serializers.SerializerMethodField()
    position_title  = serializers.SerializerMethodField()

    class Meta:
        model = Employees
        fields = [
            'id',
            'uuid', 
            'code', 
            'emp_code',
            'dependent_data', 
            
            'staff_classification',
            'staff_classification_title',
            'position',
            'position_title',
            'name',
            'email',
            'profile_image',
            'father_name',
            'dob',

            'cnic_no',
            'gender',
            'marital_status',
            'blood_group',
            'employee_type',
            'work_mode',
            'skype',
            'joining_date',
            'status',
            
            'is_active',
            'organization',
            'leaving_date',
            'current_salary',
            'starting_salary',
            'hiring_comment',
            'leaving_reason',


            'cnic_data',

            'passport_data',

        ]
    
    def get_department_title(self, obj):
        if obj.department is not None:
            return obj.department.title
        return None


class PreDataEmployeeSerializers(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = HrmsUsers
        fields = ['id', 'full_name'] 

    def get_full_name(self, obj):
        return obj.first_name+" "+obj.last_name


#     def get_staff_classification_title(self, obj):
#         if obj.staff_classification is not None:
#             return obj.staff_classification.title
#         return None


#     def get_position_title(self, obj):
#         if obj.position is not None:
#             return obj.position.title
#         return None


class EmployeeProjectsLogsViewsetSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    project_title = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeProjectsLogs
        fields = [
            'id',
            'employee',
            'employee_project',
            'employee_name',
            'project',
            'project_title',
            'request_type',
            'action_by',
            'emp_project_is_active',
            'is_active'
        ]

    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None
        
    def get_project_title(self, obj):
        try:
            return obj.project.name
        except Exception as e:
            print(str(e))
            return None
        

class EmployeeProjectsViewsetSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    project_title = serializers.SerializerMethodField()
    project_code = serializers.SerializerMethodField()
    # project_logs = serializers.SerializerMethodField()
    class Meta:
        model = EmployeeProjects
        fields = [
            'id',
            'employee',
            'employee_name',
            'jira_account_id',
            # 'project_logs',
            'project',
            'project_code',
            'project_title',
            'project_assigned_by',
            'is_active'
        ]

    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None
        
    def get_project_title(self, obj):
        try:
            return obj.project.name
        except Exception as e:
            print(str(e))
            return None
        
    def get_project_code(self, obj):
        try:
            return obj.project.code
        except Exception as e:
            print(str(e))
            return None

    # def get_project_logs(self, obj):
    #     try:
    #         logs = obj.project_logs.filter(is_active=True).order_by('-id')
    #         serializer = EmployeeProjectsLogsViewsetSerializers(logs, many=True)
    #         return serializer.data
    #     except Exception as e:
    #         print(str(e))
    #         return None
        

class UpdateEmployeeProjectsViewsetSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    project_title = serializers.SerializerMethodField()
    # project_logs = serializers.SerializerMethodField()
    class Meta:
        model = EmployeeProjects
        fields = [
            'id',
            'employee',
            'employee_name',
            'jira_account_id',
            # 'project_logs',
            'project',
            'project_title',
            # 'project_assigned_by',
            'is_active'
        ]

        read_only_fields = [
            'employee',
            'project',
        ]

    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None
        
    def get_project_title(self, obj):
        try:
            return obj.project.name
        except Exception as e:
            print(str(e))
            return None

    # def get_project_logs(self, obj):
    #     try:
    #         logs = obj.project_logs.filter(is_active=True).order_by('-id')
    #         serializer = EmployeeProjectsLogsViewsetSerializers(logs, many=True)
    #         return serializer.data
    #     except Exception as e:
    #         print(str(e))
    #         return None
        



class EmployeeRolesLogsViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRolesLogs
        fields = [
            'id',
            'employee_role',
            'role',
            'start_date',
            'end_date',
            'action_by',
            'is_active',
            'emp_role_is_active'
        ]




class EmployeeRolesViewsetSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee  = serializers.SerializerMethodField()
    project  = serializers.SerializerMethodField()
    project_title = serializers.SerializerMethodField()
    role_title = serializers.SerializerMethodField()
    employee_uuid = serializers.SerializerMethodField()
    jira_account_id = serializers.SerializerMethodField()
    project_code = serializers.SerializerMethodField()

    # role_logs = serializers.SerializerMethodField()
    class Meta:
        model = EmployeeRoles
        fields = [
            'id',
            'employee_project',
            'employee',
            'employee_uuid',
            'employee_name',
            'project',
            'jira_account_id',
            'project_title',
            'project_code',
            'role',
            'role_title',
            'start_date',
            'end_date',
            'role_assigned_by',
            'is_active'
        ]

    # def get_role_logs(self, obj):
    #     try:
    #         logs = obj.role_logs.filter(is_active=True).order_by('-id')
    #         serializer = EmployeeRolesLogsViewsetSerializers(logs, many=True)
    #         return serializer.data 
    #     except Exception as e:
    #         print(str(e))
    #         return None

    def get_jira_account_id(self, obj):
        try:
            return obj.employee_project.jira_account_id
        except Exception as e:
            print(str(e))
            return None

    def get_employee(self, obj):
        try:
            return obj.employee_project.employee.id
        except Exception as e:
            print(str(e))
            return None
    
    def get_project_code(self, obj):
        try:
            return obj.employee_project.project.code
        except Exception as e:
            print(str(e))
            return None
    
    
    def get_employee_uuid(self, obj):
        try:
            return obj.employee_project.employee.uuid
        except Exception as e:
            print(str(e))
            return None    
    

    def get_employee_name(self, obj):
        try:
            return obj.employee_project.employee.name
        except Exception as e:
            print(str(e))
            return None


    def get_project(self, obj):
        try:
            return obj.employee_project.project.id
        except Exception as e:
            print(str(e))
            return None
        
    def get_project_title(self, obj):
        try:
            return obj.employee_project.project.name
        except Exception as e:
            print(str(e))
            return None
    
    def get_role_title(self, obj):
        try:
            return obj.role.title
        except Exception as e:
            print(str(e))
            return None



class UpdateEmployeeRolesViewsetSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    role_title = serializers.SerializerMethodField()
    jira_account_id = serializers.SerializerMethodField()
    # role_logs = serializers.SerializerMethodField()
    class Meta:
        model = EmployeeRoles
        fields = [
            'employee',
            'employee_name',
            'role',
            'role_title',
            'jira_account_id',
            # 'role_logs',
            'start_date',
            'end_date',
            'assigned_by',
            'is_active'
        ]

        read_only_fields = [
            'employee',
            'role',
            'assigned_by',
        ]


    # def get_role_logs(self, obj):
    #     try:
    #         logs = obj.role_logs.filter(is_active=True).order_by('-id')
    #         serializer = EmployeeRolesLogsViewsetSerializers(logs, many=True)
    #         return serializer.data 
    #     except Exception as e:
    #         return str(e)

    def get_jira_account_id(self, obj):
        try:
            return obj.employee_project.jira_account_id
        except Exception as e:
            print(str(e))
            return None

    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None

    
    def get_role_title(self, obj):
        try:
            return obj.role.title
        except Exception as e:
            print(str(e))
            return None


class PreEmployeeRolesSerializers(serializers.ModelSerializer):
    role_title = serializers.SerializerMethodField()
    role_level = serializers.SerializerMethodField()
    class Meta:
        model = EmployeeRoles
        fields = [
            'id',
            'role',
            'role_title',
            'role_level'
        ]


    def get_role_title(self, obj):
        try:
            return obj.role.title
        except Exception as e:
            print(str(e))
            return None

    def get_role_level(self, obj):
        try:
            return obj.role.level
        except Exception as e:
            print(str(e))
            return None



class PreEmployeesDataSerializers(serializers.ModelSerializer):
    profile_image=serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = [
            'id',
            'name',
            'profile_image',
        ]    

    def get_profile_image(self, obj):
        try:
            
            query=Employees.objects.filter(id=obj.id,is_active=True)
            if not query.exists():
                return None
            obj=query.get()
            return obj.profile_image.url
        except Exception as e:
            print(str(e))
            return None 

class PreHRMSDataSerializers(serializers.ModelSerializer):
    name=serializers.SerializerMethodField()
    class Meta:
        model = HrmsUsers
        fields = [
            'id',
            'name',
        ]

    def get_name(self,obj):
        try:
            return obj.first_name+' '+obj.last_name
        except Exception as e:
            return None    
class SystemRolesViewsetSerializers(serializers.ModelSerializer):
    role_title = serializers.SerializerMethodField()
    # employee_uuid = serializers.SerializerMethodField()
    # employee_name = serializers.SerializerMethodField()
    user_name=serializers.SerializerMethodField()
    class Meta:
        model = SystemRoles
        fields = [
			'id', 
            # 'employee',

            'user',
            'user_name',
            # 'employee_uuid',
            # 'employee_name',
			'role',
            'role_title',
            'description',
            'assigned_by',
            'start_date',
            'end_date',
            'is_active',
        ]

    def get_role_title(self, obj):
        try:
            return obj.role.title
        except Exception as e:
            print(str(e))
            return None
        

    def get_employee_uuid(self, obj):
        try:
            return obj.employee.uuid
        except:
            return None
        

    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except:
            return None
        
    def get_user_name(self, obj):
        try:
            return obj.user.first_name+' '+obj.user.last_name
        except:
            return None
		
class EmployeeResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeResume
        fields = '__all__'


class EmployeeJDCMSerializer(serializers.ModelSerializer):
    # gender_type = serializers.SerializerMethodField()
    staff_classification_title = serializers.SerializerMethodField()
    # employee_type_title = serializers.SerializerMethodField()

    class Meta:
        model = Employees
        fields = [
            'id',
            'uuid',
            'name',
            'staff_classification',
            'staff_classification_title',
            'profile_image',
            # 'employee_type',
            # 'employee_type_title',
            # 'gender',
            # 'gender_type',
            'is_active',       
        ]


    def get_gender_type(self, obj):
        try:
            return gender_choices[obj.gender-1][1]
        except Exception as e:
            print(e)
            return None
        
    def get_staff_classification_title(self, obj):
        try:
            if obj.staff_classification is not None:
                return obj.staff_classification.title
            return None
        except Exception as e:
            print(e)
            return None
        
    def get_employee_type_title(self, obj):
        try:
            if obj.employee_type is not None:
                return obj.employee_type.title
            return None
        except Exception as e:
            print(e)
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
        
    def __init__(self, *args, **kwargs):
        super(EmployeeJDCMSerializer, self).__init__(*args, **kwargs)
        
        # Dynamically add fields based on the context
        if self.context.get('include_joining_date', False):
            self.fields['joining_date'] = serializers.DateField()
        if self.context.get('include_dob', False):
            self.fields['dob'] = serializers.DateField()

