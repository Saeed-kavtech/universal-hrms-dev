import time
from rest_framework import serializers
from .models import (
    EPTypes, EPComplexity, EPScaling, EPYearlySegmentation, EPBatch, EmployeesKpis,
    KpisComments, KpisLogs, KpisStatus,ScaleComplexity,
)

from departments.models import Departments 
from employees.models import Employees
from performance_evaluation.models import *
class EPTypesSerializers(serializers.ModelSerializer):
    class Meta:
        model = EPTypes
        fields = [
            'id',
            'title',
            'key',
            'organization',
            'created_by',
            'is_active',
        ]

    def get_ep_type_title(self, obj):
        try:
            return obj.ep_type.title
        except Exception as e:
            print(str(e))
            return None


class EPComplexitySerializers(serializers.ModelSerializer):
    # ep_type_title = serializers.SerializerMethodField()
    class Meta:
        model = EPComplexity
        fields = [
            'id',
            # 'ep_type_title',
            # 'ep_type',
            'organization',
            'created_by',
            'title',
            'level',
            'score',
            'is_active',
        ]
class KpisObjectivesSerializers(serializers.ModelSerializer):
    class Meta:
        model = KpisObjectives
        fields = [
            'id',
            'title',
            'organization',
            'created_by',
            'is_active',
            'created_at',
            'updated_at',
        ]
class ScaleComplexitySerializers(serializers.ModelSerializer):
   
    class Meta:
        model = ScaleComplexity
        fields = [
            'id',
            'title',
            'level',
            'score',
            'organization',
            'created_by',
            'created_at',
            'updated_at',
            'is_active',
        ]

   
        
class EPScalingSerializers(serializers.ModelSerializer):
    # ep_type_title = serializers.SerializerMethodField()
    class Meta:
        model = EPScaling
        fields = [
            'id',
            'organization',
            # 'ep_type_title',
            # 'ep_type',
            'created_by',
            'title',
            'level',
            'is_active',
        ]

    # def get_ep_type_title(self, obj):
    #     try:
    #         return obj.ep_type.title
    #     except Exception as e:
    #         print(str(e))
    #         return None
        

class EPBatchSerializers(serializers.ModelSerializer):
    class Meta:
        model = EPBatch
        fields = [
            'id',
            'title',
            'ep_yearly_segmentation',
            'batch_no',
            'batch_status',
            'start_date',
            'end_date',
            'created_by',
            'is_active',
        ]



class EPYearlySegmentationSerializers(serializers.ModelSerializer):
    ep_batches = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    class Meta:
        model = EPYearlySegmentation
        fields = [
            'id',
            'date',
            'year',
            'duration',
            'brainstorming_period',
            'brainstorming_period_for_evaluator',
            'evaluation_period',
            'organization',
            'approved_by',
            'status',
            'is_lock',
            'locked_date',
            'lock_by',
            'unlocked_date',
            'unlock_by',
            'is_active',
            'ep_batches',
            'created_by',
        ]

    def get_ep_batches(self, obj):
        try:
            query = EPBatch.objects.filter(ep_yearly_segmentation = obj.id, is_active=True).order_by('id')
            serializer = EPBatchSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            return None
        
    def get_year(self, obj):
        try:
            return obj.date.year
        except Exception as e:
            return None



class EPYearlySegmentationUpdateSerializers(serializers.ModelSerializer):
    ep_batches = serializers.SerializerMethodField()
    class Meta:
        model = EPYearlySegmentation
        fields = [
            'id',
            'duration',
            'brainstorming_period',
            'brainstorming_period_for_evaluator',
            'evaluation_period',
            'approved_by',
            'is_active',
            'ep_batches',
        ]

    def get_ep_batches(self, obj):
        try:
            query = EPBatch.objects.filter(id = obj.id, is_active=True).order_by('id')
            serializer = EPBatchSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            return None


class KpisStatusSerializers(serializers.ModelSerializer):
    status_group_title=serializers.SerializerMethodField()
    class Meta:
        model = KpisStatus
        fields = [
            'id',
            'status_key',
            'status_title',
            'status_group',
            'status_group_title',
            'level',
            'organization',
            'created_by',
            'is_active',
        ]

    def get_status_group_title(self,obj):
        try:
            return obj.status_group.title

        except Exception as e:
            return None


class StatusGroupSerializers(serializers.ModelSerializer):
    class Meta:
        model = StatusGroup
        fields = [
            'id',
            'title',
            'level',
            'organization',
            'created_by',
            'is_active',
        ]

class ListStatusGroupSerializers(serializers.ModelSerializer):
    status_data=serializers.SerializerMethodField()

    class Meta:
        model = StatusGroup
        fields = [
            'id',
            'title',
            'level',
            'status_data',
            'organization',
            'created_by',
            'is_active',
        ]

    def get_status_data(self,obj):
        try:
            query=KpisStatus.objects.filter(status_group=obj.id,is_active=True)

            if not query.exists():
                return None
            
            serializers = KpisStatusSerializers(query, many=True)
            return serializers.data

        except Exception as e:
            return None


