import os
from rest_framework import serializers
from .models import *

from django.db.models.functions import Lower, Substr
from django.db.models import F, Value

class TasksStatusSerializer(serializers.ModelSerializer):
    project_name=serializers.SerializerMethodField()
    class Meta:
        model = TasksStatus
        fields = ['id','title', 'level', 'project','project_name','organization','created_by', 'is_active', 'created_at', 'updated_at']
    def get_project_name(self,obj):
        try:
            if obj.project:
                return obj.project.name
            return None
        except Exception as e:
            return None
        
class TaskTypesSerializer(serializers.ModelSerializer):
    project_name=serializers.SerializerMethodField()
    class Meta:
        model = TaskTypes
        fields = ['id','title', 'level','organization','project','project_name','created_by', 'is_active', 'created_at', 'updated_at']
    
    def get_project_name(self,obj):
        try:
            if obj.project:
                return obj.project.name
            return None
        except Exception as e:
            return None
        

class TaskGroupsSerializer(serializers.ModelSerializer):
    project_name=serializers.SerializerMethodField()
    created_by_name=serializers.SerializerMethodField()
    task_count=serializers.SerializerMethodField()
    task_details=serializers.SerializerMethodField()
    class Meta:
        model = TaskGroups
        fields = ['id','title','organization','task_count','task_details','project','project_name','created_by', 'created_by_name','is_active', 'created_at', 'updated_at']
    
    def get_project_name(self,obj):
        try:
            if obj.project:
                return obj.project.name
            return None
        except Exception as e:
            return None
        
    def get_created_by_name(self,obj):
        try:
            if obj.created_by:
                return obj.created_by.first_name+' '+obj.created_by.last_name
            return None
        except Exception as e:
            return None   
        
    def get_task_count(self,obj):
        try:
            query=TaskGroupLinks.objects.filter(group=obj.id,is_active=True).count()
            return query
        except Exception as e:
            return None
        
    
    

    def get_task_details(self,obj):
        try:
            query=TaskGroupLinks.objects.filter(group=obj.id,is_active=True)
            task_ids = query.values_list('task_id', flat=True)  # Extract only task IDs as a list

            # Step 3: Fetch task data for the extracted task IDs
            tasks = Tasks.objects.filter(id__in=task_ids, is_active=True).order_by('-id')
            serializer = TasksSerializer(tasks, many=True).data
            return serializer
        except Exception as e:
            return None
        
    
class TasksSerializer(serializers.ModelSerializer):
    employee_name=serializers.SerializerMethodField()
    assign_to_name=serializers.SerializerMethodField()
    status_title=serializers.SerializerMethodField()
    task_type_title=serializers.SerializerMethodField()
    project_name=serializers.SerializerMethodField()
    # children=serializers.SerializerMethodField()
    profile_image_employee=serializers.SerializerMethodField()
    profile_image_assign_to=serializers.SerializerMethodField()
    comment_count=serializers.SerializerMethodField()
    attachment_count=serializers.SerializerMethodField()
    attachment_image=serializers.SerializerMethodField()
    class Meta:
        model = Tasks
        fields = ['id','title','employee','employee_name','profile_image_employee','assign_to','assign_to_name','profile_image_assign_to', 'project','project_name','parent','is_child','estimated_time','start_date','due_date','planned_hours','actual_hours','account_hour','external_ticket_reference',
                  'status','status_title','task_type','task_type_title','priority','description', 'time_log',
                  'created_by', 'is_active', 'created_at', 'updated_at','comment_count','attachment_count','attachment_image']

    def get_employee_name(self,obj):
        try:
            if obj.employee:
                return obj.employee.name
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
        
    def get_status_title(self,obj):
        try:
            if obj.status:
                return obj.status.title
            return None
        except Exception as e:
            return None

        
    def get_task_type_title(self,obj):
        try:
            if obj.task_type:
                return obj.task_type.title
            return None
        except Exception as e:
            return None
        

        
    def get_project_name(self,obj):
        try:
            if obj.project:
                return obj.project.name
            return None
        except Exception as e:
            return None
        
    def get_children(self,obj):
        try:
            children = Tasks.objects.filter(parent=obj)
            if children.exists():
                return TasksSerializer(children, many=True).data
            return None
        except Exception as e:
            return None
        
    def get_profile_image_employee(self, obj):
        try:
            
            query=Employees.objects.filter(id=obj.employee.id,is_active=True)
            if not query.exists():
                return None
            obj=query.get()
            return obj.profile_image.url
        except Exception as e:
            print(str(e))
            return None 
        
    def get_profile_image_assign_to(self, obj):
        try:
            
            query=Employees.objects.filter(id=obj.assign_to.id,is_active=True)
            if not query.exists():
                return None
            obj=query.get()
            return obj.profile_image.url
        except Exception as e:
            print(str(e))
            return None 
        
    def get_attachment_count(self, obj):
        try:
            
            query=TaskAttachments.objects.filter(task=obj.id,is_active=True).count()
            return query
        except Exception as e:
            print(str(e))
            return None 
        
    def get_comment_count(self, obj):
        try:
            
            query=TaskComment.objects.filter(task=obj.id,is_active=True).count()
            return query
        except Exception as e:
            print(str(e))
            return None 
        
    def get_attachment_image(self, obj):
        try:
            # Retrieve all active attachments for the task, ordered by newest
            query = TaskAttachments.objects.filter(
                task=obj.id,
                is_active=True
            ).order_by('-id')

            # Allowed extensions
            allowed_extensions = {"jpg", "jpeg", "png"}

            # Filter files by extension
            for attachment in query:
                file_extension = os.path.splitext(attachment.attachment.name)[-1].lower().strip('.')
                if file_extension in allowed_extensions:
                    return attachment.attachment.url # Return the first matching file
            return None  # No valid image found
        except Exception as e:
            print(str(e))
            return None




