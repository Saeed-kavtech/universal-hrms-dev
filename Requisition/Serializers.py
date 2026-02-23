from rest_framework import serializers
from .models import *
class ReplacementForSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = ReplacementFor
        fields = '__all__'
        
        
class EmployeeRequisitionSerializers(serializers.ModelSerializer):
    supervisor_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    status_title = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    class Meta:
        model = EmployeeRequisition
        fields = '__all__'
        
    def get_supervisor_name(self, obj):
        try:
            return obj.supervisor.name
        except Exception as e:
            print(str(e))
            return None
    def get_created_by_name(self, obj):
        try:
            return obj.created_by.first_name
        except Exception as e:
            print(str(e))
            return None
        
    def get_department(self, obj):
        try:
            return obj.position.department.id
        except Exception as e:
            print(str(e))
            return None
        
    def get_position_title(self, obj):
        try:
            return obj.position.title
        except Exception as e:
            print(str(e))
            return None
    def get_status_title(self,obj):
        try:
            if obj.status:
                return Requisition_Status[obj.status-1][1]
                
            return None
        except Exception as e:
            print(str(e))
            return None
    