class EmployeesKpisSerializers(serializers.ModelSerializer):
    ep_type_title = serializers.SerializerMethodField()
    ep_complexity_title = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    kpis_status_title = serializers.SerializerMethodField()
    evaluator_name = serializers.SerializerMethodField()
    ep_batch_title = serializers.SerializerMethodField()
    project_title=serializers.SerializerMethodField()
    scale_group_title=serializers.SerializerMethodField()
    is_default_group=serializers.SerializerMethodField()
    evaluation_status_title=serializers.SerializerMethodField()
    mode_of_kpis_title=serializers.SerializerMethodField()
    kpis_status_level=serializers.SerializerMethodField()
    kpis_objective_title=serializers.SerializerMethodField()
    class Meta:
        model = EmployeesKpis
        fields = [
            'id',
            'employee',
            'employee_name',
            'title',
            'description',
            'objectives',
            'kpis_objective',
            'kpis_objective_title',
            'ep_type',
            'ep_type_title',
            'ep_batch',
            'ep_batch_title',
            'ep_complexity',
            'ep_complexity_title',
            'mode_of_kpis',
            'mode_of_kpis_title',
            'employee_project',
            'project_title',
            'scale_group',
            'scale_group_title',
            'is_default_group',
            'mmtr',
            'target_dates',
            'evaluator',
            'evaluator_name',
            'kpis_status',
            'kpis_status_title',
            'kpis_status_level',
            'evaluation_status',
            'evaluation_status_title',
            'created_by',
            'is_active',
        ]

    def get_evaluator_name(self, obj):
        try:
            return obj.evaluator.name
        except Exception as e:
            return None
        
    def get_project_title(self, obj):
        try:
            return obj.employee_project.project.name
        except Exception as e:
            return None
        
    def get_scale_group_title(self, obj):
        try:
            return obj.scale_group.title
        except Exception as e:
            return None
        
    def get_is_default_group(self, obj):
        try:
            return obj.scale_group.is_default_group
        except Exception as e:
            return None
        
  
    def get_kpis_objective_title(self,obj):
        try:
            return obj.kpis_objective.title
        except Exception as e:
            return None

        
    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            return None

    def get_ep_type_title(self, obj):
        try:
            return obj.ep_type.title
        except Exception as e:
            return None
        

        

    def get_ep_batch_title(self, obj):
        try:
            return obj.ep_batch.title
        except Exception as e:
            return None
        
    def get_ep_complexity_title(self, obj):
        try:
            return obj.ep_complexity.title
        except Exception as e:
            return None

    def get_kpis_status_title(self, obj):
        try:
            return obj.kpis_status.status_title
        except Exception as e:
            return None
        
    def get_kpis_status_level(self, obj):
        try:
            return obj.kpis_status.level
        except Exception as e:
            return None

        
    def get_evaluation_status_title(self,obj):
        try:
            if obj.evaluation_status in [1,2,3]:
                return Evaluation_Status[obj.evaluation_status-1][1]
            
            return None
           
        except Exception as e:
            return None
        
    def get_mode_of_kpis_title(self,obj):
        try:
            if obj.mode_of_kpis in [1,2,3,4]:
                return Kip_Mode_CHOICES[obj.mode_of_kpis-1][1]
            
            return None
           
        except Exception as e:
            return None
        
    # def get_comments(self, obj):
    #     try:
    #         query = KpisComments.objects.filter(employee_kpi=obj.id)
    #         serializer = KpisCommentsSerializers(query, many=True)
    #         return serializer.data
    #     except Exception as e:
    #         return None
         
class KipsFileUploadSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeesKpis
        fields = [
            'employee',
            'title',
            'ep_type',
            'ep_batch',
            'ep_complexity',
            'mmtr',
            'target_dates',
            'evaluator',
            'kpis_status',
            'created_by',
        ]

class  UpdateEmployeesKpisSerializers(serializers.ModelSerializer):
    ep_type_title = serializers.SerializerMethodField()
    ep_complexity_title = serializers.SerializerMethodField()
    ep_batch_title = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    kpis_status_title = serializers.SerializerMethodField()
    evaluator_name = serializers.SerializerMethodField()
    project_title=serializers.SerializerMethodField()
    scale_group_title=serializers.SerializerMethodField()
    kpis_objective_title=serializers.SerializerMethodField()


    class Meta:
        model = EmployeesKpis
        fields = [
            'id',
            'employee_name',
            'title',
            'description',
            'objectives',
            'kpis_objective',
            'kpis_objective_title',
            'ep_batch_title',
            'ep_type',
            'ep_type_title',
            'ep_complexity',
            'ep_complexity_title',
            'employee_project',
            'project_title',
            'scale_group',
            'scale_group_title',
            'mmtr',
            'target_dates',
            'kpis_status_title',
            'evaluator',
            'evaluator_name',
            'is_active',
        ]

    def get_kpis_objective_title(self,obj):
        try:
            return obj.kpis_objective.title
        except Exception as e:
            return None

    def get_project_title(self, obj):
        try:
            return obj.employee_project.project.name
        except Exception as e:
            return None
        
    def get_scale_group_title(self, obj):
        try:
            return obj.scale_group.title
        except Exception as e:
            return None
        

    def get_evaluator_name(self, obj):
        try:
            return obj.evaluator.name
        except Exception as e:
            return None

    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            return None

    def get_ep_type_title(self, obj):
        try:
            return obj.ep_type.title
        except Exception as e:
            return None

        
    def get_ep_batch_title(self, obj):
        try:
            return obj.ep_batch.title
        except Exception as e:
            return None
        
    def get_ep_complexity_title(self, obj):
        try:
            return obj.ep_complexity.title
        except Exception as e:
            return None

    def get_kpis_status_title(self, obj):
        try:
            return obj.kpis_status.status_title
        except Exception as e:
            return None
        
    # def get_comments(self, obj):
    #     try:
    #         query = KpisComments.objects.filter(employee_kpi=obj.id)
    #         serializer = KpisCommentsSerializers(query, many=True)
    #         return serializer.data
    #     except Exception as e:
    #         return None
    


class EmployeesPersonalGoalsKpisSerializers(serializers.ModelSerializer):
    ep_type_title = serializers.SerializerMethodField()
    ep_complexity_title = serializers.SerializerMethodField()
    ep_batch_no = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    kpis_status_title = serializers.SerializerMethodField()
    evaluator_name = serializers.SerializerMethodField()
    # comments = serializers.SerializerMethodField()
    class Meta:
        model = EmployeesKpis
        fields = [
            'id',
            'employee',
            'employee_name',
            'title',
            'description',
            'objectives',
            'ep_type',
            'ep_type_title',
            'ep_batch',
            'ep_batch_no',
            'ep_complexity',
            'ep_complexity_title',
            'evaluator',
            'evaluator_name',
            'kpis_status',
            'kpis_status_title',
            # 'comments',
            'created_by',
            'is_active',
        ]
    
    def get_evaluator_name(self, obj):
        try:
            return obj.evaluator.name
        except Exception as e:
            return None

    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            return None

    def get_ep_type_title(self, obj):
        try:
            return obj.ep_type.title
        except Exception as e:
            return None
        
    def get_ep_batch_no(self, obj):
        try:
            return obj.ep_batch.batch_no
        except Exception as e:
            return None
        
    def get_ep_complexity_title(self, obj):
        try:
            return obj.ep_complexity.title
        except Exception as e:
            return None

    def get_kpis_status_title(self, obj):
        try:
            return obj.kpis_status.status_title
        except Exception as e:
            return None
        
    # def get_comments(self, obj):
    #     try:
    #         query = KpisComments.objects.filter(employee_kpi=obj.id)
    #         serializer = KpisCommentsSerializers(query, many=True)
    #         return serializer.data
    #     except Exception as e:
    #         return None
        