class TaskAttachmentsSerializer(serializers.ModelSerializer):
    created_by_name=serializers.SerializerMethodField()
    class Meta:
        model = TaskAttachments
        fields = ['id','task', 'comment','created_by','created_by_name','attachment','is_active', 'created_at', 'updated_at']
        
    
    def get_created_by_name(self,obj):
        try:
            if obj.created_by:
                return obj.created_by.first_name+' '+obj.created_by.last_name
            return None
        except Exception as e:
            return None    
        

    def validate_attachment(self, value):
        try:
            if value:
                max_size = 5 * 1024 * 1024
                if value.size > max_size:
                    raise serializers.ValidationError
                
                # print("Test:",value)
            return value
        except serializers.ValidationError:
            raise serializers.ValidationError("Attachment file size cannot be greater than 5MB")
        except Exception as e:
            print(str(e))
            return None
        
class TaskTimeLogsSerializer(serializers.ModelSerializer):
    created_by_name=serializers.SerializerMethodField()
    status_title=serializers.SerializerMethodField()
    employee_name=serializers.SerializerMethodField()
    profile_image=serializers.SerializerMethodField()
    class Meta:
        model = TaskTimeLogs
        fields = [
            'id',  # Add ID field to uniquely identify each log
            'employee',
            'employee_name',
            'profile_image',
            'task',
            'date',
            'hours_spent',
            'log_description',
            'status',
            'status_title',
            'created_by',
            'created_by_name',
            'is_active',
            'created_at',
            'updated_at',
        ]

    def get_created_by_name(self,obj):
        try:
            if obj.created_by:
                return obj.created_by.first_name+' '+obj.created_by.last_name
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
        
    def get_profile_image(self, obj):
        try:
            # organization_id = self.context.get('organization_id')
            if obj.created_by.is_admin:
                return obj.created_by.profile_image.url
            
            query=Employees.objects.filter(id=obj.employee.id,is_active=True)
            if not query.exists():
                return None
            obj=query.get()
            return obj.profile_image.url
        except Exception as e:
            print(str(e))
            return None 
        
    def get_status_title(self,obj):
        try:
            if obj.status:
                return obj.status.title
            return None
        except Exception as e:
            return None
    
