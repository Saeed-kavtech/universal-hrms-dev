from rest_framework import serializers
from .models import *
from kpis.models import *
# from kpis.serializers import *


class KPIScaleGroupsSerializers(serializers.ModelSerializer):
    have_aspects=serializers.SerializerMethodField()
    class Meta:
        model = KPIScaleGroups
        fields = [
            'id',
            'kpi_id',
            'scale_group',
            'have_aspects',
            'comment',
            'result',
            'score',
            'assign_by',
            'approved_by',
            'created_at',
            'updated_at',
            'is_active',
        ]

    def get_have_aspects(self,obj):
        try:
            return obj.scale_group.have_aspects
        except Exception as e:
            return None

class KPIAspectsSerializers(serializers.ModelSerializer):
    class Meta:
        model = KPIAspects
        fields = [
            'id',
            'kpi_sg',
            'ep_aspects',
            'comment',
            'result',
            'score',
            'created_at',
            'updated_at',
            'is_active',
        ]

class KPIAspectsParametersSerializers(serializers.ModelSerializer):
    class Meta:
        model = KPIAspectsParameterRating
        fields = [
            'id',
            'kpi_aspects',
            'parameters',
            'scale_rating',
            'comment',
            'result',
            'score',
            'is_required',
            'created_at',
            'updated_at',
            'is_active',
        ]
    
# class ListKPIScaleGroupsSerializers(serializers.ModelSerializer):
#     kpi_aspects=serializers.SerializerMethodField()
#     class Meta:
#         model = KPIScaleGroups
#         fields = [
#             'id',
#             'kpi_id',
#             'scale_group',
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

#     def get_kpi_aspects(self, obj):
#             try:
                
#                 print('KPI Scale Group id: ')
#                 print(obj.id)

#                 query = KPIAspects.objects.filter(kpi_sg=obj.id, is_active=True)
#                 print(query.values())
#                 serializers = ListKPIAspectsSerializers(query, many=True)
#                 return serializers.data
#             except Exception as e:
#                 print(str(e))
#                 return None
            
# class ListEmployeesKpisSerializers(serializers.ModelSerializer):
#     ep_type_title = serializers.SerializerMethodField()
#     ep_complexity_title = serializers.SerializerMethodField()
#     ep_batch_no = serializers.SerializerMethodField()
#     employee_name = serializers.SerializerMethodField()
#     kpis_status_title = serializers.SerializerMethodField()
#     kpis_status_level = serializers.SerializerMethodField()
#     evaluator_name = serializers.SerializerMethodField()
#     comments = serializers.SerializerMethodField()
#     scale_groups_data = serializers.SerializerMethodField()
#     project_title=serializers.SerializerMethodField()
#     scale_group_title=serializers.SerializerMethodField()
#     scale_complexity_title=serializers.SerializerMethodField()

#     class Meta:
#         model = EmployeesKpis
#         fields = [
#             'id',
#             'employee',
#             'employee_name',
#             'title',
#             'objectives',
#             'ep_type',
#             'ep_type_title',
#             'ep_batch',
#             'ep_batch_no',
#             'ep_complexity',
#             'ep_complexity_title',
#             'employee_project',
#             'project_title',
#             'scale_group',
#             'scale_group_title',
#             'scale_complexity',
#             'scale_complexity_title',
#             'mmtr',
#             'target_dates',
#             'evaluator',
#             'evaluator_name',
#             'kpis_status',
#             'kpis_status_title',
#             'kpis_status_level',
#             'comments',
#             'scale_groups_data',
#             'created_by',
#             'is_active',
#         ]
#     def get_evaluator_name(self, obj):
#         try:
#             return obj.evaluator.name
#         except Exception as e:
#             return None

#     def get_project_title(self, obj):
#         try:
#             return obj.employee_project.name
#         except Exception as e:
#             return None
        
#     def get_scale_group_title(self, obj):
#         try:
#             return obj.scale_group.title
#         except Exception as e:
#             return None
        
#     def get_scale_complexity_title(self, obj):
#         try:
#             return obj.scale_complexity.title
#         except Exception as e:
#             return None
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
        
#     def get_ep_batch_no(self, obj):
#         try:
#             return obj.ep_batch.batch_no
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
        
#     def get_kpis_status_level(self, obj):
#         try:
#             return obj.kpis_status.level
#         except Exception as e:
#             return None
        
#     def get_comments(self, obj):
#         try:
#             query = KpisComments.objects.filter(employee_kpi=obj.id)
#             serializer = KpisCommentsSerializers(query, many=True)
#             return serializer.data
#         except Exception as e:
#             return None
        
#     def get_scale_groups_data(self, obj):
#         try:
#             # print("Test")
#             query = KPIScaleGroups.objects.filter(kpi_id=obj.id,is_active=True)
#             # print(query.values())
#             serializer = ListKPIScaleGroupsSerializers(query, many=True)
#             return serializer.data
#         except Exception as e:
#             return None
        

# class ListKPIAspectsSerializers(serializers.ModelSerializer):
#     parameters=serializers.SerializerMethodField()
#     class Meta:
#         model = KPIAspects
#         fields = [
#             'id',
#             'kpi_sg',
#             'ep_aspects',
#             'comment',
#             'result',
#             'score',
#             'created_at',
#             'updated_at',
#             'is_active',
#             'parameters',
#         ]

#     def get_parameters(self, obj):
#             try:
#                 print('parameters aspect id:  ')
#                 print(obj.id)
#                 print(' parameters: ')
#                 query = KPIAspectsParameterRating.objects.filter(kpi_aspects=obj.id, is_active=True)
#                 print(query.values())
                
#                 serializers = ListKPIAspectsParametersSerializers(query, many=True)
#                 return serializers.data
#             except Exception as e:
#                 print(str(e))
#                 return None

# class ListKPIAspectsParametersSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = KPIAspectsParameterRating
#         fields = [
#             'id',
#             'kpi_aspects',
#             'parameters',
#             'scale_rating',
#             'comment',
#             'result',
#             'score',
#             'created_at',
#             'updated_at',
#             'is_active',
#         ]