class EmployeesOrganizationalGoalsKpisSerializers(serializers.ModelSerializer):
    ep_type_title = serializers.SerializerMethodField()
    ep_complexity_title = serializers.SerializerMethodField()
    ep_batch_no = serializers.SerializerMethodField()
    ep_batch_title = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    kpis_status_title = serializers.SerializerMethodField()
    evaluator_name = serializers.SerializerMethodField()
    # comments = serializers.SerializerMethodField()
    class Meta:
        model = EmployeesKpis
        fields = [
            'id',
            'employee',
            'employee_name',
            'title',
            'objectives',
            'ep_type',
            'ep_type_title',
            'ep_batch',
            'ep_batch_no',
            'ep_batch_title',
            'ep_complexity',
            'ep_complexity_title',
            'evaluator',
            'evaluator_name',
            'kpis_status',
            'kpis_status_title',
            # 'comments',
            'created_by',
            'is_active',
        ]
    
    def get_evaluator_name(self, obj):
        try:
            return obj.evaluator.name
        except Exception as e:
            return None

    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            return None

    def get_ep_type_title(self, obj):
        try:
            return obj.ep_type.title
        except Exception as e:
            return None
        
    def get_ep_batch_no(self, obj):
        try:
            return obj.ep_batch.batch_no
        except Exception as e:
            return None
        
    def get_ep_batch_title(self, obj):
        try:
            return obj.ep_batch.title
        except Exception as e:
            return None
        
    def get_ep_complexity_title(self, obj):
        try:
            return obj.ep_complexity.title
        except Exception as e:
            return None

    def get_kpis_status_title(self, obj):
        try:
            return obj.kpis_status.status_title
        except Exception as e:
            return None
        
    # def get_comments(self, obj):
    #     try:
    #         query = KpisComments.objects.filter(employee_kpi=obj.id)
    #         serializer = KpisCommentsSerializers(query, many=True)
    #         return serializer.data
    #     except Exception as e:
    #         return None
        



class EmployeesEvaluationKpisSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    ep_complexity_title = serializers.SerializerMethodField()
    kpis_status_title = serializers.SerializerMethodField()
    ep_type_title = serializers.SerializerMethodField()
    ep_batch_no = serializers.SerializerMethodField()
    ep_batch_title = serializers.SerializerMethodField()
    project_title=serializers.SerializerMethodField()
    scale_group_title=serializers.SerializerMethodField()
    scale_complexity_title=serializers.SerializerMethodField()
    kpis_objective_title=serializers.SerializerMethodField()
    class Meta:
        model = EmployeesKpis
        fields = [
            'id',
            'employee_name',
            'title',
            'objectives',
            'description',
            'kpis_objective',
            'kpis_objective_title',
            'ep_scaling',
            'ep_complexity',
            'ep_complexity_title',
            'ep_type',
            'ep_type_title',
            'ep_batch_no',
            'ep_batch_title',
            'kpis_status',
            'kpis_status_title',
            'mmtr',
            'target_dates',
            'employee_project',
            'project_title',
            'scale_group',
            'scale_group_title',
            'scale_complexity',
            'scale_complexity_title',
            # 'comments',
            'created_by',
            'is_active',
        ]

    def get_kpis_objective_title(self,obj):
        try:
            return obj.kpis_objective.title
        except Exception as e:
            return None

    def get_project_title(self, obj):
        try:
            return obj.employee_project.name
        except Exception as e:
            return None
        
    def get_scale_group_title(self, obj):
        try:
            return obj.scale_group.title
        except Exception as e:
            return None
        
    def get_scale_complexity_title(self, obj):
        try:
            return obj.scale_complexity.title
        except Exception as e:
            return None
        
    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            return None

    def get_ep_type_title(self, obj):
        try:
            return obj.ep_type.title
        except Exception as e:
            return None

    def get_ep_batch_no(self, obj):
        try:
            return obj.ep_batch.batch_no
        except Exception as e:
            return None
        
    def get_ep_batch_title(self, obj):
        try:
            return obj.ep_batch.title
        except Exception as e:
            return None
        
    def get_ep_complexity_title(self, obj):
        try:
            return obj.ep_complexity.title
        except Exception as e:
            return None

    def get_kpis_status_title(self, obj):
        try:
            return obj.kpis_status.status_title
        except Exception as e:
            return None
        
    # def get_comments(self, obj):
    #     try:
    #         query = KpisComments.objects.filter(employee_kpi=obj.id)
    #         serializer = KpisCommentsSerializers(query, many=True)
    #         return serializer.data
    #     except Exception as e:
    #         return None
        

class KpisCommentsSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_email = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    class Meta:
        model = KpisComments
        fields = [
            'id',
            'employee_name',
            'employee_email',
            'profile_image',
            'employee_kpi',
            'comments',
            'created_by',
            'created_at',
            'is_active',
        ]

        
    def get_employee_name(self, obj):
        try:
            # organization_id = self.context.get('organization_id')
            # print( organization_id)
            if obj.created_by.is_admin:
                return obj.created_by.first_name+' '+obj.created_by.last_name
            
            query=Employees.objects.filter(hrmsuser=obj.created_by.id,is_active=True)
            if not query.exists():
                return None
            obj=query.get()
            return obj.name
        except Exception as e:
            print(str(e))
            return None
        
    def get_employee_email(self, obj):
        try:
            # organization_id = self.context.get('organization_id')
            if obj.created_by.is_admin:
                return obj.created_by.email
            
            query=Employees.objects.filter(hrmsuser=obj.created_by.id,is_active=True)
            if not query.exists():
                return None
            obj=query.get()
            return obj.personal_email
        except Exception as e:
            print(str(e))
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



# class KpisCommentsSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = KpisComments
#         fields = [
#             'id',
#             'employee_kpi',
#             'comments',
#             'created_by',
#             'is_active',
#         ]

class UniqueEmployeeKpiSerializers(serializers.ModelSerializer):
    
    employee_kpis_data = serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = [
            
            'employee_kpis_data',
        ]
           
   

    def get_employee_kpis_data(self, obj):
        try:
            
            # print(unique_employee_list)
            employee_kpis = self.context.get('query')
            ep_types = self.context.get('ep_types')

            data= EmployeesKpisDataView(
                    obj,
                    context = {'emp': obj, 'kpis': employee_kpis,'ep_types':ep_types},
                ).data
                

            return data

        except Exception as e:
            print(str(e))
            return None



class SimpleEmployeeKpiSerializers(serializers.ModelSerializer):
    
    employee_kpis_data = serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = [
            
            'employee_kpis_data',
        ]

    def get_employee_kpis_data(self, obj):
        try:
            # print(unique_employee_list)
            employee_kpis = self.context.get('query')
            ep_types = self.context.get('ep_types')
            data= SimpleEmployeesKpisDataView(
                    obj,
                    context = {'emp': obj, 'kpis': employee_kpis,'ep_types':ep_types},
                ).data
                

            return data

        except Exception as e:
            print(str(e))
            return None





# class CancelEmployeeKpiSerializers(serializers.ModelSerializer):
    
