import datetime
import json
from django.db import connection
from django.shortcuts import render
import pandas as pd
from django.utils import timezone
from employees.serializers import PreEmployeesDataSerializers
from employees.views_project_roles import EmployeeProjectsRolesViewset
from projects.serializers import PreProjectDataViewSerializers
from reimbursements.models import EmployeeLeaveDates
from reimbursements.serializers import EmployeeLeaveDatesSerializers
from .models import *
from .serializers import *
from rest_framework import viewsets
from .serializers import *
from .models import *
from helpers.status_messages import *
from helpers.decode_token import decodeToken
from django.db.models import Q
from helpers.status_messages import *
from helpers.custom_permissions import IsAuthenticated,IsAdminOnly,IsEmployeeOnly
from projects.models import Projects
from employees.models import EmployeeProjects, EmployeeRoles
from django.core.paginator import Paginator

# Create your views here.
class TasksStatusViewset(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    queryset=TasksStatus.objects.all()
    serializer_class=TasksStatusSerializer

    def create(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            user_id = request.user.id
            
            required_fields = ['title','level']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all required fields','title,level')
            
            check_query=self.queryset.filter(organization=organization_id,is_active=True)

            # print("test")

            if check_query.exists():

                    if check_query.filter(title=request.data['title'],project__isnull=True).exists():
                        return errorMessage("This status title already exists in this group")
                    
                    elif check_query.filter(level=request.data['level'],project__isnull=True).exists():
                        return errorMessage("This level  already exists in this stauts group")
                
            project=request.data.get('project',None)

            if project is not None:
                

                employee_query=Projects.objects.filter(id=project,organization=organization_id,is_active=True)

                if not employee_query.exists():
                    return errorMessage("Project not exists in current organization")

                if check_query.filter(project=project).exists():

                    if check_query.filter(title=request.data['title']).exists():
                        return errorMessage("This status title already exists in this group")
                    
                    elif check_query.filter(level=request.data['level']).exists():
                        return errorMessage("This level  already exists in this stauts group")
                


            
            request.data['organization']=organization_id
            request.data['created_by'] = user_id

            serializer=self.serializer_class(data = request.data)

            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)

        except Exception as e:
          return exception(e)
        
        
    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            check_query=self.queryset.filter(organization=organization_id,is_active=True)
            serializer =self.serializer_class(check_query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
    
    def pre_data(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            check_query=self.queryset.filter(organization=organization_id,is_active=True)
            default_status=check_query.filter(project__isnull=True)
            serializer =self.serializer_class(default_status, many=True)
            project_status_list=[]
            project=request.data.get('project',None)
            if project is not None:
                project_status=check_query.filter(project=project)
                project_serializer =self.serializer_class(project_status, many=True)
                project_status_list.extend(project_serializer.data)
               

            task_type={
                "default_status":serializer.data,
                "project_status":project_status_list

            }
            
            return success(task_type)
        except Exception as e:
            return exception(e)
        
        

    
        
    def taskify_projects(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            obj = Projects.objects.filter(organization=organization_id,is_active=True)
            serializer = PreProjectDataViewSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

class TaskTypesViewset(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    queryset=TaskTypes.objects.all()
    serializer_class=TaskTypesSerializer

    def create(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            
            user_id = request.user.id
            
            required_fields = ['title','level']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all required fields','title,level')
            
            check_query=self.queryset.filter(organization=organization_id,is_active=True)
            

            if check_query.exists():
                    

                    if check_query.filter(title=request.data['title'],project__isnull=True).exists():
                        return errorMessage("This status title already exists")
                    
                    elif check_query.filter(level=request.data['level'],project__isnull=True).exists():
                        return errorMessage("This level  already assign to other title")
                
            project=request.data.get('project',None)

            if project is not None:
                employee_query=Projects.objects.filter(id=project,organization=organization_id,is_active=True)

                if not employee_query.exists():
                    return errorMessage("Project not exists in current organization")

                if check_query.filter(project=project).exists():

                    if check_query.filter(title=request.data['title']).exists():
                        return errorMessage("This status title already exists")
                    
                    elif check_query.filter(level=request.data['level']).exists():
                        return errorMessage("This level  already assign to other title")
                

                

            
            request.data['organization']=organization_id
            request.data['created_by'] = user_id

            serializer=self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)

        except Exception as e:
          return exception(e)
        
    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            check_query=self.queryset.filter(organization=organization_id,is_active=True)
            serializer =self.serializer_class(check_query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
    
    def pre_data(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            check_query=self.queryset.filter(organization=organization_id,is_active=True)
            default_type=check_query.filter(project__isnull=True)
            serializer =self.serializer_class(default_type, many=True)
            project_task_list=[]
            project=request.data.get('project',None)
            if project is not None:
                project_task=check_query.filter(project=project)
                project_serializer =self.serializer_class(project_task, many=True)
                project_task_list.extend(project_serializer.data)
               

            task_type={
                "default_task_type":serializer.data,
                "project_task_type":project_task_list

            }
            
            return success(task_type)
        except Exception as e:
            return exception(e)


class TaskGroupsViewset(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    queryset=TaskGroups.objects.all()
    serializer_class=TaskGroupsSerializer

    def create(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            # print("test")
            user_id = request.user.id

            project_id=self.kwargs['project_id']
            # print(project_id)
            required_fields = ['title']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all required fields','title')
            
            # check_query=self.queryset.filter(organization=organization_id,project=project_id,is_active=True)
            

            # if check_query.exists():

            #         if check_query.filter(title=request.data['title']).exists():
            #             return errorMessage("This group already exists")
                
            # project=request.data.get('project',None)

            # if project is not None:
            #     employee_query=Projects.objects.filter(id=project,organization=organization_id,is_active=True)

            #     if not employee_query.exists():
            #         return errorMessage("Project not exists in current organization")

            #     if check_query.filter(project=project).exists():

            #         if check_query.filter(title=request.data['title']).exists():
            #             return errorMessage("This status title already exists")
                    
            #         elif check_query.filter(level=request.data['level']).exists():
            #             return errorMessage("This level  already assign to other title")
                

                

            
            request.data['organization']=organization_id
            request.data['created_by'] = user_id

            serializer=self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            group=serializer.save()
            tasks_array = list(request.data.get('tasks_array'))
            # Initialize an error list to capture any error IDs
            error_ids = []

            for task in tasks_array:
                task_query = Tasks.objects.filter(id=task, project=project_id, is_active=True)
                
                if task_query.exists():
                    task_obj = task_query.get()

                    # Check if the task is already linked to the same group
                    existing_link = TaskGroupLinks.objects.filter(task=task_obj, group=group)
                    
                    if existing_link.exists():
                        # If the task is linked to the same group, do nothing
                        continue
                    
                    # Check if task is linked to a different group, if so deactivate the old link
                    existing_link = TaskGroupLinks.objects.filter(task=task_obj, is_active=True)
                    if existing_link.exists():
                        # Deactivate the existing link
                        existing_link.update(is_active=False)
                    
                    # Create a new TaskGroupLink for the task and group
                    TaskGroupLinks.objects.create(task=task_obj, group=group, is_active=True)
                else:
                    # If the task doesn't exist or is inactive, add to error list
                    error_ids.append(task)  # Append the task ID that failed validation

            # Return or log the error_ids as needed
            if error_ids:
               return errorMessageWithData("Some task are not link with group",error_ids)


            return successMessageWithData("Success",serializer.data)

        except Exception as e:
          return exception(e)
        
    # def list(self, request, *args, **kwargs):
    #     try:
    #         organization_id = decodeToken(request, self.request)['organization_id']
    #         user=request.user.id
    #         project_id=self.kwargs['project_id']
    #         check_query=self.queryset.filter(organization=organization_id,project=project_id,created_by=user,is_active=True)
    #         serializer =self.serializer_class(check_query, many=True)
    #         return success(serializer.data)
    #     except Exception as e:
    #         return exception(e)
    def list(self, request, *args, **kwargs):
        try:
            # Decode organization ID from the token
            organization_id = decodeToken(request, self.request)['organization_id']
            user = request.user.id
            project_id = self.kwargs['project_id']

            # Fetch all groups for the project
            groups = self.queryset.filter(organization=organization_id, project=project_id, is_active=True)

            # Prepare grouped tasks data
            group_data = []
            linked_task_ids = set()  # To track tasks already linked to groups

            for group in groups:
                # Get task IDs linked to this group
                group_task_ids = TaskGroupLinks.objects.filter(group=group.id, is_active=True).values_list('task_id', flat=True)
                linked_task_ids.update(group_task_ids)

                # Fetch task details
                group_tasks = Tasks.objects.filter(id__in=group_task_ids, is_active=True)
                group_serializer = TasksSerializer(group_tasks, many=True).data

                group_data.append({
                    "group_id": group.id,
                    "group_title": group.title,
                    "tasks": group_serializer
                })

            # Fetch all tasks for the project
            all_tasks = Tasks.objects.filter(project_id=project_id, is_active=True)

            # Find ungrouped tasks
            ungrouped_tasks = all_tasks.exclude(id__in=linked_task_ids)
            ungrouped_serializer = TasksSerializer(ungrouped_tasks, many=True).data

            # Prepare the response
            response_data = {
                "groups": group_data,
                "default_group": {
                    "group_title": "Default Group",
                    "tasks": ungrouped_serializer
                }
            }

            return success(response_data)

        except Exception as e:
            return exception(e)

        
    def patch(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            user_id = request.user.id

            group_id=self.kwargs['group_id']
            
            check_query=self.queryset.filter(id=group_id,organization=organization_id,is_active=True)
            if not check_query.exists():
                return errorMessage("Group not exists")
            
            elif not check_query.filter(created_by=user_id).exists():
                        return errorMessage("You don't have access to update this group")
            
            obj=check_query.get()

            serializer=self.serializer_class(obj,data = request.data,partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()

            return successMessageWithData("Success",serializer.data)

        except Exception as e:
          return exception(e)
        
    def delete(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            user_id = request.user.id

            group_id=self.kwargs['group_id']
            
            check_query=self.queryset.filter(id=group_id,organization=organization_id,is_active=True)
            if not check_query.exists():
                return errorMessage("Group not exists")
            
            elif not check_query.filter(created_by=user_id).exists():
                        return errorMessage("You don't have access to delete this group")
            obj=check_query.get()
            obj.is_active=False
            obj.save()
            TaskGroupLinks.objects.filter(group=obj.id).update(is_active=False)
            return successMessage("Success")

        except Exception as e:
          return exception(e)
        
    def get_group_based_tasks(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            group_id = self.kwargs['group_id']
            user_id = request.user.id

            page_number = request.data.get('page', None)
            if page_number is not None:
                page_number = int(page_number)
            else:
                page_number = 1


            results_per_page = request.data.get('pagination_limit', None)
            if results_per_page is not None:
                results_per_page = int(results_per_page)
            else:
                results_per_page = 20
            # Step 1: Fetch all task links associated with the group
            task_links = TaskGroupLinks.objects.filter(
                group=group_id, group__created_by=user_id, is_active=True
            )

            # Step 2: Extract all task IDs from the task links
            task_ids = task_links.values_list('task_id', flat=True)  # Extract only task IDs as a list

            # Step 3: Fetch task data for the extracted task IDs
            tasks = Tasks.objects.filter(id__in=task_ids, is_active=True).order_by('-id')

            # Step 4: Serialize the task data
            paginator_data = Paginator(tasks, results_per_page)
            total_pages = paginator_data.num_pages

            current_page_data = paginator_data.get_page(page_number) 
            serializer = TasksSerializer(current_page_data, many=True)

            data={
                "task_data":serializer.data,
                "total_pages":total_pages
            }
            # serializer = TasksSerializer(tasks, many=True)
            return success(data)
        except Exception as e:
            return exception(e)
        
    def task_group_link(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            user_id = request.user.id
            
            group_id=self.kwargs['group_id']
            
            check_query=self.queryset.filter(id=group_id,organization=organization_id,created_by=user_id,group__isactive=True,is_active=True)
            if not check_query.exists():
                return errorMessage("Group not exists")     
            obj=check_query.get()
            tasks_array = list(request.data.get('tasks_array'))

            # Initialize an error list to capture any error IDs
            error_ids = []
            if tasks_array:
             for task in tasks_array:
                task_query = Tasks.objects.filter(id=task, project=obj.project, is_active=True)
                
                if task_query.exists():
                    task_obj = task_query.get()

                    # Check if the task is already linked to the same group
                    existing_link = TaskGroupLinks.objects.filter(task=task_obj, group=obj,is_active=True)
                    
                    if existing_link.exists():
                        # If the task is linked to the same group, do nothing
                        continue
                    
                    # Check if task is linked to a different group, if so deactivate the old link
                    existing_link = TaskGroupLinks.objects.filter(task=task_obj, is_active=True)
                    if existing_link.exists():
                        # Deactivate the existing link
                        existing_link.update(is_active=False)
                    
                    # Create a new TaskGroupLink for the task and group
                    TaskGroupLinks.objects.create(task=task_obj, group=obj, is_active=True)
                else:
                    # If the task doesn't exist or is inactive, add to error list
                    error_ids.append(task)  # Append the task ID that failed validation

            # Return or log the error_ids as needed
            if error_ids:
               return errorMessageWithData("Some task are not link with group",error_ids)


            return successMessage("Success")

        except Exception as e:
          return exception(e)




class TasksViewset(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    queryset=Tasks.objects.all()
    serializer_class=TasksSerializer


    
    
    def create(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id=token_data['employee_id']

            required_fields = ['title','description','assign_to','project','task_type','priority']
            if not all(field in request.data for field in required_fields):
                        return errorMessageWithData('make sure you have added all required fields','title,description,assign_to,project,task_type,priority')
            
            request.data._mutable = True
            
            query_stauts_check=TasksStatus.objects.filter(level=1,organization=organization_id,is_active=True)
            if not query_stauts_check.exists():
                return errorMessage('status not exists')
            
            employee_query=Projects.objects.filter(id=request.data['project'],organization=organization_id,is_active=True)

            if not employee_query.exists():
                return errorMessage("Project not exists in current organization")
            
            project_task_type=request.data.get('project_task_type',False)
            

            if project_task_type==True:
                query_type_check=TaskTypes.objects.filter(id=request.data['task_type'],project=request.data['project'],project__isnull=False,organization=organization_id,is_active=True)
                if not query_type_check.exists():
                    return errorMessage('project task type not exists')
                
            else:
                query_type_check=TaskTypes.objects.filter(id=request.data['task_type'],project__isnull=True,organization=organization_id,is_active=True)
                if not query_type_check.exists():
                    return errorMessage('task type not exists')
                
            parent=request.data.get("parent",None)

            if parent:
                check_parent_query=self.queryset.filter(id=parent,employee__organization=organization_id,is_active=True)
                if not check_parent_query.exists():
                    return errorMessage('parent not exists')
                request.data['is_child']=True

            
            status=query_stauts_check.get()
            request.data['status']=status.id
            request.data['created_by'] = request.user.id
            request.data['employee'] = employee_id
            request.data['is_active']=True
            
            serializer=self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            task_instance=serializer.save()
            comment=None
            attachment_data = request.data.getlist('attachments')
            attachment_serializer_errors=[]
            for attachment in attachment_data:
                    date_check=task_attachments(task_instance,request.user.id,attachment,comment)
                    if date_check['status'] == 400:
                        attachment_serializer_errors.append(date_check['message'])
                        continue
            if attachment_serializer_errors:
                return errorMessageWithData("Task added but some attachemnets not added",attachment_serializer_errors)
            
            return successfullyCreated(serializer.data)
            
        except Exception as e:
            return exception(e)
  
    
    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            project_id=self.kwargs['project_id']

            query = self.queryset.filter(project=project_id,is_child=False,employee__organization=organization_id,is_active=True).order_by('-id')
            
            status=request.data.get('status',None)
            is_active=request.data.get('is_active',None)
            task_type=request.data.get("task_type",None)
            priority=request.data.get("priority",None)
            assign_to=request.data.get("assign_to",None)
            employee=request.data.get("employee",None)
            page_number = request.data.get('page', None)
            if page_number is not None:
                page_number = int(page_number)
            else:
                page_number = 1


            results_per_page = request.data.get('pagination_limit', None)
            if results_per_page is not None:
                results_per_page = int(results_per_page)
            else:
                results_per_page = 20
            
            if status is not None: 
                query=query.filter(status=status)
                
            if is_active is not None:
                query=query.filter(is_active=is_active)

            if task_type is not None:
                query=query.filter(task_type=task_type)

            if priority is not None:
                query=query.filter(priority=priority)

            if assign_to is not None:
                query=query.filter(assign_to=assign_to)

            if employee is not None:
                query=query.filter(employee=employee)


            paginator_data = Paginator(query, results_per_page)
            total_pages = paginator_data.num_pages

            current_page_data = paginator_data.get_page(page_number) 
            serializer = self.serializer_class(current_page_data, many=True)

            data={
                "task_data":serializer.data,
                "total_pages":total_pages
            }

            
            
            return success(data)
        except Exception as e:
            return exception(e)
        
    def get_single_data(self,request,*args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            pk=self.kwargs['pk']
            query = self.queryset.filter(id=pk,employee__organization=organization_id,is_active=True)
            serializer = self.serializer_class(query,many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
            
        except Exception as e:
            return exception(e)
        
    def get_child_task(self,request,*args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            parent_id=self.kwargs['parent_id']
            query = self.queryset.filter(parent=parent_id,is_child=True,employee__organization=organization_id,is_active=True).order_by('id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
          exception(e)
        
    def patch(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            user_id=request.user.id
            pk = self.kwargs['pk']
            if not request.data:
                return errorMessage("Request Data is empty")

            query=self.queryset.filter(id=pk,employee__organization=organization_id,is_active=True)

            if not query.exists():
                    return errorMessage("Data not exists in current organization")
            
            parent=request.data.get("parent",None)

            if parent:
                check_parent_query=self.queryset.filter(id=parent,employee__organization=organization_id,is_active=True)
                if not check_parent_query.exists():
                    return errorMessage('parent not exists')
                
            obj=query.get()
            request_data=request.data

            date_check=task_logs(obj,user_id,request_data)
            if date_check['status'] == 400:
                    return errorMessage(date_check['message'])
            
            serializer=self.serializer_class(obj, data = request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            

            return successfullyUpdated(serializer.data)
            
        except Exception as e:
            return exception(e)
        


    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            user_id=request.user.id
            query = self.queryset.filter(id=pk)
            if not query.exists():
                return errorMessage('Task does not exists')
            if not query.filter(is_active=True).exists():
                return errorMessage('Task is already deactivated at this id')
            
            if query.filter(status__level__gt=1).exists():
                return errorMessage('Task only deactived at its initial stages')
            obj = query.get()

            request_data={
                "is_deactivated":True
            }

            date_check=task_logs(obj,user_id,request_data)
            if date_check['status'] == 400:
                    return errorMessage(date_check['message'])
            
            obj.is_active=False
            obj.save()
            
            return successMessage('Task is deactivated successfully')
        except Exception as e:
            return exception(e)
        
    def update_task_stauts(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            # employee_id=token_data['employee_id']
            pk = self.kwargs['pk']
            user_id=request.user.id
            status = request.data.get('status', None)
            if not status:
                return errorMessage('status is a required field')
            
            query=self.queryset.filter(id=pk,employee__organization=organization_id,is_active=True)

            if not query.exists():
                    return errorMessage("The specified task is unavailable in the current organization")   
            
            if query.filter(status=status).exists():
                return successMessage("Same status already applied against this task")
            
            obj=query.get()

            project_status=request.data.get('project_status',False)
           
            query_stauts_check=TasksStatus.objects.filter(id=status,organization=organization_id,is_active=True)
            if project_status==True:
                query_stauts_check=query_stauts_check.filter(project=obj.project,project__isnull=False)
            
                if not query_stauts_check.exists():
                    return errorMessage('project status not exists')
                
            else:
                query_stauts_check=query_stauts_check.filter(id=status,project__isnull=True,)
                if not query_stauts_check.exists():
                    return errorMessage('status not exists')
                
            status_obj=query_stauts_check.get()

                
            request_data={
                "status":status
            }
            
            if status_obj.level==2 and obj.start_date is None:
               request_data['start_date']=datetime.datetime.today().date()

            date_check=task_logs(obj,user_id,request_data)
            if date_check['status'] == 400:
                    return errorMessage(date_check['message'])

            serializer=self.serializer_class(obj, data = request_data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            

            return successfullyUpdated(serializer.data)
            
        except Exception as e:
            return exception(e)
        
    def task_assign_to(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            project_id=self.kwargs['project_id']
            query = self.queryset.filter(project=project_id,assign_to=employee_id,employee__organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
        
    def task_created_by_employee(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            project_id=self.kwargs['project_id']
            query = self.queryset.filter(employee=employee_id,project=project_id,employee__organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    
    
    def employee_project(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id=token_data['employee_id']
            data=[]
            employee_projects=EmployeeProjects.objects.filter(employee=employee_id,employee__organization=organization_id,is_active=True)
            
            for projects in employee_projects:
                query=Projects.objects.filter(id=projects.project.id,is_active=True)
                serializer = PreProjectDataViewSerializers(query, many=True)
                data.extend(serializer.data)
            
            return success(data)
            
        except Exception as e:
            return exception(e)
        
    def project_employees(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            project_id=self.kwargs['project_id']
            data=[]
            projects_employee=EmployeeProjects.objects.filter(project=project_id,employee__organization=organization_id,is_active=True)
                
            for employee in projects_employee:
                query=Employees.objects.filter(id=employee.employee.id,is_active=True)
                serializer = PreEmployeesDataSerializers(query, many=True)
                data.extend(serializer.data)
            
            return success(data)
            
        except Exception as e:
            return exception(e)
        

class TaskTimeLogsViewset(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    queryset=TaskTimeLogs.objects.all()
    serializer_class=TaskTimeLogsSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Decode the token to get organization ID
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            # Get task primary key from URL kwargs
            pk = self.kwargs['pk']

            # Get user ID from request
            user_id = request.user.id

            task_query=Tasks.objects.filter(id=pk,employee__organization=organization_id,is_active=True)

            if not task_query.exists():
                return errorMessage("No task exists at this id")
            
            obj=task_query.get()
            
            
            required_fields = ['hours_spent','date']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all required fields','hours_spent,date')

            employee_id=request.data.get('employee',None)

            if employee_id:
                employee_query=Employees.objects.filter(id=employee_id,organization=organization_id,is_active=True)
                if not employee_query.exists():
                    return errorMessage("Employee not exists in organization")
            else:
                employee_id = token_data['employee_id']

            # Query to find if the log for this task, date, and organization already exists
            task_logs_query = self.queryset.filter(
                task=pk, 
                task__employee__organization=organization_id, 
                date=request.data['date'],
                created_by=user_id,
                is_active=True
            )
            
            if request.data['hours_spent'] > 24:
               return errorMessage('Hours spent cannot exceed 24 hours')
            
            request.data['status']=obj.status.id
            
            serializer=None
            # If a log already exists, update it
            if task_logs_query.exists():
                task_log = task_logs_query.first()
                request_data={
                    "status":task_log.status.id,
                    "hours_spent":task_log.hours_spent,
                    "date":task_log.date
                }
                date_check=task_logs(obj,user_id,request_data)
                if date_check['status'] == 400:
                        return errorMessage(date_check['message'])
                serializer = self.serializer_class(task_log, data=request.data, partial=True)
                if not serializer.is_valid():
                    return serializerError(serializer.errors)
                serializer.save()
                return successfullyUpdated(serializer.data)
            
            
            # If no log exists, create a new one
            else:
                request.data['created_by'] = user_id
                request.data['employee']=employee_id
                request.data['task']=pk
                serializer = self.serializer_class(data=request.data)
                if not serializer.is_valid():
                    return serializerError(serializer.errors)
                serializer.save()

            
            return successfullyCreated(serializer.data)

        except Exception as e:
            return exception(e)
        
    def list(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            organization_id = decodeToken(request, self.request)['organization_id']
            task_logs_query = self.queryset.filter(
                task=pk, 
                task__employee__organization=organization_id, 
                is_active=True
            )
            serializer =self.serializer_class(task_logs_query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def delete(self, request, *args, **kwargs):
        try:
            time_log_id = self.kwargs['time_log_id']
            user_id=request.user.id

            query = self.queryset.filter(id=time_log_id,created_by=user_id)
            if not query.exists():
                return errorMessage('Time log does not exists')
            if not query.filter(is_active=True).exists():
                return errorMessage('Time log is already deactivated at this id')
            
            obj = query.get()

            request_data={
                    "status":obj.status.id,
                    "hours_spent":obj.hours_spent,
                    "date":obj.date,
                    "is_deactivated":True
                }
            date_check=task_logs(obj,user_id,request_data)
            if date_check['status'] == 400:
                        return errorMessage(date_check['message'])
 
            obj.is_active=False
            obj.save()

            return successMessage('Time log deactivated successfully')
        except Exception as e:
            return exception(e)
        

    def task_report(self,request,*args, **kwargs):
        try:
            project_id = self.kwargs['project_id']
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id=request.data.get('employee',None)
            
            if employee_id:
                employee_query=Employees.objects.filter(id=employee_id,organization=organization_id,is_active=True)
                if not employee_query.exists():
                    return errorMessage("Employee not exists in organization")
            else:
                employee_id = decodeToken(request, self.request)['employee_id'],

            start_date= request.data.get('start_date',None)
            end_date= request.data.get('end_date',None)

            # Update start_date and end_date only if they are provided
            if start_date is None:
                start_date = datetime.datetime.now().date()

            if end_date is None:
                end_date = datetime.datetime.now().date()

            # Convert strings to datetime objects
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

            # Make them timezone-aware (converts naive datetime to aware datetime)
            start_date = timezone.make_aware(start_date)  # Make the datetime timezone-aware
            end_date = timezone.make_aware(end_date)

            # Validate the date range
            if end_date < start_date:
                raise ValueError("End date cannot be less than start date.")
            
            emp_leave_dates = EmployeeLeaveDates.objects.filter(employee_leave__employee=employee_id, is_active=True)
            
            emp_leave_dates = EmployeeLeaveDates.objects.filter(
            employee_leave__employee=employee_id,
            is_active=True
            ).filter(
                Q(date__gte=start_date) & Q(date__lte=end_date)
            )
            leaves_data=EmployeeLeaveDatesSerializers(emp_leave_dates,many=True).data
            weekend_dates = []
            current_date = start_date
            while current_date <= end_date:
                # Check if the current date is a Saturday (5) or Sunday (6)
                if current_date.weekday() == 5 or current_date.weekday() == 6:
                    weekend_dates.append(current_date.date())
                current_date += datetime.timedelta(days=1)

            status=request.data.get('status',None)
            is_active=request.data.get('is_active',None)
            task_type=request.data.get("task_type",None)
            priority=request.data.get("priority",None)
            assign_to=request.data.get("assign_to",None)

            
            # Prefetch the time logs related to tasks in a single query
            time_log_task_ids = TaskTimeLogs.objects.filter(
                task__project=project_id, 
                task__employee__organization=organization_id,
                employee=employee_id,
                date__range=(start_date, end_date),
                is_active=True
            ).values_list('task_id', flat=True)

            # Get all distinct task IDs from the time logs
            # time_log_task_ids = time_log_query.values_list('task_id', flat=True)

            # Get all assigned tasks for the employee in a single query
            assigned_tasks_query = Tasks.objects.filter(
                project=project_id,
                employee__organization=organization_id,
                assign_to=employee_id,
                created_at__range=(start_date, end_date),
                is_active=True
            ).values_list('id', flat=True)

            # Combine task IDs from both queries, ensuring distinctness
            all_task_ids = set(time_log_task_ids).union(set(assigned_tasks_query))


            # Fetch all distinct tasks and prefetch related time logs
            task_query = Tasks.objects.filter(
                id__in=all_task_ids,
                is_active=True
            )

            
            if status is not None: 
                task_query=task_query.filter(status=status)
                
            if is_active is not None:
                task_query=task_query.filter(is_active=is_active)

            if task_type is not None:
                task_query=task_query.filter(task_type=task_type)

            if priority is not None:
                task_query=task_query.filter(priority=priority)

            if assign_to is not None:
                task_query=task_query.filter(assign_to=assign_to)



            # Serialize the tasks and time logs in a single loop
            task_time_log_data = [
                TaskswithTimeLogsSerializer(
                    task,
                    context={'query': TaskTimeLogs.objects.filter(task=task.id,employee=employee_id,date__range=(start_date,end_date))}
                ).data
                for task in task_query
            ]

            data_list={
                "task_time_log_data":task_time_log_data,
                "leaves_data":leaves_data,
                "weekends_data":weekend_dates
            }

            

            return successMessageWithData("Success", data_list)
        except Exception as e:
            return exception(e)
    

    def get_project_count(self,request,*args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            employee_id = decodeToken(self, self.request)['employee_id']
            # project=request.data.get()

            pk=self.kwargs['project_id']
            query = Projects.objects.filter(id=pk,  organization=organization_id)
            if not query.exists():
                return errorMessage('Project not exists in current organization')
                
            if query.filter(is_active=False).exists():
                return errorMessage('The project is deactivated at this id')
            query_data=custom_query_get_project_task_count(pk,employee_id)
            return successMessageWithData('Success',query_data)

        except Exception as e:
            return exception(e) 
 
        
    
    

class TaskCommentViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TaskComment.objects.all()
    serializer_class = TaskCommentSerializer

    def create(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            user = request.user
            user_id = user.id
            pk = self.kwargs['pk']

            query = Tasks.objects.filter(id=pk, employee__organization=organization_id, is_active=True)
            if not query.exists():
                return errorMessage('Task does not exists')
            obj = query.get()
            request.data._mutable = True

            comment = request.data.get('comment', None)
            if not comment:
                return errorMessage('Comment is a required field')
            date_check=task_comment(obj,user_id,comment)
            if date_check['status'] == 400:
                    return errorMessage(date_check['message'])
        
            attachment_data = request.data.getlist('attachments')
            attachment_serializer_errors=[]
            comment_id=date_check['comment_id']
            for attachment in attachment_data:
                    date_check=task_attachments(obj,request.user.id,attachment,comment_id.id)
                    if date_check['status'] == 400:
                        attachment_serializer_errors.append(date_check['message'])
                        continue
            if attachment_serializer_errors:
                return errorMessageWithData("Task comment added but some attachemnets not added",attachment_serializer_errors)
            
            
            comments = self.queryset.filter(task=obj,is_active=True).order_by('-id')
           

            # Serialize and return the comments
            serializer = self.serializer_class(comments, many=True)
          
            return successMessageWithData('Successfully created', serializer.data)
        except Exception as e: 
            return exception(e)
        
   
    def list(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk'] 
            query =Tasks.objects.filter(id=pk,employee__organization=organization_id, is_active=True)
            if not query.exists():
                return errorMessage('Task does not exist')

            obj = query.first()
            comments = self.queryset.filter(task=obj,is_active=True).order_by('-id')

            # Serialize and return the comments
         
            serializer = self.serializer_class(comments, many=True)
            return successMessageWithData('success', serializer.data)

        except Exception as e:
            return exception(e)
        
    def patch(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            user_id=request.user.id
            pk = self.kwargs['comment_id']
            if not request.data:
                return errorMessage("Request Data is empty")

            query=self.queryset.filter(id=pk,created_by=request.user.id,is_active=True)

            if not query.exists():
                    return errorMessage("comment not exists in current organization")
                
            obj=query.get()

            comment = request.data.get('comment', None)
            if comment is not None:
                date_check=task_comment(obj,user_id,comment)
                if date_check['status'] == 400:
                        return errorMessage(date_check['message'])
            
            serializer=self.serializer_class(obj, data = request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()


            comments = self.queryset.filter(task=obj.task,is_active=True).order_by('-id')

            # Serialize and return the comments
            serializer = self.serializer_class(comments, many=True)
            

            return successfullyUpdated(serializer.data)
            
        except Exception as e:
            return exception(e)
        


        
    def delete(self, request, *args, **kwargs):
        try:
            comment_id = self.kwargs['comment_id']
            user_id=request.user.id

            query = self.queryset.filter(id=comment_id)
            if not query.exists():
                return errorMessage('Comment does not exists')
            elif not query.filter(created_by=user_id):
                return errorMessage('Only the employee who posted the comment can delete it')
            elif not query.filter(is_active=True).exists():
                return errorMessage('Comment is already deactivated at this id')
            
            obj = query.get()
 
            obj.is_active=False
            obj.save()
            TaskAttachments.objects.filter(comment_id=obj.id).update(is_active=False)
            
            comments = self.queryset.filter(task=obj.task,is_active=True).order_by('-id')


            # Serialize and return the comments
            serializer = self.serializer_class(comments, many=True)
            return successMessageWithData('Successfully deactivated', serializer.data)
        except Exception as e:
            return exception(e)
        

class TaskAttachmentsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TaskAttachments.objects.all()
    serializer_class = TaskAttachmentsSerializer

    def create(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            user = request.user
            user_id = user.id
            pk=self.kwargs['pk']
            comment=request.data.get('comment',None)
            query = Tasks.objects.filter(id=pk, employee__organization=organization_id, is_active=True)
            if not query.exists():
                    return errorMessage('Task does not exists')
            obj = query.get()

            if comment:
                query = TaskComment.objects.filter(task=pk,id=comment, task__employee__organization=organization_id, is_active=True)
                if not query.exists():
                        return errorMessage('Comment does not exists')
                
            attachment_data = request.data.getlist('attachments')
            attachment_serializer_errors=[]
            for attachment in attachment_data:
                    date_check=task_attachments(obj,request.user.id,attachment,comment)
                    if date_check['status'] == 400:
                        attachment_serializer_errors.append(date_check['message'])
                        continue
            
            attachments = self.queryset.filter(task=obj,is_active=True).order_by('-id')
            if comment:
                attachments=attachments.filter(comment=comment)
            else:
                attachments=attachments.filter(comment__isnull=True)

            
            # Serialize and return the comments
            serializer = self.serializer_class(attachments, many=True)


            if attachment_serializer_errors:
                return errorMessageWithData("Some attachemnets not added",serializer.data)
          
            return successMessageWithData('Successfully created', serializer.data)
        except Exception as e: 
            return exception(e)
        
   
    def list(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk'] 
            # print(pk)
            query =Tasks.objects.filter(id=pk,employee__organization=organization_id, is_active=True)
            if not query.exists():
                return errorMessage('Task does not exist')
            obj = query.first()
            comment=request.data.get('comment',None)
            if comment:
                query = TaskComment.objects.filter(task=pk,id=comment, task__employee__organization=organization_id, is_active=True)
                if not query.exists():
                        return errorMessage('Comment does not exists')
            attachments = self.queryset.filter(task=obj,is_active=True).order_by('-id')
            if comment:
                attachments=attachments.filter(comment=comment)
            else:
                attachments=attachments.filter(comment__isnull=True)
         
            serializer = self.serializer_class(attachments, many=True)
            return successMessageWithData('success', serializer.data)

        except Exception as e:
            return exception(e)
        
    # def patch(self, request, *args, **kwargs):
    #     try:
    #         token_data = decodeToken(self, self.request)
    #         organization_id = token_data['organization_id']
    #         user_id=request.user.id
    #         pk = self.kwargs['comment_id']
    #         if not request.data:
    #             return errorMessage("Request Data is empty")

    #         query=self.queryset.filter(id=pk,created_by=request.user.id,is_active=True)

    #         if not query.exists():
    #                 return errorMessage("attachment not exists in current organization")
                
    #         obj=query.get()

    #         comment = request.data.get('comment', None)
    #         if comment is not None:
    #             # date_check=task_attachments(obj,user_id,attachment,comment_obj)
    #             if date_check['status'] == 400:
    #                     return errorMessage(date_check['message'])
            
    #         serializer=self.serializer_class(obj, data = request.data, partial=True)
    #         if not serializer.is_valid():
    #             return serializerError(serializer.errors)
    #         serializer.save()


    #         attachments = self.queryset.filter(task=obj.task,is_active=True).order_by('-id')

    #         # Serialize and return the comments
    #         serializer = self.serializer_class(attachments, many=True)
            

    #         return successfullyUpdated(serializer.data)
            
    #     except Exception as e:
    #         return exception(e)
        


    def delete(self, request, *args, **kwargs):
        try:
            attachment_id = self.kwargs['attachment_id']
            user_id=request.user.id

            query = self.queryset.filter(id=attachment_id)
            if not query.exists():
                return errorMessage('Attachment does not exists')
            
            elif not query.filter(created_by=user_id):
                return errorMessage('Only the employee who uploaded the file can delete it')

            elif not query.filter(is_active=True).exists():
                return errorMessage('Attachment is already deactivated at this id')
            
            
            obj = query.get()
 
            obj.is_active=False
            obj.save()
            
            attachments = self.queryset.filter(task=obj.task,is_active=True).order_by('-id')

            # Serialize and return the comments
            serializer = self.serializer_class(attachments, many=True)
            return successMessageWithData('Successfully deleted', serializer.data)
        except Exception as e:
            return exception(e)
        

class TaskPreDataviewset(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]

    def get_project_data(self, request, *args, **kwargs):
        try:
            # Decode the token to get organization ID
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']

            
            # Initialize response structure
            data_response = {
                "default_status": [],
                "project_status": [],
                "task_group":[],
                "default_task_type": [],
                "project_task_type": [],
                "project_groups":[],
                "project_employees": [],
                "employee_project_role":[]
            }

            # Query for default status and type (those not linked to any project)
            check_query_status = TasksStatus.objects.filter(organization=organization_id, is_active=True)
            default_status_query = check_query_status.filter(project__isnull=True)

            check_query_type=TaskTypes.objects.filter(organization=organization_id, is_active=True)
            default_task_type_query = check_query_type.filter(project__isnull=True)
            
            # Serialize default status and task type
            default_status_serializer =TasksStatusSerializer(default_status_query, many=True)
            default_task_type_serializer = TaskTypesSerializer(default_task_type_query, many=True)
            
            # Assign to response
            data_response["default_status"] = default_status_serializer.data
            data_response["default_task_type"] = default_task_type_serializer.data

            # Check if project ID is provided in request data
            project_id = self.kwargs['project_id']
            if project_id is not None:
                # Query for project-specific status and type
                project_status_query = check_query_status.filter(project=project_id)
                project_task_type_query = check_query_type.filter(project=project_id)
                
                # Serialize project-specific status and task type
                project_status_serializer = TasksStatusSerializer(project_status_query, many=True)
                project_task_type_serializer = TaskTypesSerializer(project_task_type_query, many=True)
                
                # Assign to response
                data_response["project_status"] = project_status_serializer.data
                data_response["project_task_type"] = project_task_type_serializer.data
                #Groups data
                Group_data=TaskGroups.objects.filter(organization=organization_id,project=project_id,created_by=request.user.id,is_active=True)
                Group_data =TaskGroupsSerializer(Group_data, many=True)
                data_response['project_groups']=Group_data.data
                # Query for project employees
                projects_employee = EmployeeProjects.objects.filter(project=project_id, employee__organization=organization_id, is_active=True)
                
                project_employees_data = []
                for employee in projects_employee:
                    employee_query = Employees.objects.filter(id=employee.employee.id, is_active=True)
                    employee_serializer = PreEmployeesDataSerializers(employee_query, many=True)
                    project_employees_data.extend(employee_serializer.data)
                
                # Assign to response
                data_response["project_employees"] = project_employees_data

                data_response['employee_project_role']=EmployeeProjectsRolesViewset().project_role(employee_id,organization_id,project_id)
            
            return success(data_response)

        except Exception as e:
            return exception(e)

    def task_logs_data(self, request, *args, **kwargs):
        try:
            # token_data = decodeToken(self, self.request)
            # organization_id = token_data['organization_id']
            pk = self.kwargs['pk'] 
            query =TaskLogs.objects.filter(task=pk,is_active=True).order_by('-id')
           
            # Serialize and return the comments

            serializer = TaskLogsSerializer(query, many=True)
            return success(serializer.data)

        except Exception as e:
            return exception(e)






def task_comment(task,user_id,comment):
    try:
        result = {'status': 400, 'message': '','comment_id':None,'data': None}
        employee_kpis_data = {
            'task': task.id,
            'created_by': user_id,
            'comment':comment,
        }
        # print(employee_kpis_data)
        serializer =TaskCommentSerializer(data=employee_kpis_data)
        if not serializer.is_valid():
            result['message'] = serializer.errors
            return result
        comment_id=serializer.save()
        result['data'] = serializer.data
        result['comment_id']=comment_id
        result['status'] = 200
        return result
    except Exception as e:
        result['message'] = str(e)
        return result



def task_attachments(task,user_id,attachment,comment):
    try:
        result = {'status': 400, 'message': '', 'data': None}
        data = {
            'task': task.id,
            'created_by': user_id,
            'attachment':attachment,
            'comment':comment
        }
        # print(employee_kpis_data)
        serializer =TaskAttachmentsSerializer(data=data)
        if not serializer.is_valid():
            if serializer.errors.get('attachment'):
                result['message']=serializer.errors.get('attachment', [''])[0]
            else:
                result['message']=(serializer.errors)
            return result
        
        serializer.save()
        result['data'] = serializer.data
        result['status'] = 200
        return result
    except Exception as e:
        result['message'] = str(e)
        return result



def task_logs(task,user_id,request_data):
    try:
        result = {'status': 400, 'message': '', 'data': None}
        request_data['created_by']=user_id
        request_data['task']=task.id
        # print(employee_kpis_data)
        serializer =TaskLogsSerializer(data=request_data)
        if not serializer.is_valid():
            result['message'] = serializer.errors
            return result
        serializer.save()
        result['data'] = serializer.data
        result['status'] = 200
        return result
    except Exception as e:
        result['message'] = str(e)
        return result



def custom_query_get_project_task_count(project_id,employee_id):
    with connection.cursor() as cursor:
        cursor.execute("""
WITH task_counts AS (
    SELECT 
        e.id AS employee_id,
        e.name AS employee_name,
        p.id AS project_id,
        p.name AS project_title,
        t.status_id,
        ts.title AS status_title,  -- Include status title
        COUNT(t.id) AS status_count  -- Count of tasks for each status
    FROM 
        taskify_tasks AS t
    JOIN 
        employees_employees AS e ON t.assign_to_id = e.id
    JOIN 
        projects_projects AS p ON t.project_id = p.id 
    JOIN 
        taskify_tasksstatus AS ts ON t.status_id = ts.id  -- Join to get status title
    WHERE 
        t.project_id = %s -- Replace with the project ID you want to filter by
        AND (t.assign_to_id = COALESCE(NULLIF(%s, 0), t.assign_to_id))
        AND t.is_active = True
    GROUP BY 
        e.id, p.id, t.status_id, ts.title
)

SELECT 
    employee_id,
    employee_name,
    project_id,
    project_title,
    CAST(SUM(status_count) AS INT) AS total_tasks,  -- Total tasks for the employee
    JSON_AGG(
        JSON_BUILD_OBJECT(
            'id', status_id,
            'title', status_title,  -- Include status title
            'count', status_count  -- Count of tasks for each status
        )
    ) AS task_status_counts
FROM 
    task_counts
GROUP BY 
    employee_id, employee_name, project_id, project_title;
        """, [project_id,employee_id])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # # Parse the employees_data field into a list of dictionaries
        # for row in rows:
        #     row['task_status_counts'] = parse_employees_data(row['task_status_counts'])

        return rows

    
def parse_employees_data(employees_data):
    # Parse the employees_data string into a list of dictionaries
    return json.loads("[" + employees_data + "]")