class TaskCommentSerializer(serializers.ModelSerializer):
    created_by_name=serializers.SerializerMethodField()
    profile_image=serializers.SerializerMethodField()
    attachments=serializers.SerializerMethodField()
    class Meta:
        model = TaskComment
        fields = ['id','task', 'comment','created_by','created_by_name','profile_image','is_active', 'created_at', 'updated_at','attachments']
        
    
    def get_created_by_name(self,obj):
        try:
            if obj.created_by:
                return obj.created_by.first_name+' '+obj.created_by.last_name
            return None
        except Exception as e:
            return None    
        
    def get_attachments(self,obj):
        try:
            query=TaskAttachments.objects.filter(comment=obj.id,is_active=True)
            if query.exists():
                serializers=TaskAttachmentsSerializer(query,many=True).data

                return serializers
            
            return None

        except Exception as e:
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
   
        
class TaskLogsSerializer(serializers.ModelSerializer):
    created_by_name=serializers.SerializerMethodField()
    status_title=serializers.SerializerMethodField()
    task_type_title=serializers.SerializerMethodField()
    project_name=serializers.SerializerMethodField()
    assign_to_name=serializers.SerializerMethodField()
    created_by_image=serializers.SerializerMethodField()
    
    class Meta:
        model = TaskLogs
        fields = ['id', 'task', 'title', 'estimated_time', 'task_type','task_type_title', 'description','date','hours_spent',
                  'priority', 'project','project_name','parent','planned_hours','actual_hours','account_hour','external_ticket_reference','start_date','due_date','assign_to',
                  'assign_to_name','status','status_title','is_deactivated', 'created_by','created_by_name','created_by_image',
                  'is_active', 'created_at', 'updated_at']
        
    def get_created_by_name(self,obj):
        try:
            if obj.created_by:
                return obj.created_by.first_name+' '+obj.created_by.last_name
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
        
    def get_status_title(self,obj):
        try:
            if obj.status:
                return obj.status.title
            return None
        except Exception as e:
            return None

    
    def get_project_name(self,obj):
        try:
            if obj.project:
                return obj.project.name
            return None
        except Exception as e:
            return None

        
    def get_task_type_title(self,obj):
        try:
            if obj.task_type:
                return obj.task_type.title
            return None
        except Exception as e:
            return None
        

    def get_created_by_image(self, obj):
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
        
    def to_representation(self, instance):
        # Get the default representation
        representation = super().to_representation(instance)
        
        # Filter out fields with null values
        filtered_representation = {key: value for key, value in representation.items() if value is not None or (key == 'is_deactivated' and value is True)}
        
        return filtered_representation


class TaskswithTimeLogsSerializer(serializers.ModelSerializer):
    employee_name=serializers.SerializerMethodField()
    assign_to_name=serializers.SerializerMethodField()
    status_title=serializers.SerializerMethodField()
    task_type_title=serializers.SerializerMethodField()
    project_name=serializers.SerializerMethodField()
    # children=serializers.SerializerMethodField()
    task_time_logs=serializers.SerializerMethodField()
    parent_title=serializers.SerializerMethodField()
    class Meta:
        model = Tasks
        fields = ['id','title','parent','parent_title','employee','employee_name','assign_to','assign_to_name','project','project_name','estimated_time','start_date','due_date','planned_hours','actual_hours','account_hour','external_ticket_reference','status','status_title','task_type','task_type_title','priority','description','task_time_logs', 'is_active', 'created_at', 'updated_at']

    def get_employee_name(self,obj):
        try:
            if obj.employee:
                return obj.employee.name
            return None
        except Exception as e:
            return None
        
    def get_parent_title(self,obj):
        try:
            if obj.parent:
                return obj.parent.title
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
        
    def get_status_title(self,obj):
        try:
            if obj.status:
                return obj.status.title
            return None
        except Exception as e:
            return None
    
    def get_project_name(self,obj):
        try:
            if obj.project:
                return obj.project.name
            return None
        except Exception as e:
            return None

        
    def get_task_type_title(self,obj):
        try:
            if obj.task_type:
                return obj.task_type.title
            return None
        except Exception as e:
            return None
        
    def get_task_time_logs(self, obj):
        try:
            query = self.context.get('query')
            if query:
                return TaskTimeLogsSerializer(query, many=True).data
            return None
        except Exception as e:
            # Log or handle the exception as needed
            return None
        

class TaskGroupLinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskGroupLinks
        fields = ['id', 'task', 'group', 'is_active', 'created_at', 'updated_at']