#     employee_kpis_data = serializers.SerializerMethodField()
#     class Meta:
#         model = Employees
#         fields = [
            
#             'employee_kpis_data',
#         ]
           
   

#     def get_employee_kpis_data(self, obj):
#         try:
            
#             # print(unique_employee_list)
#             employee_kpis = self.context.get('query')
#             ep_types = self.context.get('ep_types')

#             data= CancelEmployeesKpisDataView(
#                     obj,
#                     context = {'emp': obj, 'kpis': employee_kpis,'ep_types':ep_types},
#                 ).data
                

#             return data

#         except Exception as e:
#             print(str(e))
#             return None


class UniqueEmployeesListSerializers(serializers.ModelSerializer):
    evaluator = serializers.SerializerMethodField()
    evaluator_name = serializers.SerializerMethodField()
    employee_kpis_data = serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = [
            'evaluator',
            'evaluator_name',
            'employee_kpis_data',
        ]
           
    def get_evaluator(self, obj):
        try:
            return obj.id
        except Exception as e:
            return None

    def get_evaluator_name(self, obj):
        try:
            return obj.name
        except Exception as e:
            return None

    def get_employee_kpis_data(self, obj):
        try:
            unique_employee_list = self.context.get('unique_employee_list')
            employee_kpis = self.context.get('query')
            ep_types = self.context.get('ep_types')
            data = []
            # print("Data")
            for kpi_id in unique_employee_list:
                kpis = employee_kpis.filter(employee=kpi_id)
                if not kpis.exists():
                    continue
                employees = Employees.objects.filter(id=kpi_id)
                if not employees.exists():
                    continue

                serializer = EmployeesKpisDataView(
                    employees,
                    context = {'emp': kpi_id, 'kpis': kpis,'ep_types':ep_types},
                    many=True
                )
                data.append(serializer.data)

            return data

        except Exception as e:
            print(str(e))
            return None



class SimpleUniqueEmployeesListSerializers(serializers.ModelSerializer):
    evaluator = serializers.SerializerMethodField()
    evaluator_name = serializers.SerializerMethodField()
    employee_kpis_data = serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = [
            'evaluator',
            'evaluator_name',
            'employee_kpis_data',
        ]
           
    def get_evaluator(self, obj):
        try:
            return obj.id
        except Exception as e:
            return None

    def get_evaluator_name(self, obj):
        try:
            return obj.name
        except Exception as e:
            return None

    def get_employee_kpis_data(self, obj):
        try:
            unique_employee_list = self.context.get('unique_employee_list')
            employee_kpis = self.context.get('query')
            ep_types = self.context.get('ep_types')
            data = []
            # print("Data")
            for kpi_id in unique_employee_list:
                kpis = employee_kpis.filter(employee=kpi_id)
                if not kpis.exists():
                    continue
                employees = Employees.objects.filter(id=kpi_id)
                if not employees.exists():
                    continue

                serializer = SimpleEmployeesKpisDataView(
                    employees,
                    context = {'emp': kpi_id, 'kpis': kpis,'ep_types':ep_types},
                    many=True
                )
                data.append(serializer.data)

            return data

        except Exception as e:
            print(str(e))
            return None




class HrListDataSerializers(serializers.ModelSerializer):
    evaluator = serializers.SerializerMethodField()
    evaluator_name = serializers.SerializerMethodField()
    employee_kpis_data = serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = [
            'evaluator',
            'evaluator_name',
            'employee_kpis_data',
        ]
           
    def get_evaluator(self, obj):
        try:
            return obj.id
        except Exception as e:
            return None

    def get_evaluator_name(self, obj):
        try:
            return obj.name
        except Exception as e:
            return None

    def get_employee_kpis_data(self, obj):
        try:
            employee_kpis = self.context.get('query')
            kpis = employee_kpis.filter(evaluator=obj.id)
            ep_types = self.context.get('ep_types')
            if not kpis.exists():
                return None

            unique_employee_list = list(set([kpi.employee.id for kpi in kpis]))
            unique_employee_list.sort()

            data = []
            for emp in unique_employee_list:
                query = Employees.objects.filter(id=emp)
                serializer = EmployeesKpisDataView(
                    query,
                    context = {'emp': emp, 'kpis': kpis,'ep_types':ep_types},
                    many=True
                )
                data.append(serializer.data)
            
                

            return data

        except Exception as e:
            print(str(e))
            return None



class SimpleHrListDataSerializers(serializers.ModelSerializer):
    evaluator = serializers.SerializerMethodField()
    evaluator_name = serializers.SerializerMethodField()
    employee_kpis_data = serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = [
            'evaluator',
            'evaluator_name',
            'employee_kpis_data',
        ]
           
    def get_evaluator(self, obj):
        try:
            return obj.id
        except Exception as e:
            return None

    def get_evaluator_name(self, obj):
        try:
            return obj.name
        except Exception as e:
            return None

    def get_employee_kpis_data(self, obj):
        try:
            employee_kpis = self.context.get('query')
            kpis = employee_kpis.filter(evaluator=obj.id)
            ep_types = self.context.get('ep_types')
            if not kpis.exists():
                return None
            
            unique_employee_list = list(set([kpi.employee.id for kpi in kpis]))
            unique_employee_list.sort()
            data = []
            for emp in unique_employee_list:
                query = Employees.objects.filter(id=emp)
                serializer = SimpleEmployeesKpisDataView(
                    query,
                    context = {'emp': emp, 'kpis': kpis,'ep_types':ep_types},
                    many=True
                )
                data.append(serializer.data)
                

            return data

        except Exception as e:
            print(str(e))
            return None




class EmployeesDataView(serializers.ModelSerializer):
    employee_kpis_data = serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = [
            'id',
            'name',
            'employee_kpis_data',
        ]

    def get_employee_kpis_data(self, obj):
        try:
            employee = self.context.get('emp')
            employee_kpis = self.context.get('kpis')
            kpis_data = employee_kpis.filter(employee=employee).order_by('id')
            if kpis_data.exists():
                data = EmployeesKpisSerializers(kpis_data, many=True).data
            else:
                data = None

            return data

        except Exception as e:
            print(str(e))
            return None

class EmployeesKpisDataView(serializers.ModelSerializer):
    employee_kpis_data = serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = [
            'id',
            'name',
            'employee_kpis_data',
        ]

    def get_employee_kpis_data(self, obj):
        try:
            employee = self.context.get('emp')
            employee_kpis = self.context.get('kpis')
            ep_types = self.context.get('ep_types')
            kpis_data = employee_kpis.filter(employee=employee).order_by('id')
            
            if not kpis_data.exists():
                return None
            
            data = EPTypeBaseEmployeekpis(
                    ep_types,
                    context = {'kpis_data': kpis_data},
                    many=True
                ).data
            
            return data

        except Exception as e:
            print(str(e))
            return None



