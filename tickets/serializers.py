from rest_framework import serializers
from .models import *

class TicketCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketCategory
        fields = [
            'id', 
            'title', 
            'organization', 
            'is_department', 
            'is_main_admin', 
            'created_by', 
            'is_active', 
            'created_at', 
            'updated_at'
        ]


class TicketCategoryDepartmentSerializer(serializers.ModelSerializer):
    department_title=serializers.SerializerMethodField()
    ticket_category_title=serializers.SerializerMethodField()
    class Meta:
        model = TicketCategoryDepartment
        fields = [
            'id', 
            'ticket_category',
            'ticket_category_title',
            'department',
            'department_title',
            'created_by', 
            'is_active', 
            'created_at', 
            'updated_at'
        ]
        
           
    def get_department_title(self,obj):
        try:
            if obj.department:
                return obj.department.title
            return None
        except Exception as e:
            return None
        
    def get_ticket_category_title(self,obj):
        try:
            if obj.ticket_category:
                return obj.ticket_category.title
            return None
        except Exception as e:
            return None


class TicketDepartmentEmployeeSerializer(serializers.ModelSerializer):
    employee_name=serializers.SerializerMethodField()
    department_title=serializers.SerializerMethodField()
    department=serializers.SerializerMethodField()
    class Meta:
        model = TicketDepartmentEmployee
        fields = [
            'id', 
            'ticket_category_department',
            'department',
            'department_title',
            'employee',
            'employee_name',
            'created_by', 
            'is_active', 
            'created_at', 
            'updated_at'
        ]
 
        
    def get_employee_name(self,obj):
        try:
            if obj.employee:
                return obj.employee.name
            return None
        except Exception as e:
            return None
        
    def get_department(self,obj):
        try:
            if obj.ticket_category_department:
                return obj.ticket_category_department.department.id
            return None
        except Exception as e:
            return None
        
    def get_department_title(self,obj):
        try:
            if obj.ticket_category_department:
                return obj.ticket_category_department.department.title
            return None
        except Exception as e:
            return None



class TicketSerializer(serializers.ModelSerializer):
    employee_name=serializers.SerializerMethodField()
    transfer_to_name=serializers.SerializerMethodField()
    assign_to_name=serializers.SerializerMethodField()
    team_lead_name=serializers.SerializerMethodField()
    ticket_status_title=serializers.SerializerMethodField()
    category_title=serializers.SerializerMethodField()
    ticket_department_title=serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id','employee','employee_name','ticket_department','ticket_department_title','subject', 'description','category','category_title','team_lead','team_lead_name','assign_to','assign_to_name', 'transfer_to','transfer_to_name',  'ticket_status','ticket_status_title', 'created_by', 'is_active','send_to_admin', 'created_at', 'updated_at']
    
    def get_ticket_department_title(self,obj):
        try:
            if obj.ticket_department:
                return obj.ticket_department.title
            return None
        except Exception as e:
            return None
        
    def get_employee_name(self,obj):
        try:
            if obj.employee:
                return obj.employee.name
            return None
        except Exception as e:
            return None
        
    def get_transfer_to_name(self,obj):
        try:
            if obj.transfer_to:
                return obj.transfer_to.name
            return None
        except Exception as e:
            return None
        
    def get_team_lead_name(self,obj):
        try:
            if obj.team_lead:
                return obj.team_lead.name
            return None
        except Exception as e:
            return None
        
    
    def get_assign_to_name(self,obj):
        try:
            if obj.assign_to:
                return obj.assign_to.name
            return None
        except Exception as e:
            return None
        
        
    def get_category_title(self,obj):
        try:
            if obj.category:
                return obj.category.title
            return None
        
        except Exception as e:
            return None
        
    def get_ticket_status_title(self,obj):
        try:
            if obj.ticket_status in [1,2,3,4,5,6,7,8,9,10,11,12,13]:
                return status_choices[obj.ticket_status-1][1]
            return None
        
        except Exception as e:
            return None
        

class TicketLogsSerializer(serializers.ModelSerializer):
    ticket_status_title=serializers.SerializerMethodField()
    decision_by_name=serializers.SerializerMethodField()
    class Meta:
        model = TicketLogs
        fields = ['id','ticket', 'decision_reason', 'ticket_status','ticket_status_title','decision_by','decision_by_name','is_active', 'created_at', 'updated_at']
        
    def get_decision_by_name(self,obj):
        try:
            if obj.decision_by:
                return obj.decision_by.first_name+" "+obj.decision_by.last_name
            return None
        except Exception as e:
            return None
    
    def get_ticket_status_title(self,obj):
        try:
            if obj.ticket_status in [1,2,3,4,5,6,7,8,9,10,11,12,13]:
                return status_choices[obj.ticket_status-1][1]
            
            return None
        
        except Exception as e:
            return None