class NewEmployeesKpisDataView(serializers.ModelSerializer):
    # employee_kpis_data = serializers.SerializerMethodField()
    employment_type_title=serializers.SerializerMethodField()
    total_kpis=serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = [
            'id',
            'name',
            'employee_type',
            'employment_type_title',
            'profile_image',
            'total_kpis',
        ]

    def get_total_kpis(self, obj):
        try:
            employee_kpis = self.context.get('query')
            # ep_types = self.context.get('ep_types')
            # print("Test")
            count = employee_kpis.filter(employee=obj.id).count()
            
            return count

        except Exception as e:
            print(str(e))
            return None
        

    def get_employment_type_title(self,obj):
        try:
            return obj.employee_type.title
        except Exception as e:
            return None





class SimpleEmployeesKpisDataView(serializers.ModelSerializer):
    employee_kpis_data = serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = [
            'id',
            'name',
            'employee_kpis_data',
        ]

    def get_employee_kpis_data(self, obj):
        try:
            employee = self.context.get('emp')
            employee_kpis = self.context.get('kpis')
            ep_types = self.context.get('ep_types')
            # print(ep_types)
            kpis_data = employee_kpis.filter(employee=employee).order_by('id')
            # ep_type_kpi_data = kpis_data.filter(ep_type=11)
            # print('kpis ep type data')
            # print(ep_type_kpi_data.values)
            if not kpis_data.exists():
                return None
                # data = ListEmployeesKpisSerializers(kpis_data, many=True).data
            
            data = SimpleEPTypeBaseEmployeekpis(
                    ep_types,
                    context = {'kpis_data': kpis_data},
                    many=True
                ).data
            # print(data)
            # print('get employee kpis data')
            return data

        except Exception as e:
            print(str(e))
            return None






class EPTypeBaseEmployeekpis(serializers.ModelSerializer):
    employee_kpis_data=serializers.SerializerMethodField()
    class Meta:
        model = EPTypes
        fields = [
            'id',
            'title',
            'employee_kpis_data',
            'key',
            'organization',
            'created_by',
            'is_active',
        ]

    def to_representation(self, instance):
        employee_kpis_data = self.get_employee_kpis_data(instance)
        
        if employee_kpis_data is None:
            # Return None for instances where employee_kpis_data is None
            return None

        representation = super().to_representation(instance)
        representation['employee_kpis_data'] = employee_kpis_data
        return representation
  
    def get_employee_kpis_data(self, obj):
        try:
            
            employee_kpis = self.context.get('kpis_data')
            # print(employee_kpis.values())
            kpis_data = employee_kpis.filter(ep_type=obj.id).order_by('id')
            if kpis_data.exists():
                
                data = ListEmployeesKpisSerializers(kpis_data, many=True).data
               
            else:
                data = None

            return data
        except Exception as e:
            print(str(e))
            return None


class SimpleEPTypeBaseEmployeekpis(serializers.ModelSerializer):
    employee_kpis_data=serializers.SerializerMethodField()
    class Meta:
        model = EPTypes
        fields = [
            'id',
            'title',
            'employee_kpis_data',
            'key',
            'organization',
            'created_by',
            'is_active',
        ]
  
    def get_employee_kpis_data(self, obj):
        try:
            employee_kpis = self.context.get('kpis_data')
            # print(employee_kpis.values())
            kpis_data = employee_kpis.filter(ep_type=obj.id).order_by('id')
            # print(kpis_data)
            if kpis_data.exists():
                # print('kpi data exist')
                data = EmployeesKpisSerializers(kpis_data, many=True).data
                # print('employee kpi data ')
                # print(data)
            else:
                data = None

            return data
        except Exception as e:
            print(str(e))
            return None

  

class KpisLogsSerializers(serializers.ModelSerializer):
    class Meta:
        model = KpisLogs
        fields = [
            'id',
            'employees_kpi',
            'request_type',
            'ep_complexity',
            'kpis_status',
            'title',
            'objectives',
            'ep_batch',
            'ep_scaling',
            'mmtr',
            'target_dates',
            'evaluator',
            'created_by',
            'is_active',
        ]

# new add for kpis evaluation process
   
# class ListKPIScaleGroupsSerializers(serializers.ModelSerializer):
#     kpi_aspects=serializers.SerializerMethodField()
#     scale_group_title=serializers.SerializerMethodField()
#     ep_type_title = serializers.SerializerMethodField()
#     ep_complexity_title = serializers.SerializerMethodField()
#     ep_batch_title = serializers.SerializerMethodField()
#     project_title=serializers.SerializerMethodField()
#     evaluation_status_title=serializers.SerializerMethodField()
#     kpis_status_title = serializers.SerializerMethodField()
#     ep_type= serializers.SerializerMethodField()
#     ep_complexity= serializers.SerializerMethodField()
#     ep_batch= serializers.SerializerMethodField()
#     employee_project=serializers.SerializerMethodField()
#     evaluation_status=serializers.SerializerMethodField()
#     kpis_status= serializers.SerializerMethodField()
#     kpi_title = serializers.SerializerMethodField()
#     class Meta:
#         model = KPIScaleGroups
#         fields = [
#             'id',
#             'kpi_id',
#             'kpi_title',
#             'ep_type',
#             'ep_type_title',
#             'ep_complexity',
#             'ep_complexity_title',
#             'ep_batch',
#             'ep_batch_title',
#             'employee_project',
#             'project_title',
#             'evaluation_status',
#             'evaluation_status_title',
#             'kpis_status',
#             'kpis_status_title',
#             'scale_group',
#             'scale_group_title',
#             'result',
#             'score',
#             'comment',
#             'assign_by',
#             'approved_by',
#             'is_active',
#             'created_at',
#             'updated_at',
#             'kpi_aspects',
#         ]


#     def get_scale_group_title(self, obj):
#             try:
                
#                 return obj.scale_group.title
#             except Exception as e:
#                 print(str(e))
#                 return None
            
#     def get_project_title(self, obj):
#         try:
#             return obj.kpi_id.employee_project.project.name
#         except Exception as e:
#             return None
        
    
#     def get_ep_type_title(self, obj):
#         try:
#             return obj.kpi_id.ep_type.title
#         except Exception as e:
#             return None
        
            
#     def get_evaluation_status_title(self,obj):
#         try:
#             if obj.kpi_id.evaluation_status in [1,2,3]:
#                 return Evaluation_Status[int(obj.kpi_id.evaluation_status)-1][1]
            
#             return None
           
#         except Exception as e:
#             return None
        

        
    
#     def get_ep_batch_title(self, obj):
#         try:
#             return obj.kpi_id.ep_batch.title
#         except Exception as e:
#             return None
        
#     def get_ep_complexity_title(self, obj):
#         try:
#             return obj.kpi_id.ep_complexity.title
#         except Exception as e:
#             return None

#     def get_kpis_status_title(self, obj):
#         try:
#             return obj.kpi_id.kpis_status.status_title
#         except Exception as e:
#             return None
        
#     def get_kpi_title(self, obj):
#         try:
#             return obj.kpi_id.title
#         except Exception as e:
#             return None
        

            
#     def get_employee_project(self, obj):
#         try:
#             return obj.kpi_id.employee_project.id
#         except Exception as e:
#             return None
        
    
#     def get_ep_type(self, obj):
#         try:
#             return obj.kpi_id.ep_type.id
#         except Exception as e:
#             return None
        
            
#     def get_evaluation_status(self,obj):
#         try:
#             if obj.kpi_id.evaluation_status in [1,2,3]:
#                 return obj.kpi_id.evaluation_status
            
#             return None
           
#         except Exception as e:
#             return None
        

        
    
#     def get_ep_batch(self, obj):
#         try:
#             return obj.kpi_id.ep_batch.id
#         except Exception as e:
#             return None
        
#     def get_ep_complexity(self, obj):
#         try:
#             return obj.kpi_id.ep_complexity.id
#         except Exception as e:
#             return None

#     def get_kpis_status(self, obj):
#         try:
#             return obj.kpi_id.kpis_status.id
#         except Exception as e:
#             return None
        
#     def get_kpi_title(self, obj):
#         try:
#             return obj.kpi_id.title
#         except Exception as e:
#             return None
        

            
#     def get_kpi_aspects(self, obj):
#             try:
                
#                 # print('KPI Scale Group id: ')
#                 # print(obj.id)
                
#                 query = KPIAspects.objects.filter(kpi_sg=obj.id, is_active=True)
#                 if not query.exists():
#                     return None
#                 serializers = ListKPIAspectsSerializers(query, many=True)
#                 # print("Aspect:",serializers.data)
#                 return serializers.data
#             except Exception as e:
#                 print(str(e))
#                 return None
            
# class ListEmployeesKpisSerializers(serializers.ModelSerializer):
#     # ep_type_title = serializers.SerializerMethodField()
#     # ep_complexity_title = serializers.SerializerMethodField()
#     employee_name = serializers.SerializerMethodField()
#     # kpis_status_title = serializers.SerializerMethodField()
#     evaluator_name = serializers.SerializerMethodField()
#     # ep_batch_title = serializers.SerializerMethodField()
#     # project_title=serializers.SerializerMethodField()
#     # scale_group_title=serializers.SerializerMethodField()
#     # evaluation_status_title=serializers.SerializerMethodField()
#     mode_of_kpis_title=serializers.SerializerMethodField()

#     class Meta:
#         model = EmployeesKpis
#         fields = [
#             'id',
#             'employee',
#             'employee_name',
#             'title',
#             'objectives',
#             'ep_type',
#             # 'ep_type_title',
#             'ep_batch',
#             # 'ep_batch_title',
#             'ep_complexity',
#             # 'ep_complexity_title',
#             'mode_of_kpis',
#             'mode_of_kpis_title',
#             'employee_project',
#             # 'project_title',
#             'scale_group',
#             # 'scale_group_title',
#             # 'scale_complexity',
#             'mmtr',
#             'target_dates',
#             'evaluator',
#             'evaluator_name',
#             'kpis_status',
#             # 'kpis_status_title',
#             'evaluation_status',
#             # 'evaluation_status_title',
#             'created_by',
#             'is_active',
#         ]
#     def get_evaluator_name(self, obj):
#         try:
#             return obj.evaluator.name
#         except Exception as e:
#             return None

#     # def get_project_title(self, obj):
#     #     try:
#     #         return obj.employee_project.name
#     #     except Exception as e:
#     #         return None
        
#     def get_scale_group_title(self, obj):
#         try:
#             return obj.scale_group.title
#         except Exception as e:
#             return None
        
#     # def get_scale_complexity_title(self, obj):
#     #     try:
#     #         return obj.scale_complexity.title
#     #     except Exception as e:
#     #         return None
    
#     def get_employee_name(self, obj):
#         try:
#             return obj.employee.name
#         except Exception as e:
#             return None

#     def get_ep_type_title(self, obj):
#         try:
#             return obj.ep_type.title
#         except Exception as e:
#             return None
        
#     # def get_ep_batch_no(self, obj):
#     #     try:
#     #         return obj.ep_batch.batch_no
#     #     except Exception as e:
#     #         return None
        
    
#     def get_ep_batch_title(self, obj):
#         try:
#             return obj.ep_batch.title
#         except Exception as e:
#             return None
        
#     def get_ep_complexity_title(self, obj):
#         try:
#             return obj.ep_complexity.title
#         except Exception as e:
#             return None

#     def get_kpis_status_title(self, obj):
#         try:
#             return obj.kpis_status.status_title
#         except Exception as e:
#             return None
        
#     # def get_kpis_status_level(self, obj):
#     #     try:
#     #         return obj.kpis_status.level
#     #     except Exception as e:
#     #         return None
        
#     # def get_comments(self, obj):
#     #     try:
#     #         query = KpisComments.objects.filter(employee_kpi=obj.id)
#     #         serializer = KpisCommentsSerializers(query, many=True)
#     #         return serializer.data
#     #     except Exception as e:
#     #         return None
        
#     def get_evaluation_status_title(self,obj):
#         try:
#             if obj.evaluation_status:
#                 return Evaluation_Status[int(obj.evaluation_status)-1][1]
            
#             return None
           
#         except Exception as e:
#             return None
        
#     def get_mode_of_kpis_title(self,obj):
#         try:
#             if obj.mode_of_kpis in [1,2,3,4]:
#                 return Kip_Mode_CHOICES[obj.mode_of_kpis-1][1]
            
#             return None
           
#         except Exception as e:
#             return None
        
#     # def get_scale_groups_data(self, obj):
#     #     try:
            
#     #         query = KPIScaleGroups.objects.filter(kpi_id=obj.id,is_active=True)
#     #         # print(query.values())
#     #         serializer = ListKPIScaleGroupsSerializers(query, many=True)
            

#     #         return serializer.data
#     #     except Exception as e:
#     #         return None
        
class ListEmployeesKpisSerializers(serializers.ModelSerializer):
    ep_type_title = serializers.SerializerMethodField()
    ep_complexity_title = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    kpis_status_title = serializers.SerializerMethodField()
    kpis_status_level=serializers.SerializerMethodField()
    evaluator_name = serializers.SerializerMethodField()
    ep_batch_title = serializers.SerializerMethodField()
    project_title=serializers.SerializerMethodField()
    scale_group_title=serializers.SerializerMethodField()
    evaluation_status_title=serializers.SerializerMethodField()
    mode_of_kpis_title=serializers.SerializerMethodField()
    kpis_objective_title=serializers.SerializerMethodField()
    class Meta:
        model = EmployeesKpis
        fields = [
            'id',
            'employee',
            'employee_name',
            'title',
            'description',
            'objectives',
            'kpis_objective',
            'kpis_objective_title',
            'ep_type',
            'ep_type_title',
            'ep_batch',
            'ep_batch_title',
            'ep_complexity',
            'ep_complexity_title',
            'mode_of_kpis',
            'mode_of_kpis_title',
            'employee_project',
            'project_title',
            'scale_group',
            'scale_group_title',
            'mmtr',
            'target_dates',
            'evaluator',
            'evaluator_name',
            'kpis_status',
            'kpis_status_title',
            'kpis_status_level',
            'evaluation_status',
            'evaluation_status_title',
            'created_by',
            'is_active',
        ]

    def get_kpis_objective_title(self,obj):
        try:
            return obj.kpis_objective.title
        except Exception as e:
            return None
        
    def get_evaluator_name(self, obj):
        try:
            return obj.evaluator.name
        except Exception as e:
            return None
        
    def get_kpis_status_level(self, obj):
        try:
            return obj.kpis_status.level
        except Exception as e:
            return None
        

    def get_project_title(self, obj):
        try:
            return obj.employee_project.project.name
        except Exception as e:
            return None
        
    def get_scale_group_title(self, obj):
        try:
            return obj.scale_group.title
        except Exception as e:
            return None
        
    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            return None

    def get_ep_type_title(self, obj):
        try:
            return obj.ep_type.title
        except Exception as e:
            return None
        

        
    
    def get_ep_batch_title(self, obj):
        try:
            return obj.ep_batch.title
        except Exception as e:
            return None
        
    def get_ep_complexity_title(self, obj):
        try:
            return obj.ep_complexity.title
        except Exception as e:
            return None

    def get_kpis_status_title(self, obj):
        try:
            return obj.kpis_status.status_title
        except Exception as e:
            return None
        

        
    def get_evaluation_status_title(self,obj):
        try:
            if obj.evaluation_status:
                return Evaluation_Status[int(obj.evaluation_status)-1][1]
            
            return None
           
        except Exception as e:
            return None
        
    def get_mode_of_kpis_title(self,obj):
        try:
            if obj.mode_of_kpis in [1,2,3,4]:
                return Kip_Mode_CHOICES[obj.mode_of_kpis-1][1]
            
            return None
           
        except Exception as e:
            return None
        
class ListKPIScaleGroupsSerializers(serializers.ModelSerializer):
    kpi_aspects=serializers.SerializerMethodField()
    scale_group_title=serializers.SerializerMethodField()
    have_aspects=serializers.SerializerMethodField()
    is_default_group=serializers.SerializerMethodField()
    class Meta:
        model = KPIScaleGroups
        fields = [
            'id',
            'kpi_id',
            'scale_group',
            'have_aspects',
            'is_default_group',
            'scale_group_title',
            'result',
            'score',
            'comment',
            'assign_by',
            'approved_by',
            'is_active',
            'created_at',
            'updated_at',
            'kpi_aspects',
        ]

    def get_have_aspects(self,obj):
        try:
            return obj.scale_group.have_aspects
        except Exception as e:
            print(str(e))
            return None
        
    def get_is_default_group(self,obj):
        try:
            return obj.scale_group.is_default_group
        except Exception as e:
            print(str(e))
            return None


    def get_scale_group_title(self, obj):
            try:
                
                return obj.scale_group.title
            except Exception as e:
                print(str(e))
                return None
            

            
            
    def get_kpi_aspects(self, obj):
            try:
                
                # print('KPI Scale Group id: ')
                # print(obj.id)
                
                query = KPIAspects.objects.filter(kpi_sg=obj.id, is_active=True)
                if not query.exists():
                    return None
                serializers = ListKPIAspectsSerializers(query, many=True)
                # print("Aspect:",serializers.data)
                return serializers.data
            except Exception as e:
                print(str(e))
                return None
      
class ListKPIAspectsSerializers(serializers.ModelSerializer):
    parameters=serializers.SerializerMethodField()
    aspect_group_title=serializers.SerializerMethodField()
    class Meta:
        model = KPIAspects
        fields = [
            'id',
            'kpi_sg',
            'ep_aspects',
            'aspect_group_title',
            'comment',
            'result',
            'score',
            'created_at',
            'updated_at',
            'is_active',
            'parameters',
        ]

    def get_aspect_group_title(self, obj):
            try:
                
                return obj.ep_aspects.title
            except Exception as e:
                print(str(e))
                return None
            
    def get_parameters(self, obj):
            try:
                query = KPIAspectsParameterRating.objects.filter(kpi_aspects=obj.id, is_active=True)
                # print(query.values())
                if not query.exists():
                    return None
                
                serializers = ListKPIAspectsParametersSerializers(query, many=True)
                # print("Parameter",serializers.data)
                return serializers.data
            except Exception as e:
                print(str(e))
                return None

class ListKPIAspectsParametersSerializers(serializers.ModelSerializer):
    parameter_group_title=serializers.SerializerMethodField()
    required_parameter=serializers.SerializerMethodField()
    class Meta:
        model = KPIAspectsParameterRating
        fields = [
            'id', 
            'kpi_aspects',
            'parameters',
            'parameter_group_title',
            'scale_rating',
            'comment',
            'result',
            'score',
            'required_parameter',
            'is_required',
            'created_at',
            'updated_at',
            'is_active',
        ]

    def get_parameter_group_title(self, obj):
            try:
                
                return obj.parameters.title
            except Exception as e:
                print(str(e))
                return None
            
    def get_required_parameter(self, obj):
            try:
                
                return obj.parameters.is_required
            except Exception as e:
                print(str(e))
                return None
            


      
class NewEmployeesKpisSerializers(serializers.ModelSerializer):
    # employee_name = serializers.SerializerMethodField()
    kpis_status_title = serializers.SerializerMethodField()
    evaluator_name = serializers.SerializerMethodField()
   

    class Meta:
        model = EmployeesKpis
        fields = [
            'id',
            'employee',
            # 'employee_name',
            'evaluator',
            'evaluator_name',
            'kpis_status',
            'kpis_status_title',
            
        ]
    def get_evaluator_name(self, obj):
        try:
            return obj.evaluator.name
        except Exception as e:
            return None


    
    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            return None

        


    def get_kpis_status_title(self, obj):
        try:
            return obj.kpis_status.status_title
        except Exception as e:
            return None
        
  

class DepartmentKpisPreformanceSerializers(serializers.ModelSerializer):
    employee_kpis_data=serializers.SerializerMethodField()
    class Meta:
        model = Departments
        fields = [
            'id',
            'grouphead',
            'title',
            'description',
            'status',
            'employee_kpis_data',
            'created_by',
            'is_active',
        ]


    def get_employee_kpis_data(self, obj):
        try:
            employee = self.context.get('employee').filter(department=obj.id)
            kpis_data = self.context.get('kpis_data').filter(employee__department=obj.id)
            employee_data = DepartmentEmployeesKpisDataView(employee, many=True, context={'kpis_data': kpis_data}).data
            return employee_data
        except Exception as e:
            print(str(e))
            return None

 
class DepartmentEmployeesKpisDataView(serializers.ModelSerializer):
    # employee_kpis_data = serializers.SerializerMethodField()
    employment_type_title=serializers.SerializerMethodField()
    total_kpis_result=serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = [
            'id',
            'name',
            'employee_type',
            'employment_type_title',
            'profile_image',
            'total_kpis_result',
        ]

    def get_total_kpis_result(self, obj):
        try:
            kpis_data = self.context.get('kpis_data')
            kpis_employee=kpis_data.filter(employee=obj.id)
            # print("Test")
            kpis_evaluated_count=kpis_employee.count()
            kpis_avarage_score=0.0
            if kpis_evaluated_count >0:
                sg_result=0.0
                for kpis in kpis_employee:
                    sg_data=KPIScaleGroups.objects.get(kpi_id=kpis.id,is_active=True)
                    if sg_data is not None:
                            result=float(sg_data.result)
                            sg_result += result

                kpis_avarage_score=round(sg_result/kpis_evaluated_count,2)
            
            return kpis_avarage_score

        except Exception as e:
            print(str(e))
            return None
        

    def get_employment_type_title(self,obj):
        try:
            return obj.employee_type.title
        except Exception as e:
            return None
        

class DepartmentKpisObjectivesSerializers(serializers.ModelSerializer):
    employee_kpis_data=serializers.SerializerMethodField()
    org_id=serializers.SerializerMethodField()
    class Meta:
        model = Departments
        fields = [
            'id',
            'grouphead',
            'title',
            'description',
            'status',
            'org_id',
            'employee_kpis_data',
            'created_by',
            'is_active',
        ]

 

 
    def get_org_id(self, obj):
        try:
            
            return obj.grouphead.organization.id
        except Exception as e:
            print(str(e))
            return None
    
    def get_employee_kpis_data(self, obj):
        try:
            employee = self.context.get('employee').filter(department=obj.id)
            kpis_data = self.context.get('kpis_data').filter(employee__department=obj.id)
            employee_data = DepartmentEmployeesKpisObjectivesDataView(employee, many=True, context={'kpis_data': kpis_data}).data
            return employee_data
        except Exception as e:
            print(str(e))
            return None

class DepartmentEmployeesKpisObjectivesDataView(serializers.ModelSerializer):
    total_carry_forward = serializers.SerializerMethodField()
    employment_type_title=serializers.SerializerMethodField()
    total_completed=serializers.SerializerMethodField()
    total_count=serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = [
            'id',
            'name',
            'employee_type',
            'employment_type_title',
            'profile_image',
            'total_count',
            'total_completed',
            'total_carry_forward',
            

        ]

    def get_total_count(self, obj):
        try:
            kpis_data = self.context.get('kpis_data')
            kpis_employee=kpis_data.filter(employee=obj.id)
            kpis_total_count=max(kpis_employee.count(), 0)
            return  kpis_total_count

        except Exception as e:
            print(str(e))
            return None

    def get_total_completed(self, obj):
        try:
            kpis_data = self.context.get('kpis_data')
            kpis_employee=kpis_data.filter(employee=obj.id)
            kpis_total_count=max(kpis_employee.count(), 0)
            kpis_completed_count=max(kpis_employee.filter(evaluation_status=1).count(),0)
            print(kpis_total_count,kpis_completed_count)
            count=0
            count=max(kpis_completed_count,0)
            return count

        except Exception as e:
            print(str(e))
            return None
        
    def get_total_carry_forward(self, obj):
        try:
            kpis_data = self.context.get('kpis_data')
            kpis_employee=kpis_data.filter(employee=obj.id)
            kpis_total_count=max(kpis_employee.count(), 0)
            kpis_completed_count=max(kpis_employee.filter(evaluation_status=3).count(),0)
            print(kpis_total_count,kpis_completed_count)
            count=0
            
            count=max(kpis_completed_count,0)
            return count

        except Exception as e:
            print(str(e))
            return None
        

    def get_employment_type_title(self,obj):
        try:
            return obj.employee_type.title
        except Exception as e:
            return None
        

class DepartmentKpisComplexitySerializers(serializers.ModelSerializer):
    total_count=serializers.SerializerMethodField()
    heigh_complixity=serializers.SerializerMethodField()
    medium_complixity=serializers.SerializerMethodField()
    low_complixity=serializers.SerializerMethodField()
    class Meta:
        model = Departments
        fields = [
            'id',
            'grouphead',
            'title',
            'description',
            'status',
            'total_count',
            'heigh_complixity',
            'medium_complixity',
            'low_complixity',
            'created_by',
            'is_active',
        ]

    def get_total_count(self, obj):
        try:
            kpis_data = self.context.get('kpis_data').filter(employee__department=obj.id).count()
            return  kpis_data

        except Exception as e:
            print(str(e))
            return None


    def get_heigh_complixity(self, obj):
        try:
            kpis_data = self.context.get('kpis_data').filter(employee__department=obj.id,ep_complexity__level=1).count()
            return kpis_data
        except Exception as e:
            print(str(e))
            return None
        
    def get_medium_complixity(self, obj):
        try:
            kpis_data = self.context.get('kpis_data').filter(employee__department=obj.id,ep_complexity__level=2).count()
            return kpis_data
        except Exception as e:
            print(str(e))
            return None
        
    def get_low_complixity(self, obj):
        try:
            kpis_data = self.context.get('kpis_data').filter(employee__department=obj.id,ep_complexity__level=3).count()
            return kpis_data
        except Exception as e:
            print(str(e))
            return None
