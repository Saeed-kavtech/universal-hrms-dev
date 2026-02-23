import json
import time
from django.db import connection
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Q
from departments.models import Departments
from helpers.decode_token import decodeToken
from helpers.custom_permissions import IsAuthenticated, IsEmployeeOnly
from helpers.status_messages import ( 
    exception, errorMessage, serializerError, successMessageWithData,
    success, successMessage, successfullyCreated, successfullyUpdated, errorMessageWithData
)
from employees.models import Employees
from employees.serializers import EmployeePreDataSerializers
from performance_evaluation.models import KPIScaleGroups
from projects.models import Projects
from .models import (
    EPTypes, EPComplexity, EPScaling, EPYearlySegmentation, EPBatch, EmployeesKpis,
    KpisComments, KpisObjectives, KpisStatus,ScaleComplexity,StatusGroup
)
from .kpislogs import kpis_logs
from departments.views import DepartmentsViewset
from performance_configuration.views import ScaleGroupsViewset,ScaleRatingViewset
from employees.views_project_roles import EmployeeProjectsRolesViewset
from performance_evaluation.views import EmployeeKIPScaleGroupsViewset
from performance_configuration.models import ScaleGroups
from .serializers import(
    DepartmentEmployeesKpisDataView, DepartmentEmployeesKpisObjectivesDataView, DepartmentKpisComplexitySerializers, EPTypesSerializers, EPComplexitySerializers, EPScalingSerializers, EPYearlySegmentationSerializers,
    EPBatchSerializers, EmployeesKpisSerializers, KpisCommentsSerializers, KpisLogsSerializers,
    EmployeesPersonalGoalsKpisSerializers, EmployeesOrganizationalGoalsKpisSerializers, KpisObjectivesSerializers,ListEmployeesKpisSerializers, ListKPIScaleGroupsSerializers, NewEmployeesKpisDataView, NewEmployeesKpisSerializers,
    UpdateEmployeesKpisSerializers, EmployeesEvaluationKpisSerializers, KpisStatusSerializers,UniqueEmployeeKpiSerializers,
    UniqueEmployeesListSerializers,SimpleUniqueEmployeesListSerializers,SimpleEmployeeKpiSerializers,SimpleHrListDataSerializers,StatusGroupSerializers,ListStatusGroupSerializers, HrListDataSerializers,KipsFileUploadSerializers,ScaleComplexitySerializers,
    DepartmentKpisPreformanceSerializers,DepartmentKpisObjectivesSerializers
)
import datetime
import pandas as pd

# Routers
class EPTypesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EPTypes.objects.all()
    serializer_class = EPTypesSerializers

    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            queryset = self.queryset.filter(organization=organization_id, is_active=True)
            serializer = self.get_serializer(queryset, many=True)
            serialized_data = serializer.data
            return successMessageWithData('success', serialized_data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            request.data['created_by'] = request.user.id
            request.data['organization'] = organization_id
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return exception(e)       
        
    def pre_data(self, organization_id):
        try:
            queryset = EPTypes.objects.filter(organization=organization_id, is_active=True)
            serializer = EPTypesSerializers(queryset, many=True)
            serialized_data = serializer.data
            return serialized_data
        except Exception as e:
            print(e)
            return None
    
            

class EPComplexityViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EPComplexity.objects.all()
    serializer_class = EPComplexitySerializers

    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            queryset = self.queryset.filter(organization=organization_id, is_active=True)
            serializer = self.get_serializer(queryset, many=True)
            serialized_data = serializer.data

            return successMessageWithData('success', serialized_data)
        except Exception as e:
            return exception(e)  

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            required_fields = ['title', 'level','score']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [title,level,score]')
            
            check_level_query = self.queryset.filter(organization=organization_id,level=request.data['level'],is_active=True)
            
            if check_level_query.exists():
                return errorMessage('level is already exists in current organization')
            
            
            request.data['organization'] = organization_id
            request.data['created_by'] = request.user.id
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return exception(e)  
        
    def pre_data(self, organization_id):
        try:        
            queryset = EPComplexity.objects.filter(organization=organization_id, is_active=True)
            serializer = EPComplexitySerializers(queryset, many=True)
            serialized_data = serializer.data
            return serialized_data
        except Exception as e:
            return None
        
class KpisObjectivesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = KpisObjectives.objects.all()
    serializer_class = KpisObjectivesSerializers

    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            queryset = self.queryset.filter(organization=organization_id, is_active=True)
            serializer = self.get_serializer(queryset, many=True)
            serialized_data = serializer.data

            return successMessageWithData('success', serialized_data)
        except Exception as e:
            return exception(e)  

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            required_fields = ['title']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added the required field: [title]')
            
            check_title_query = self.queryset.filter(organization=organization_id,title=request.data['title'],is_active=True)
            
            if check_title_query.exists():
                return errorMessage('title is already exists in current organization')
            
            
            request.data['organization'] = organization_id
            request.data['created_by'] = request.user.id
            serializer=self.serializer_class(data=request.data)
            
            if not serializer.is_valid():
                errorMessage(serializer.errors)

            serializer.save()

            return success(serializer.data)


        except Exception as e:
            return exception(e)  
        
    def pre_data(self, organization_id):
        try:        
            queryset = KpisObjectives.objects.filter(organization=organization_id, is_active=True)
            serializer = KpisObjectivesSerializers(queryset, many=True)
            serialized_data = serializer.data
            return serialized_data
        except Exception as e:
            return None
    

class ScaleComplexityViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ScaleComplexity.objects.all()
    serializer_class = ScaleComplexitySerializers

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
           

            required_fields = ['title', 'level','score']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [title,level,score]')
            
           

            check_title_query = self.queryset.filter(organization=organization_id,title=request.data['title'],is_active=True)
         
            if check_title_query.exists():
                return errorMessage('title is already exists in current organization')
            
            check_level_query = self.queryset.filter(organization=organization_id,level=request.data['level'],is_active=True)
            
            if check_level_query.exists():
                return errorMessage('level is already exists in current organization')
            
            
            request.data['created_by'] = request.user.id
            request.data['organization'] = organization_id
            
            serializer=self.serializer_class(data = request.data)

            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()

            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)  

    def pre_data(self, organization_id):
        try:        
            queryset = ScaleComplexity.objects.filter(organization=organization_id, is_active=True)
            serializer = ScaleComplexitySerializers(queryset, many=True)
            serialized_data = serializer.data
            return serialized_data
        except Exception as e:
            return None


class EPScalingViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EPScaling.objects.all()
    serializer_class = EPScalingSerializers
    
    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            queryset = self.queryset.filter(organization=organization_id, is_active=True)
            serializer = self.get_serializer(queryset, many=True)
            serialized_data = serializer.data
            return successMessageWithData('success', serialized_data)
        except Exception as e:
            return exception(e)  

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            required_fields = ['title', 'level']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [title,level]')
            
            check_level_query = self.queryset.filter(organization=organization_id,level=request.data['level'],is_active=True)
            
            if check_level_query.exists():
                return errorMessage('level is already exists in current organization')
            
            request.data['organization'] = organization_id
            request.data['created_by'] = request.user.id
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return exception(e)  
        
    def pre_data(self, organization_id):
        try:
            queryset = EPScaling.objects.filter(organization=organization_id, is_active=True)
            serializer = EPScalingSerializers(queryset, many=True)
            serialized_data = serializer.data
            return serialized_data
        except Exception as e:
            return None


class KpisStatusViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = KpisStatus.objects.all()
    serializer_class = KpisStatusSerializers

    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            queryset = self.queryset.filter(organization=organization_id, is_active=True)
            serializer = self.get_serializer(queryset, many=True)
            serialized_data = serializer.data

            return successMessageWithData('success', serialized_data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            # print(organization_id)
           
            required_fields = ['status_key', 'status_title','level','status_group']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [status_key, status_title,level,status_group]')

            level_check=KpisStatus.objects.filter(level=request.data['level'],organization=organization_id,is_active=True)
                
            if level_check.exists():
                    return errorMessage("Level is already exists in current organization")
            
            # print(level_check.values())
            request.data['organization'] = organization_id
            request.data['created_by'] = request.user.id
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return exception(e)
        
    def pre_data(self, organization_id):
        try:
            queryset = self.queryset.filter(organization=organization_id, is_active=True)
            serializer = self.get_serializer(queryset, many=True)
            serialized_data = serializer.data
            return serialized_data
        except Exception as e:
            return exception(e)  



class StatusGroupViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = StatusGroup.objects.all()
    serializer_class = StatusGroupSerializers

    def list(self, request, *args, **kwargs):
        try:
            # print("Tets")
            organization_id = decodeToken(request, self.request)['organization_id']
            queryset = self.queryset.filter(organization=organization_id, is_active=True)
            serializer = self.get_serializer(queryset, many=True)
            serialized_data = serializer.data

            return successMessageWithData('success', serialized_data)
        except Exception as e:
            return exception(e)
        

    def pre_data(self, organization_id):
        try:
            queryset = self.queryset.filter(organization=organization_id, is_active=True)
            # print("Test1")
            # print(queryset.values())
            serializer = ListStatusGroupSerializers(queryset, many=True)
            serialized_data = serializer.data
            return serialized_data
        except Exception as e:
            return None
        

    

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            # print("TEST:",organization_id)
            
            required_fields = ['title','level']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [title,level]')
            
            check_level_query = self.queryset.filter(organization=organization_id,level=request.data['level'],is_active=True)
            # print(check_level_query.values())
            if check_level_query.exists():
                return errorMessage('level is already exists in current organization')
            
            request.data['organization']=organization_id
            request.data['created_by'] =request.user.id
            serializer=StatusGroupSerializers(data=request.data)
            # print(serializer)

            if not serializer.is_valid():
                return serializerError(serializer.errors)
                
            serializer.save()

            return successfullyCreated(serializer.data)

        except Exception as e:
            return exception(e)
        
 


# views
class EPYearlySegmentationViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EPYearlySegmentation.objects.all()
    serializer_class = EPYearlySegmentationSerializers
    
    def get_queryset(self):
        organization_id = decodeToken(self, self.request)['organization_id']
        return self.queryset.filter(organization=organization_id)
    
    def pre_data(self, organization_id):
        try:
            queryset = self.queryset.filter(organization=organization_id, is_active=True)
            # print( queryset)
            serializer = EPYearlySegmentationSerializers(queryset, many=True)
            serialized_data = serializer.data
            # print(serialized_data)
            return serialized_data
        except Exception as e:
            return exception(e)  
        

    def inprogress_pre_data(self, organization_id):
        try:
            # current_year = datetime.datetime.now().year
            # ep_yearly_segmentation__date__year=current_year
            # print(current_year)
            queryset = EPBatch.objects.filter(batch_status="in-progress",ep_yearly_segmentation__status="in-progress",ep_yearly_segmentation__organization=organization_id, is_active=True)
            # print(queryset)
            serializer = EPBatchSerializers(queryset, many=True)
            serialized_data = serializer.data
            return serialized_data
        except Exception as e:
            return None
        
    def completed_pre_data(self, organization_id):
        try:
            current_year = datetime.datetime.now().year
            # print(current_year)
            queryset = EPBatch.objects.filter(batch_status="completed",ep_yearly_segmentation__date__year=current_year,ep_yearly_segmentation__organization=organization_id, is_active=True).order_by('-id')
            # print(queryset)
            serializer = EPBatchSerializers(queryset,many=True)
            # print(serializer.data)
            serialized_data = serializer.data
            return serialized_data
        except Exception as e:
            return None

    def list(self, request, *args, **kwargs):
        try:
            query = self.get_queryset().filter(is_active=True, status='in-progress')
            
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def complete_batch(self, request, *args, **kwargs):
        try:
            # user_id = request.user.id
            pk = self.kwargs['pk']
            current_date = datetime.datetime.today().date()
            current_month = datetime.datetime.today().month
            current_year = datetime.datetime.now().year
            organization_id = decodeToken(self, request)['organization_id']


            pre_query = EPBatch.objects.filter(id=pk,ep_yearly_segmentation__organization=organization_id ,is_active=True)
            if not pre_query.exists():
                return errorMessage("Batch not exists")
            
            obj=pre_query.get()
            ep_yearly_segmentation=obj.ep_yearly_segmentation.id


            query = self.get_queryset().filter(id=ep_yearly_segmentation)
            if query.filter(is_active=False):
                return errorMessage('EPYearlySegmentation is deactivated ')
            if query.filter(is_lock=True):
                return errorMessage('Batch is locked')
            
            if pre_query.filter(batch_status="completed"):
               return errorMessage("Batch is already completed")
            
            if not pre_query.filter(
                (Q(end_date__year__lt=current_year) |
                (Q(end_date__year=current_year) & Q(end_date__lt=current_date)))):

                return errorMessage("Batch completion is allowed from the end date and onwards")


            obj.batch_status="completed"

            obj.save()

            if obj.end_date.month == 12:
                successMessage("All batch of this segmentation has been completed")

            next_batch_month=obj.end_date.month+1

            next_query = EPBatch.objects.filter(start_date__month=next_batch_month,ep_yearly_segmentation__organization=organization_id ,is_active=True)
            if not next_query.exists():
               return errorMessage("Batch not exists")
            # print(next_query)
            next_query=next_query.filter(batch_status="upcoming")
            
            if next_query:
                obj1=next_query.get()
                obj1.batch_status="in-progress"
                obj1.save()

            else:
                return errorMessage("Next Batch is already in-progress or completed")

            return successMessage("Success")
        except Exception as e:
            return exception(e)


    def start_batch(self, request, *args, **kwargs):
        try:
            # user_id = request.user.id
            pk = self.kwargs['pk']
            # print(pk)
            # current_year = datetime.datetime.now().year
            current_date = datetime.datetime.today().date()
            organization_id = decodeToken(self, request)['organization_id']
            # print(organization_id)

            pre_query = EPBatch.objects.filter(
                id=pk,
                ep_yearly_segmentation__organization=organization_id,
                is_active=True
            )
            # print(pre_query)
            if not pre_query.exists():
                return errorMessage("Batch not exists")
            

            obj=pre_query.get()
            
            ep_yearly_segmentation=obj.ep_yearly_segmentation.id

            query = self.get_queryset().filter(id=ep_yearly_segmentation)
            if query.filter(is_active=False):
                return errorMessage('EPYearlySegmentation is deactivated ')
            if not query.filter(is_lock=True):
                return errorMessage('Batch is not locked')
            
            
            if pre_query.filter(batch_status="in-progress"):
                return errorMessage("Batch is already in progress or completed")
            
            

            # batch_start_date=obj.start_date.month
            # batch_end_date=obj.end_date.month
            
            if not (obj.start_date <= current_date <= obj.end_date):
                return errorMessage("Batch must begin within its designated time frame")


            obj.batch_status="in-progress"

            obj.save()

            return successMessage("Success")
        except Exception as e:
            return exception(e)

   
    def complete_batch_only(self, request, *args, **kwargs):
        try:
            # user_id = request.user.id
            pk = self.kwargs['pk']
            current_date = datetime.datetime.today().date()
            # current_month = datetime.datetime.today().month
            current_year = datetime.datetime.now().year
            organization_id = decodeToken(self, request)['organization_id']

            pre_query = EPBatch.objects.filter(id=pk,ep_yearly_segmentation__organization=organization_id )
            if not pre_query.exists():
                return errorMessage("Batch not exists")
            
            obj=pre_query.get()
            
            ep_yearly_segmentation=obj.ep_yearly_segmentation.id
            # print(ep_yearly_segmentation)

            query = self.get_queryset().filter(id=ep_yearly_segmentation)
            if query.filter(is_active=False):
                return errorMessage('EPYearlySegmentation is deactivated ')
            
            if not query.filter(is_lock=True):
                return errorMessage('Batch is not locked')
            
            # print("end_date:", obj.end_date)
            # print('end_date_year',obj.end_date.year)
            # print("current_year:", current_year)
            # print("current_date:", current_date)

            # print(pre_query.values())
            
            if not pre_query.filter(
                (Q(end_date__year__lt=current_year) |
                (Q(end_date__year=current_year) & Q(end_date__lt=current_date)))):

                return errorMessage("Batch completion is allowed from the end date and onwards")
            
            # print()
                            
            if pre_query.filter(batch_status="completed"):
               return errorMessage("Batch is already completed")


            obj.batch_status="completed"

            obj.save()

            if obj.end_date.month == 12:
                successMessage("All batch of this segmentation has been completed successfully")

            return successMessage("Success")
        except Exception as e:
            return exception(e)


    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            request.data['organization'] = organization_id
            user_id = request.user.id
            current_date = datetime.datetime.today().date()
            date = request.data.get('date', current_date)

            request.data['date'] = date

            required_fields = ['duration', 'brainstorming_period', 'brainstorming_period_for_evaluator']
            if not all(field in request.data for field in required_fields):
                return errorMessage(
                    'make sure you have added all the required fields: '
                    '[duration, brainstorming_period, brainstorming_period_for_evaluator]'
                )
                       
            
            duration = request.data['duration']
            request.data['created_by'] = user_id

            query = self.get_queryset().filter(date__year=date.year, is_active=True)
            if query.filter(status="in-progress").exists():
                return errorMessage('This year segment already exists')
            
            # if query.exists():
            #     for obj in query:
            #         obj.is_active = False
            #         obj.save()
                    
            serializer = self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            yearly_segment = serializer.save()

            batches = self.create_update_batches(yearly_segment, duration, current_date, user_id)
            if batches['status'] == 400:
                return errorMessage(batches['message'])

            refreshed_serializer = self.serializer_class(instance=yearly_segment)
            return successfullyCreated(refreshed_serializer.data)
        except Exception as e:
            return exception(e)
        
    def create_update_batches(self, yearly_segment, duration, current_date, user_id):
        try:
        
            result = {'status': 400, 'message': ''}
            number_of_batches = round(12/duration)
            year = yearly_segment.date.year

            batches = EPBatch.objects.filter(ep_yearly_segmentation=yearly_segment.id, ep_yearly_segmentation__date__year=year, is_active=True)
            if batches.exists():
                for batch in batches:
                    batch.is_active = False
                    batch.save()

            batch_data_dict = {
                'ep_yearly_segmentation': yearly_segment.id,
                'title':None,
                'batch_no': None,
                'batch_status': None,
                'start_date': None,
                'end_date': None,    
                'created_by': user_id,   
                'is_active': True,
            }

            for batch_number in range(1, number_of_batches + 1):
                batch_no = str(year) + '_' + str(batch_number)
                end_month = duration * batch_number
                start_month = end_month - duration + 1
                
                
                # Convert month numbers to month names
                start_month_name = datetime.date(1, start_month, 1).strftime('%b')
                end_month_name = datetime.date(1, end_month, 1).strftime('%b')

                if start_month_name==end_month_name:
                    title = start_month_name

                else:
                    title = f"{start_month_name}-{end_month_name}"


                # Create the title
                

                end_day = self.get_end_day(end_month, year)
                
                end_date = datetime.date(year=year, month=end_month, day=end_day) 
                start_date = datetime.date(year=year, month=start_month, day=1) 

                batch_status = None
                if start_date <= current_date >= end_date:
                    batch_status = 'not-used'
                elif start_date <= current_date <= end_date:
                    batch_status = 'in-progress'
                elif current_date <= end_date: 
                    batch_status = 'upcoming'
                
                batch_data_dict['title']=title
                batch_data_dict['batch_no'] = batch_no
                batch_data_dict['batch_status'] = batch_status
                batch_data_dict['start_date'] = start_date
                batch_data_dict['end_date'] = end_date

                batch_serializer = EPBatchSerializers(data=batch_data_dict)
                if not batch_serializer.is_valid():
                    continue
                batch_serializer.save()
                                
            result['status'] = 200
            return result
        except Exception as e:
            result['message'] = str(e)
            return result
        
    def get_end_day(self, end_month, year):
        try:
            if end_month in [1, 3, 5, 7, 8, 10, 12]:
                end_date = 31
            elif end_month in [4, 6, 9, 11]:
                end_date = 30
            else:  # February (handling leap years)
                if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                    end_date = 29
                else:
                    end_date = 28

            return end_date
        except:
            end_date = 28
            return end_date


    def patch(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            current_date = datetime.date.today()
            user_id = request.user.id
            

            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('No EPYearlySegmentation exists at this id')
            if query.filter(is_active=False):
                return errorMessage('EPYearlySegmentation is deactivated at this id')
            if query.filter(is_lock=True):
                return errorMessage('Batch is locked')
            obj = query.get()

            current_duration = obj.duration
            serializer = self.serializer_class(obj, data = request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            yearly_segment = serializer.save()
            new_duration = request.data.get('duration', current_duration)

            if current_duration != new_duration:
                batches = self.create_update_batches(yearly_segment, new_duration, current_date, user_id)

                serializer = self.serializer_class(instance=yearly_segment)
            
            return successMessageWithData('Success', serializer.data)
        except Exception as e:
            return exception(e)
        


    def complete_yearlysegmentation(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            query = self.get_queryset().filter(status='in-progress',is_active=True)

            if not query.exists():
                return errorMessage('No EPYearlySegmentation is currently in progress')
            
            if query.filter(status='completed').exists():
                return errorMessage('EPYearlySegmentation is already completed')
   
            obj = query.get()


            yearly_segment_id = obj.id

            batch_query = EPBatch.objects.filter(ep_yearly_segmentation=yearly_segment_id,is_active=True).order_by('-id').first()
            
            if batch_query:
                if batch_query.batch_status!='completed':
                    return errorMessage("The segmentation process cannot be marked as completed, as the last batch is still not completed")
            

            
            obj.status='completed'
            obj.save()
            return successMessage('Sucessfully completed')
        except Exception as e:
            return exception(e)
        
    

    def unlock_batch(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            current_date = datetime.datetime.today()
            user_id = request.user.id

            query = self.get_queryset().filter(is_active=True)
            if query.filter(is_lock=True, unlock_by__isnull=False):
                return errorMessage('Batch is already unlocked')
            if query.filter(is_lock=False):
                return errorMessage('Batch is not locked yet')
            if not query.filter(is_active=True):
                return errorMessage('EPYearlySegmentation is deactivated at this id')


            # print(query.values())    
            obj = query.get()

            # emp_kpis = EmployeesKpis.objects.filter(
            #     employee__organization=organization_id, 
            #     kpis_status__level = 1,
            #     is_active=True,
            # )
            # if emp_kpis.exists():
            #     return errorMessage('Employees KPIs exists')            

            yearly_segment_id = obj.id
            obj.unlock_by = request.user
            obj.unlocked_date = datetime.date.today()

            batches = EPBatch.objects.filter(ep_yearly_segmentation=yearly_segment_id, is_active=True)
            # print("test")
            # print(batches.values())
            
            for batch in batches:
                # print(batch)
                batch.is_active = False
                batch.save()

            # print(obj) 
            obj.is_active=False
            obj.save()

            return successMessage('Sucessfully Unlock')
        except Exception as e:
            return exception(e)
        
    
    def lock_batch(self, request, *args, **kwargs):
        try:

            query = self.get_queryset().filter(status='in-progress',is_active=True)
            if not query.exists():
                return errorMessage('EPYearlySegmentation is deactivated')
            if query.filter(is_lock=True):
                return errorMessage('Batch is already locked')
            obj = query.get()

            obj.lock_by = request.user
            obj.locked_date = datetime.date.today()
            obj.is_lock = True
            obj.save()
            return successMessage('Sucessfully lock')
        except Exception as e:
            return exception(e)
        

class EmployeesKpisViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EmployeesKpis.objects.all()
    serializer_class = EmployeesKpisSerializers
    

    def get_queryset(self):
        token_data = decodeToken(self, self.request)
        organization_id = token_data['organization_id']
        employee_id = token_data['employee_id']
        
        return self.queryset.filter(employee=employee_id, employee__organization=organization_id)
    
    def pre_data(self, organization_id):
        try:
            queryset = self.queryset.filter(employee__organization=organization_id, is_active=True).order_by('-id')
            serializer = self.get_serializer(queryset, many=True)
            serialized_data = serializer.data
            return successMessageWithData('success', serialized_data)
        except Exception as e:
            return exception(e)  
    
    def list(self, request, *args, **kwargs):
        try:
            query = self.get_queryset().filter(is_active=True,ep_batch__batch_status='in-progress',ep_batch__is_active=True)
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)  
        
    def uploadkpis(self, request, *args, **kwargs):
        try:
            # Read the CSV file
            df = pd.read_csv("C:\\Users\\Kavtech\\Downloads\\Personal goals.csv")
           
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            

            # Remove rows with all NaN values
            df = df.dropna(how='all')

            # Remove columns with all NaN values
            df = df.dropna(axis=1, how='all')
           
            # Fetch data from specific columns
            emp_code_list = df['emp_code'].tolist()
            emp_mmtr_list=df['mmtr'].tolist()
            title_list=df['personal-goals'].tolist()
            evaluator_list=df['evaluator'].tolist()
            # target_dates_list=df['target_date'].tolist()
            target_dates_list=pd.to_datetime(df['target_date'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d').tolist()
            not_found_data=[]
            batch=EPBatch.objects.get(ep_yearly_segmentation__organization=organization_id,batch_status="in-progress")
            ep_batch_id=batch.id
            # get organization in progress batch id
            #

            for i in range (len(df)):
                    emp = Employees.objects.filter(emp_code=emp_code_list[i], organization_id=organization_id,is_active=True).first()
                    
                    if not emp:
                            not_found_data.append([emp_code_list[i],"Employee is not exists"])
                            continue
                            
                    else:
                        emp_id=emp.id
                        title=title_list[i]
                        ep_type=24
                        ep_batch=ep_batch_id
                        ep_complexity=39
                        mmtr=emp_mmtr_list[i]
                        target_dates=target_dates_list[i]
                        evaluator=evaluator_list[i]
                        kpis_status=28
                        created_by=emp.id
                        list_data={
                            'employee':emp_id,
                            'title':title,
                            'ep_type':ep_type,
                            'ep_batch':ep_batch,
                            'ep_complexity':ep_complexity,
                            'mmtr':mmtr,
                            'target_dates':target_dates,
                            'evaluator':evaluator,
                            'kpis_status':kpis_status,
                            'created_by':created_by,
                        }
                        filter_criteria = Q()

                        for field, value in list_data.items():
                            filter_criteria &= Q(**{field: value})
                        records_to_delete = EmployeesKpis.objects.filter(filter_criteria)

                        if records_to_delete.exists():
                             # If there are records that match all criteria, delete them
                             records_to_delete.delete()


                        serializer = KipsFileUploadSerializers(data=list_data)
                        if not serializer.is_valid():
                            return serializerError(serializer.errors)
                            
                        serializer = serializer.save()
                        

            if not_found_data:
                not_found_df = pd.DataFrame(not_found_data, columns=['Emp_code','Message'])
                not_found_df.to_csv('C:\\Users\\Kavtech\\Downloads\\not_found_kpis_employees.csv', index=False)

            # print(df)
            return successMessage('Sucessfully uploaded file data')
        
        except Exception as e:
            return exception(e) 
        
    def create(self, request, *args, **kwargs):
        try:
            # print("Test")
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            user_id = request.user.id

            current_date = datetime.date.today()
            current_year = current_date.year


            required_fields = ['title','description','kpis_objective','ep_type', 'ep_complexity','ep_batch']
            if not all(field in request.data for field in required_fields):
                return errorMessage(
                    'make sure you have added all the required fields: '
                    '[title,description,kpis_objective,ep_type, ep_complexity,ep_batch]'
                )
            
            request.data['created_by'] = user_id
            request.data['employee'] = employee_id
           
            ep_type_id = request.data.get('ep_type')
            ep_complexity_id = request.data.get('ep_complexity')
            ep_batch_id = request.data.get('ep_batch')
            kpis_objectives_id=request.data.get('kpis_objective')



            emp_query = Employees.objects.filter(
                    id=employee_id, 
                    organization=organization_id, 
                    is_active=True
                )
            
            mode=0

            if emp_query.filter(employee_type__isnull=True):
                return errorMessage("Epmployee type is not correctly set by adminstrator")
            else:
                mode=emp_query.first().employee_type.level
        

            request.data['mode_of_kpis']=mode


            evaluator_id = request.data.get('evaluator', None)
            if evaluator_id:
                evaluator = Employees.objects.filter(
                    id=evaluator_id, 
                    organization=organization_id, 
                    is_active=True
                )
                if not evaluator.exists():
                    return errorMessage('Evaluator does not exists at this id')
            
            kpis_status = KpisStatus.objects.filter(level=1, organization=organization_id, is_active=True)
            if not kpis_status.exists():
                return errorMessage('Kpis status not set yet by adminstrator')
            kpis_status = kpis_status.first()
            request.data['kpis_status'] = kpis_status.id

               
            ep_type = EPTypes.objects.filter(id=ep_type_id, organization=organization_id)
            if not ep_type.exists():
                return errorMessage('EP type does not exists')
            elif not ep_type.filter(is_active=True).exists():
                return errorMessage('EP type is deactivated')

            ep_complexity = EPComplexity.objects.filter(id=ep_complexity_id, organization=organization_id)
            if not ep_complexity.exists():
                return errorMessage('EP complexity does not exist')
            elif not ep_complexity.filter(is_active=True).exists():
                return errorMessage('EP complexity is deactivated')
            
            kpis_objective = KpisObjectives.objects.filter(id=kpis_objectives_id, organization=organization_id)
            if not kpis_objective.exists():
                return errorMessage('Kpis objective does not exists')
            elif not kpis_objective.filter(is_active=True).exists():
                return errorMessage('Kpis objective is deactivated')
            

            ep_batch = EPBatch.objects.filter(
                id=ep_batch_id,
                
                ep_yearly_segmentation__organization=organization_id,
                is_active=True,
            )

            if not ep_batch.exists():
                return errorMessage('Employee performance batch is not set yet')
            
            elif not ep_batch.filter(is_active=True).exists():
                return errorMessage('EP batch is deactivated')
            elif not ep_batch.filter(ep_yearly_segmentation__is_lock=True).exists():
                return errorMessage('EP batch is not locked yet')
            
            elif not ep_batch.filter(batch_status="in-progress").exists():
                return errorMessage('EP batch is not in progress')

            ep_batch_obj = ep_batch.get()
            # request.data['ep_batch'] = ep_batch_obj.id

            brainstorming_period = ep_batch_obj.ep_yearly_segmentation.brainstorming_period
            if not brainstorming_period:
                return errorMessage('Brainstorming period is not set by the admin')
            # start_date = ep_batch_obj.start_date
            # brainstorming_duration = self.brainstorming_duration_checks(
            #     brainstorming_period, 
            #     start_date, 
            #     current_date,
            # )

            # if brainstorming_duration['status'] == 400:
            #     return errorMessage(brainstorming_duration['message'])



            
            serializer_data = self.get_serializer_data(ep_type.get())
            if not serializer_data:
                return errorMessage('Ep type title is not correctly set by adminstrator')
            
            
            # if evaluator_id==employee_id:
            #     return errorMessage('Employee cannot set themselves as their own evaluator')
            scale_group = request.data.get('scale_group', None)
            if scale_group is None:
                scale_group_query=ScaleGroups.objects.filter(is_default_group=True,organization=organization_id,is_active=True).last()
                if scale_group_query is None:
                   return errorMessage("Default scale group is not configured. Please select different scale group or get in touch with the administrator") 
                
                scale_group=scale_group_query.id
                request.data['scale_group']=scale_group

            serializer = serializer_data(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            

            employee_kpis = serializer.save()
            kpi_id = employee_kpis.id
          
                
            output=EmployeeKIPScaleGroupsViewset().assign_scale_group(kpi_id,scale_group,user_id)
            if output['status'] == 400:
                        # print("IF")
                        return errorMessage(output['message'])
            
            
            comments = request.data.get('comments', None)
            if comments:
                comments = kpis_comments(employee_kpis, comments, user_id)
                serializer = serializer_data(instance=employee_kpis)
            
            request_type = request.method
            requested_data = request.data
            kpis_logs(self, employee_kpis, requested_data, request_type, user_id)
            
            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)
    

    def create_by_team_lead(self, request, *args, **kwargs):
        try:
            # print("Test")
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            user_id = request.user.id

            current_date = datetime.date.today()
            current_year = current_date.year


            required_fields = ['title','description','kpis_objective', 'ep_type', 'ep_complexity','employee','ep_batch']
            if not all(field in request.data for field in required_fields):
                return errorMessage(
                    'make sure you have added all the required fields: '
                    '[title,description,kpis_objective,ep_type, ep_complexity,employee,ep_batch]'
                )
            
            request.data['created_by'] = user_id
           
            ep_type_id = request.data.get('ep_type')
            ep_complexity_id = request.data.get('ep_complexity')
            ep_batch_id = request.data.get('ep_batch')
            kpis_objectives_id=request.data.get('kpis_objective')
            kpis_employee_id=request.data['employee']

            emp_query = Employees.objects.filter(
                    id=kpis_employee_id, 
                    organization=organization_id, 
                    is_active=True
                )
            if not emp_query.exists():
                    return errorMessage('Employee does not exists in this organization')
            
            
            #     evaluator = Employees.objects.filter(
            #         id=evaluator_id, 
            #         organization=organization_id, 
            #         is_active=True
            #     )
            #     if not evaluator.exists():
            #         return errorMessage('Evaluator does not exists at this id')
            
            mode=0

            if emp_query.filter(employee_type__isnull=True):
                return errorMessage("Epmployee type is not correctly set by adminstrator")

            else:
                mode=emp_query.first().employee_type.level
        
            request.data['mode_of_kpis']=mode
      
            request.data['evaluator']=employee_id
                
            action=request.data.get('action',None)
            if action:
               action = action.lower()

            if action =="submit":
                kpis_status = KpisStatus.objects.filter(level=3, organization=organization_id, is_active=True)
                if not kpis_status.exists():
                    return errorMessage('Kpis status not set yet by adminstrator')
                kpis_status = kpis_status.first()
                request.data['kpis_status'] = kpis_status.id

            else:
                kpis_status = KpisStatus.objects.filter(level=2, organization=organization_id, is_active=True)
                if not kpis_status.exists():
                    return errorMessage('Kpis status  not set yet by adminstrator')
                kpis_status = kpis_status.first()
                request.data['kpis_status'] = kpis_status.id

               
            ep_type = EPTypes.objects.filter(id=ep_type_id, organization=organization_id)
            if not ep_type.exists():
                return errorMessage('EP type does not exists')
            elif not ep_type.filter(is_active=True).exists():
                return errorMessage('EP type is deactivated')

            ep_complexity = EPComplexity.objects.filter(id=ep_complexity_id, organization=organization_id)
            if not ep_complexity.exists():
                return errorMessage('EP complexity does not exist')
            elif not ep_complexity.filter(is_active=True).exists():
                return errorMessage('EP complexity is deactivated')
            # elif not ep_complexity.filter(ep_type=ep_type_id).exists():
            #     return errorMessage('Complexity does not belong to this type')

            kpis_objective = KpisObjectives.objects.filter(id=kpis_objectives_id, organization=organization_id)
            if not kpis_objective.exists():
                return errorMessage('Kpis objective does not exists')
            elif not kpis_objective.filter(is_active=True).exists():
                return errorMessage('Kpis objective is deactivated')

            ep_batch = EPBatch.objects.filter(
                # start_date__lte=current_date, 
                # end_date__gte=current_date, 
                id= ep_batch_id,
                ep_yearly_segmentation__organization=organization_id,
                is_active=True,
            )
            if not ep_batch.exists():
                return errorMessage('Employee performance batch is not set yet')
            elif not ep_batch.filter(is_active=True).exists():
                return errorMessage('EP batch is deactivated')
            elif not ep_batch.filter(ep_yearly_segmentation__is_lock=True).exists():
                return errorMessage('EP batch is not locked yet')
            elif not ep_batch.filter(batch_status="in-progress").exists():
                return errorMessage('EP batch is not in progress')
            ep_batch_obj = ep_batch.get()
            request.data['ep_batch'] = ep_batch_obj.id

            brainstorming_period = ep_batch_obj.ep_yearly_segmentation.brainstorming_period
            if not brainstorming_period:
                return errorMessage('Brainstorming period is not set by the admin')
            # start_date = ep_batch_obj.start_date
            # brainstorming_duration = self.brainstorming_duration_checks(
            #     brainstorming_period, 
            #     start_date, 
            #     current_date,
            # )

            # if brainstorming_duration['status'] == 400:
            #     return errorMessage(brainstorming_duration['message'])



            
            serializer_data = self.get_serializer_data(ep_type.get())
            if not serializer_data:
                return errorMessage('Ep type title is not correctly set by adminstrator')
            
            
            # if employee_id==kpis_employee_id:
            #     return errorMessage('Employee cannot set themselves as their own evaluator')
            scale_group = request.data.get('scale_group', None)
        
            if scale_group is None:
                scale_group_query=ScaleGroups.objects.filter(is_default_group=True,organization=organization_id,is_active=True).last()
                if scale_group_query is None:
                   return errorMessage("Default scale group is not configured. Please select different scale group or get in touch with the administrator") 
                
                scale_group=scale_group_query.id
                request.data['scale_group']=scale_group

            
                
            serializer = serializer_data(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            

            employee_kpis = serializer.save()
            kpi_id = employee_kpis.id
            
                
            output=EmployeeKIPScaleGroupsViewset().assign_scale_group(kpi_id,scale_group,user_id)
            if output['status'] == 400:
                        # print("IF")
                        return errorMessage(output['message'])
            
            
            comments = request.data.get('comments', None)
            if comments:
                comments = kpis_comments(employee_kpis, comments, user_id)
                serializer = serializer_data(instance=employee_kpis)
            
            request_type = request.method
            requested_data = request.data
            kpis_logs(self, employee_kpis, requested_data, request_type, user_id)
            
            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)
    
    def get_serializer_data(self, ep_type):
        try:
            serializer = None
            if ep_type.key == 'personal-goals':
                serializer = EmployeesKpisSerializers
            elif ep_type.key == 'organizational-goals':
                serializer = EmployeesKpisSerializers
            elif ep_type.key == 'kpis':
                serializer = EmployeesKpisSerializers

            return serializer
        except Exception as e:
            print(str(e))
            return serializer

    def brainstorming_duration_checks(self, period, start_date, current_date):
        try:
            result = {'status': 400, 'message': ''}
            number_of_days = (current_date - start_date).days
         
            if number_of_days >= period:
                result['message'] = 'Kpis submission closed'
                return result
            
            result['status'] = 200
            return result

        except Exception as e:
            result['message'] = str(e)
            return result

    def get_approval_by_team_member_list(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            
            kpis_array = list(request.data.get('kpis_array', None))
            if not kpis_array:
                return errorMessage("kpis array is not passed")

            kpis_status = KpisStatus.objects.filter(level=2, organization=organization_id, is_active=True)
            if not kpis_status.exists():
                return errorMessage('Kpis status not set yet by adminstrator')
            kpis_status = kpis_status.first()
            
            does_not_exists = []
            kpis_status_not_set = []
            kpis_levels_issue = []
            not_employee = []
            evaluator_does_not_exists = []
            scale_group_not_exists=[]

            count = 0
            for kpis in kpis_array:
                query = self.get_queryset().filter(id=kpis, employee__organization=organization_id)
                if not query.exists():
                    does_not_exists.append(kpis)
                    continue

                obj = query.get()
                if not obj.kpis_status:
                    kpis_status_not_set.append(kpis)
                    continue

                if not obj.evaluator:
                    evaluator_does_not_exists.append(kpis)
                    continue

                if not obj.scale_group:
                    scale_group_not_exists.append(kpis)
                    continue
                
                if obj.kpis_status.level == 2:
                    kpis_levels_issue.append(kpis)
                    continue
                if obj.kpis_status.level != 1:
                    kpis_levels_issue.append(kpis)
                    continue

                if not obj.employee.id == employee_id:
                    not_employee.append(kpis)

                obj.kpis_status = kpis_status

                ep_batch_obj = obj.ep_batch
                brainstorming_period = ep_batch_obj.ep_yearly_segmentation.brainstorming_period
                if not brainstorming_period:
                    return errorMessage('Brainstorming period is not set by the admin')
                
                # start_date = ep_batch_obj.start_date
                # brainstorming_duration = self.brainstorming_duration_checks(
                #     brainstorming_period, 
                #     start_date, 
                #     datetime.date.today(),
                # )

                # if brainstorming_duration['status'] == 400:
                #     return errorMessage(brainstorming_duration['message'])
                
                obj.save()
                request_type = request.method
                requested_data = {
                    'kpis_status': obj.kpis_status.id
                }
                user_id = request.user.id
                kpis_logs(self, obj, requested_data, request_type, user_id)
                
                count += 1

            data = {
                    'does_not_exists': does_not_exists, 
                    'kpis_status_not_set': kpis_status_not_set,
                    'kpis_levels_issue': kpis_levels_issue,
                    'not_evaluator': not_employee,
                    'evaluator_does_not_exists': evaluator_does_not_exists,
                    'scale_group_not_exists':scale_group_not_exists
                }
            
            if count == len(kpis_array):
                return successMessage('All kpis status is changed successfuly')
            elif count == 0:
                return errorMessageWithData('Failed to change Kpis status', data) 
            elif count > 0:
                return successMessageWithData('Some of the data is processed successfully', data)

            return successMessage('Status changed successfully')

        except Exception as e:
            return exception(e)
    
    def patch(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            user_id = request.user.id
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('kpis does not exists')
            
            if not query.filter(ep_batch__batch_status='in-progress'):
                return errorMessage('No batch is currently in in-progress state')
            obj = query.filter(ep_batch__batch_status='in-progress').get()
        
            if obj.kpis_status:
                if obj.kpis_status.level != 1:
                    return errorMessage('Kpis can only be updated when it is in progress by team member')

            ep_type_id = request.data.get('ep_type', None)
            if ep_type_id:
                ep_type = EPTypes.objects.filter(id=ep_type_id, organization=organization_id)
                if not ep_type.exists():
                    return errorMessage('EP type does not exists')
                elif not ep_type.filter(is_active=True).exists():
                    return errorMessage('EP type is deactivated')

            ep_complexity_id = request.data.get('ep_complexity', None)
            if ep_complexity_id:
                ep_complexity = EPComplexity.objects.filter(id=ep_complexity_id, organization=organization_id)
                if not ep_complexity.exists():
                    return errorMessage('EP complexity does not exist')
                elif not ep_complexity.filter(is_active=True).exists():
                    return errorMessage('EP complexity is deactivated')

            if 'evaluator' in request.data:
                evaluator_id = request.data['evaluator']  

                evaluator = Employees.objects.filter(
                    id=evaluator_id, 
                    organization=organization_id, 
                    is_active=True
                )
                if not evaluator.exists():
                    return errorMessage('Evaluator does not exists at this id')   

                # if evaluator_id == user_id:
                #     return errorMessage('Employee cannot set themselves as their own evaluator') 
   

            brainstorming_period = obj.ep_batch.ep_yearly_segmentation.brainstorming_period
            if not brainstorming_period:
                return errorMessage('Brainstorming period is not set by the admin')
            # start_date = obj.ep_batch.start_date
            # brainstorming_duration = self.brainstorming_duration_checks(
            #     brainstorming_period, 
            #     start_date, 
            #     datetime.date.today()
            # )

            # if brainstorming_duration['status'] == 400:
            #     return errorMessage(brainstorming_duration['message'])
            

            request_type = request.method
            requested_data = request.data
            

            scale_group = request.data.get('scale_group', None)
            if scale_group is not None and scale_group!="":
                query=ScaleGroups.objects.filter(id=scale_group,organization=organization_id,is_active=True)
                if not query.exists():
                    return errorMessage('Scale Group not exixts in this organization')
                output=EmployeeKIPScaleGroupsViewset().update_scale_group(pk,scale_group,user_id,organization_id)
                if output['status'] == 400:
                    return errorMessage(output['message'])

            serializer = UpdateEmployeesKpisSerializers(obj, data = request.data, partial=True)
            if not serializer.is_valid():                  
                return serializerError(serializer.errors)
            employee_kpis = serializer.save()

            kpis_logs(self, employee_kpis, requested_data, request_type, user_id)
            

            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)
        
    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('Does not exists')
            if not query.filter(is_active=True).exists():
                return errorMessage('Kpis is already deactivated at this id')
            obj = query.get()
            if obj.kpis_status:
                if obj.kpis_status.level != 1:
                    return errorMessage('Kpis can only be updated when it is in progress by team member')
            
            obj.is_active=False
            obj.save()

            employee_kpis = obj
            request_type = request.method
            requested_data = {
                'kpis_is_active': False
            }
            user_id = request.user.id
            kpis_logs(self, employee_kpis, requested_data, request_type, user_id)
            
            return successMessage('Kpis are deactivated successfully')
        except Exception as e:
            return exception(e)
        
    def assign_scale_group(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            
            # print(pk)
            scale_group = request.data.get('scale_group', None)
            if scale_group is None or scale_group=="":
                return errorMessage('Scale Group is empty')
            
            kpi_query = self.get_queryset().filter(id=pk,employee__organization=organization_id,is_active=True)
            if not kpi_query.exists():
                return errorMessage('Kpi Does not exists')
            # print(pk)
            obj=kpi_query.get()
            user_id=request.user.id
          
            query=ScaleGroups.objects.filter(id=scale_group,organization=organization_id,is_active=True)
            if not query.exists():
                return errorMessage('Scale Group not exixts in this organization')
                
            output=EmployeeKIPScaleGroupsViewset().update_scale_group(pk,scale_group,user_id,organization_id)
            if output['status'] == 400:
                return errorMessage(output['message'])
            
            scale_group_instance=query.get()

            obj.scale_group=scale_group_instance

            obj.save()

            return successMessage("Success")
            
            
        except Exception as e:
            return exception(e)
    
    def kpi_data(self, request, *args, **kwargs):
        try:
            # print("Test")
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            # employee_id = token_data['employee_id']
        

            required_fields = ['employee_id', 'kpi_id']
            if not all(field in request.data for field in required_fields):
                return errorMessage(
                    'make sure you have added all the required fields: '
                    '[employee_id, kpi_id]'
                )
            kpi_id=request.data.get('kpi_id',None)
            employee_id=request.data.get('employee_id',None)
            # if employee_id is None:
            #     return errorMessage("Employee id is empty")
            
            # if kpi_id is None:
            #     return errorMessage("Kpi id is empty")
            
            emp_query=Employees.objects.filter(id=employee_id,organization=organization_id,is_active=True)
            query= self.queryset.filter(id=kpi_id,employee=employee_id, employee__organization=organization_id,is_active=True)
            
            if not emp_query.exists():
                return errorMessage('Employee not exists in this organization')
            

            if not query.exists():
                return errorMessage('Kpi not exists not exists in this organization')
            
            serializer = ListEmployeesKpisSerializers(query, many=True)
            serialized_data = serializer.data
            return successMessageWithData('success', serialized_data)

        except Exception as e:
            return exception(e)
    
 
class KpisEvaluationViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EmployeesKpis.objects.all()
    serializer_class = EmployeesEvaluationKpisSerializers
    
    def get_queryset(self):
        token_data = decodeToken(self, self.request)
        organization_id = token_data['organization_id']
        employee_id = token_data['employee_id']
        return self.queryset.filter(employee__organization=organization_id)

    def get_kpis_scale_group_data(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            query = KPIScaleGroups.objects.filter(kpi_id=pk,kpi_id__employee__organization=organization_id,is_active=True)
            # print(query.values())
            serializer=ListKPIScaleGroupsSerializers(query, many=True)
            # print(serializer.data)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

        
    def get_kpis_data(self, request, *args, **kwargs):
        try:
            # print("Test")
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            
            employee_id=self.kwargs['pk']
            query= EmployeesKpis.objects.filter(employee=employee_id,kpis_status__level__in=[2],employee__organization=organization_id,is_active=True).order_by('-id')
            
            serializer=ListEmployeesKpisSerializers(query, many=True)
            # print(serializer.data)
            return success(serializer.data)

        except Exception as e:
            return exception(e)
    
 
        
    
    # def get_request_to_hr(self, request,  *args, **kwargs):
    #     try:
    #         token_data = decodeToken(self, self.request)
    #         organization_id = token_data['organization_id']
    #         employee_id = token_data['employee_id']


    #         user = request.user

    #         if not user.is_admin:
    #             return errorMessage('User is not an admin user')
            

            
    #         query = EmployeesKpis.objects.filter(
    #             employee__organization=organization_id, 
    #             evaluator__isnull=False,
    #             ep_batch__batch_status='in-progress',
    #             ep_batch__is_active=True,
    #             kpis_status__level__in=[3, 4,5,6],
    #             is_active=True,
    #         ).order_by('id')
            

    #         if not query.exists():
    #             return successMessageWithData('No Employees Kpis exists',query)
            
    #         unique_evaluator_list = list(set([obj.evaluator.id for obj in query]))
            
    #         ep_types=EPTypes.objects.filter(organization=organization_id,is_active=True)
    #         evaluator = Employees.objects.filter(id__in=unique_evaluator_list)
    #         serializer = HrListDataSerializers(
    #             evaluator, 
    #             context = {'query': query,'ep_types':ep_types},
    #             many=True
    #         )
    #         # print(serializer.data)
            
    #         return success(serializer.data)
    #     except Exception as e:
    #         return exception(e)   
        

    def get_request_to_hr(self, request,  *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']


            user = request.user

            if not user.is_admin:
                return errorMessage('User is not an admin user')
            

            
            query = EmployeesKpis.objects.filter(
                employee__organization=organization_id, 
                evaluator__isnull=False,
                ep_batch__batch_status='in-progress',
                ep_batch__is_active=True,
                kpis_status__level__in=[3, 4,5,6],
                is_active=True,
            ).order_by('id')
            

            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)
            
            unique_employee_list = list(set([obj.employee.id for obj in query]))
        
            employee = Employees.objects.filter(id__in=unique_employee_list)
            serializer = NewEmployeesKpisDataView(
                employee, 
                context = {'query': query},
                many=True
            )
            # print(serializer.data)
            
            return success(serializer.data)
        except Exception as e:
            return exception(e)   
        

    
        

    def get_request_to_hr_data(self, request,  *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = self.kwargs['pk']

            
            user = request.user

            if not user.is_admin:
                return errorMessage('User is not an admin user')
            

            
            query = EmployeesKpis.objects.filter(
                employee=employee_id,
                employee__organization=organization_id, 
                evaluator__isnull=False,
                ep_batch__batch_status='in-progress',
                ep_batch__is_active=True,
                kpis_status__level__in=[3, 4,5,6],
                is_active=True,
            ).order_by('id')
            
            
            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)
            
           
            serializer=ListEmployeesKpisSerializers(query,many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)   
        


    def recheck_request_to_hr(self, request,  *args, **kwargs):
      try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            request_type = request.method
            requested_data = request.data
            
            user = request.user

            if not user.is_admin:
                return errorMessage('User is not an admin user')
            
            query = self.get_queryset().filter(id=pk,kpis_status__level=6,is_active=True)
            if not query.exists():
                return errorMessage('kpis does not exists')
            
            obj=query.get()


            if obj.kpis_status.level == 7:
                return successMessage("Success")
            
            kpis_status = KpisStatus.objects.filter(level=7, organization=organization_id, is_active=True)
            if not kpis_status.exists():
                return errorMessage('Kpis levels are not set yet by adminstrator')
            kpis_status = kpis_status.first()

          

            obj.kpis_status=kpis_status

            obj.save()


            requested_data = {
            'kpis_status': obj.kpis_status.id
            }

            # print(requested_data)

            kpis_logs(self, obj, requested_data, request_type,request.user.id)

            return successMessage("Success")

      except Exception as e:
          return exception(e)



    def get_pervious_batch_hr_kpis(self, request,  *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            

            required_fields = ['ep_yearly_segmentation','ep_batch']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData(
                    'make sure you have added all the required fields','ep_yearly_segmentation,ep_batch'
                )
            

           
            employee_id=request.data.get('employee',None)
            ep_batch_id=request.data['ep_batch']
            ep_yearly_segmentation_id=request.data['ep_yearly_segmentation']


            evaluator_id=request.data.get('evaluator',None)
            department_id=request.data.get('department',None)

            if evaluator_id is not None:

                evaluator = Employees.objects.filter(
                        id=evaluator_id, 
                        organization=organization_id, 
                        is_active=True
                    )
                
                if not evaluator.exists():
                        return errorMessage('Evaluator does not exists at this id')
                
            
                
            if employee_id is not None:

                employee = Employees.objects.filter(
                        id=employee_id, 
                        organization=organization_id, 
                        is_active=True
                    )
                    

                if not employee.exists():
                        return errorMessage('Employee does not exists at this id')

            if department_id is not None:   
                departments_query=Departments.objects.filter(id=department_id,grouphead__organization=organization_id,is_active=True)
                if not departments_query.exists():
                    return errorMessage("Department not exists")
                
            


            ep_yearly_segmentation=EPYearlySegmentation.objects.filter(id=ep_yearly_segmentation_id,organization=organization_id)
            
            if not ep_yearly_segmentation.exists():
                return errorMessage('Yearly segmentation not exists')
            
            elif not ep_yearly_segmentation.filter(is_active=True).exists():
                return errorMessage('Yearly segmentation is deactivated')

            ep_batch = EPBatch.objects.filter(
                id=ep_batch_id,
                ep_yearly_segmentation=ep_yearly_segmentation_id,
                ep_yearly_segmentation__organization=organization_id,
            )

            if not ep_batch.exists():
                return errorMessage('Employee performance batch is not set yet')
            
            elif not ep_batch.filter(is_active=True).exists():
                return errorMessage('EP batch is deactivated')
            elif not ep_batch.filter(ep_yearly_segmentation__is_lock=True).exists():
                return errorMessage('EP batch is not locked yet')
            

            query = EmployeesKpis.objects.filter(
                employee__organization=organization_id, 
                ep_batch__ep_yearly_segmentation=ep_yearly_segmentation_id,
                ep_batch=ep_batch_id,
                ep_batch__is_active=True,
                is_active=True,
            ).order_by('id')


            if employee_id is not None:
                query=query.filter(employee=employee_id)

            if evaluator_id is not None:
                query=query.filter(evaluator=evaluator_id)

            if department_id is not None:
                query=query.filter(employee__department=department_id)

            
            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)
            unique_evaluator_list = list(set([obj.evaluator.id for obj in query if obj.evaluator]))
            ep_types=EPTypes.objects.filter(organization=organization_id,is_active=True)
            evaluator = Employees.objects.filter(id__in=unique_evaluator_list)
            serializer = SimpleHrListDataSerializers(
                evaluator, 
                context = {'query': query,'ep_types':ep_types},
                many=True
            )
            return success(serializer.data)
        except Exception as e:
            return exception(e)  

    def get_recheck_request_to_hr(self, request,  *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            query = EmployeesKpis.objects.filter(
                employee__organization=organization_id, 
                evaluator__isnull=False,
                ep_batch__is_active=True,
                kpis_status__level__in=[7,8,9,10],
                is_active=True,
            ).order_by('id') 

            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)
            
            unique_employee_list = list(set([obj.employee.id for obj in query]))
        
            employee = Employees.objects.filter(id__in=unique_employee_list)
            serializer = NewEmployeesKpisDataView(
                employee, 
                context = {'query': query},
                many=True
            )
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def get_recheck_request_to_hr_data(self, request,  *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = self.kwargs['pk']
            query = EmployeesKpis.objects.filter(
                employee=employee_id,
                employee__organization=organization_id, 
                evaluator__isnull=False,
                ep_batch__is_active=True,
                kpis_status__level__in=[7,8,9,10],
                is_active=True,
            ).order_by('id')
            
            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)
            
           
            serializer = ListEmployeesKpisSerializers(
                query, 
                many=True
            )

            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def get_cancle_request_to_hr(self, request,  *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            query = EmployeesKpis.objects.filter(
                employee__organization=organization_id, 
                evaluator__isnull=False,
                ep_batch__is_active=True,
                kpis_status__level__in=[11,12],
                is_active=True,
            ).order_by('id')

            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)
            unique_employee_list = list(set([obj.employee.id for obj in query]))
        
            employee = Employees.objects.filter(id__in=unique_employee_list)
            serializer = NewEmployeesKpisDataView(
                employee, 
                context = {'query': query},
                many=True
            )
            return success(serializer.data)
        except Exception as e:
            return exception(e)
   
    def get_cancle_request_to_hr_data(self, request,  *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = self.kwargs['pk']
            query = EmployeesKpis.objects.filter(
                employee=employee_id,
                employee__organization=organization_id, 
                evaluator__isnull=False,
                ep_batch__is_active=True,
                kpis_status__level__in=[11,12],
                is_active=True,
            ).order_by('id')

            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)

            serializer = ListEmployeesKpisSerializers(
                query, 
                many=True
            )
            return success(serializer.data)
        except Exception as e:
            return exception(e)
   

   
    def get_approval_by_hr_list(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            user = request.user
            if not user.is_admin:
                return errorMessage('User is not an admin user')
            
            if 'kpis_array' not in request.data:
                return errorMessage('kpis_array does not exists')

            kpis_array = list(request.data.get('kpis_array'))

            kpis_status = KpisStatus.objects.filter(level=4, organization=organization_id, is_active=True)
            if not kpis_status.exists():
                return errorMessage('Kpis levels are not set yet by adminstrator')
            kpis_status = kpis_status.first()
            
            does_not_exists = []
            kpis_status_not_set = []
            kpis_levels_issue = []
            count = 0
            for kpis in kpis_array:
                query = self.get_queryset().filter(id=kpis, employee__organization=organization_id)
                if not query.exists():
                    does_not_exists.append(kpis)
                    continue

                obj = query.get()
                if not obj.kpis_status:
                    kpis_status_not_set.append(kpis)
                    continue

                if obj.kpis_status.level == 4:
                    kpis_levels_issue.append(kpis)
                    continue
                if obj.kpis_status.level != 3:
                    kpis_levels_issue.append(kpis)
                    continue
                    
                obj.kpis_status = kpis_status
                obj.save()

                employee_kpis = obj
                request_type = request.method

                requested_data = {
                    'kpis_status': obj.kpis_status.id
                }
                user_id = request.user.id

                kpis_logs(self, employee_kpis, requested_data, request_type, user_id)

                count += 1

            data = {
                    'does_not_exists': does_not_exists, 
                    'kpis_status_not_set': kpis_status_not_set,
                    'kpis_levels_issue': kpis_levels_issue,
                }
            
            if count == len(kpis_array):
                return successMessage('All kpis status is changed successfuly')
            elif count == 0:
                return errorMessageWithData('Failed to change Kpis status', data) 
            elif count > 0:
                return successMessageWithData('Some of the data is processed successfully', data)

            return successMessage('Status changed successfully')

        except Exception as e:
            return exception(e)

    def get_recheck_approval_by_hr_list(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            user = request.user
            if not user.is_admin:
                return errorMessage('User is not an admin user')
            
            if 'kpis_array' not in request.data:
                return errorMessage('kpis_array does not exists')

            kpis_array = list(request.data.get('kpis_array'))

            kpis_status = KpisStatus.objects.filter(level=10, organization=organization_id, is_active=True)
            if not kpis_status.exists():
                return errorMessage('Kpis levels are not set yet by adminstrator')
            kpis_status = kpis_status.first()
            
            does_not_exists = []
            kpis_status_not_set = []
            kpis_levels_issue = []
            count = 0
            for kpis in kpis_array:
                query = self.get_queryset().filter(id=kpis, employee__organization=organization_id,is_active=True)
                if not query.exists():
                    does_not_exists.append(kpis)
                    continue

                obj = query.get()
                if not obj.kpis_status:
                    kpis_status_not_set.append(kpis)
                    continue

                if obj.kpis_status.level == 10:
                    kpis_levels_issue.append(kpis)
                    continue
                
                if obj.kpis_status.level != 9:
                    kpis_levels_issue.append(kpis)
                    continue
                    
                obj.kpis_status = kpis_status
                obj.save()

                employee_kpis = obj
                request_type = request.method

                requested_data = {
                'kpis_status': obj.kpis_status.id
                }

                user_id = request.user.id
                kpis_logs(self, employee_kpis, requested_data, request_type, user_id)

                count += 1

            data = {
                    'does_not_exists': does_not_exists, 
                    'kpis_status_not_set': kpis_status_not_set,
                    'kpis_levels_issue': kpis_levels_issue,
                }
            
            if count == len(kpis_array):
                return successMessage('All kpis status is changed successfuly')
            elif count == 0:
                return errorMessageWithData('Failed to change Kpis status', data) 
            elif count > 0:
                return successMessageWithData('Some of the data is processed successfully', data)

            return successMessage('Status changed successfully')

        except Exception as e:
            return exception(e)
    
    def get_cancle_approval_by_hr_list(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            user = request.user
            if not user.is_admin:
                return errorMessage('User is not an admin user')
            
            if 'kpis_array' not in request.data:
                return errorMessage('kpis_array does not exists')

            kpis_array = list(request.data.get('kpis_array'))

            kpis_status = KpisStatus.objects.filter(level=12, organization=organization_id, is_active=True)
            if not kpis_status.exists():
                return errorMessage('Kpis levels are not set yet by adminstrator')
            kpis_status = kpis_status.first()
            
            does_not_exists = []
            kpis_status_not_set = []
            kpis_levels_issue = []
            count = 0
            for kpis in kpis_array:
                query = self.get_queryset().filter(id=kpis, employee__organization=organization_id,is_active=True)
                if not query.exists():
                    does_not_exists.append(kpis)
                    continue

                obj = query.get()
                if not obj.kpis_status:
                    kpis_status_not_set.append(kpis)
                    continue

                if obj.kpis_status.level == 12:
                    kpis_levels_issue.append(kpis)
                    continue
                
                if obj.kpis_status.level != 11:
                    kpis_levels_issue.append(kpis)
                    continue
                    
                obj.kpis_status = kpis_status
                obj.save()

                employee_kpis = obj
                request_type = request.method
                requested_data = {
                'kpis_status': obj.kpis_status.id
                }
                user_id = request.user.id
                kpis_logs(self, employee_kpis, requested_data, request_type, user_id)

                count += 1

            data = {
                    'does_not_exists': does_not_exists, 
                    'kpis_status_not_set': kpis_status_not_set,
                    'kpis_levels_issue': kpis_levels_issue,
                }
            
            if count == len(kpis_array):
                return successMessage('All kpis status is changed successfuly')
            elif count == 0:
                return errorMessageWithData('Failed to change Kpis status', data) 
            elif count > 0:
                return successMessageWithData('Some of the data is processed successfully', data)

            return successMessage('Status changed successfully')

        except Exception as e:
            return exception(e)
    
        
    def get_request_to_employee(self, request,  *args, **kwargs):
        try:
            # emp_id = request.user.id
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            # print(pk)
            query = EmployeesKpis.objects.filter(
                employee =employee_id ,
                employee__organization=organization_id, 
                ep_batch__batch_status='in-progress',
                ep_batch__is_active=True,
                is_active=True
            ).order_by('id')

            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)
            
            emp = Employees.objects.get(id=employee_id)

            ep_types=EPTypes.objects.filter(organization=organization_id,is_active=True)
            
            serializer = UniqueEmployeeKpiSerializers(
                emp,
                context = { 'query': query,'ep_types':ep_types},
            )
            return success(serializer.data)
        except Exception as e:
            return exception(e)   
        


    def get_pervious_batch_employee_kpis(self,request,*args, **kwargs):
        try:
            # emp_id = request.user.id
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            # print(pk)

            required_fields = ['ep_yearly_segmentation','ep_batch']
            if not all(field in request.data for field in required_fields):
                return errorMessage(
                    'make sure you have added all the required fields: '
                )
            

            
            ep_batch_id=request.data['ep_batch']
            ep_yearly_segmentation_id=request.data['ep_yearly_segmentation']



            ep_yearly_segmentation=EPYearlySegmentation.objects.filter(id=ep_yearly_segmentation_id,organization=organization_id)
            
            if not ep_yearly_segmentation.exists():
                return errorMessage('Yearly segmentation not exists')
            
            elif not ep_yearly_segmentation.filter(is_active=True).exists():
                return errorMessage('Yearly segmentation is deactivated')


            ep_batch = EPBatch.objects.filter(
                id=ep_batch_id,
                 ep_yearly_segmentation=ep_yearly_segmentation_id,
                ep_yearly_segmentation__organization=organization_id,
            )
            # print(ep_batch.values())
            if not ep_batch.exists():
                return errorMessage('Employee performance batch is not set yet')
            
            elif not ep_batch.filter(is_active=True).exists():
                return errorMessage('EP batch is deactivated')
            elif not ep_batch.filter(ep_yearly_segmentation__is_lock=True).exists():
                return errorMessage('EP batch is not locked yet')
            
        
            query = EmployeesKpis.objects.filter(
                employee =employee_id,
                employee__organization=organization_id, 
                ep_batch=ep_batch_id,
                ep_batch__ep_yearly_segmentation=ep_yearly_segmentation_id,
                ep_batch__is_active=True,
                is_active=True
            ).order_by('id')

            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)
            
            emp = Employees.objects.get(id=employee_id)

            ep_types=EPTypes.objects.filter(organization=organization_id,is_active=True)
            
            serializer = SimpleEmployeeKpiSerializers(
                emp,
                context = { 'query': query,'ep_types':ep_types},
            )
            return success(serializer.data)
        except Exception as e:
            return exception(e)   
        


    def get_pervious_batch_team_lead_kpis(self,request,*args, **kwargs):
        try:
            # emp_id = request.user.id
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            evaluator_id = token_data['employee_id']
            # print(pk)

            required_fields = ['employee','ep_yearly_segmentation','ep_batch']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData(
                    'make sure you have added all the required fields: ','ep_batch,ep_yearly_segmentation,employee'
                )
            
            employee_id=request.data['employee']
            ep_batch_id=request.data['ep_batch']
            ep_yearly_segmentation_id=request.data['ep_yearly_segmentation']


            employee = Employees.objects.filter(
                    id=employee_id, 
                    organization=organization_id, 
                    is_active=True
                )
                

            if not employee.exists():
                    return errorMessage('Employee does not exists at this id')
            


            ep_yearly_segmentation=EPYearlySegmentation.objects.filter(id=ep_yearly_segmentation_id,organization=organization_id)
            
            if not ep_yearly_segmentation.exists():
                return errorMessage('Yearly segmentation not exists')
            
            elif not ep_yearly_segmentation.filter(is_active=True).exists():
                return errorMessage('Yearly segmentation is deactivated')
            


            ep_batch = EPBatch.objects.filter(
                id=ep_batch_id,
                ep_yearly_segmentation=ep_yearly_segmentation_id,
                ep_yearly_segmentation__organization=organization_id,
            )

            if not ep_batch.exists():
                return errorMessage('Employee performance batch is not set yet')
            
            elif not ep_batch.filter(is_active=True).exists():
                return errorMessage('EP batch is deactivated')
            elif not ep_batch.filter(ep_yearly_segmentation__is_lock=True).exists():
                return errorMessage('EP batch is not locked yet')
        
            query = EmployeesKpis.objects.filter(
                employee =employee_id,
                employee__organization=organization_id, 
                evaluator=evaluator_id,
                ep_batch=ep_batch_id,
                ep_batch__ep_yearly_segmentation=ep_yearly_segmentation_id,
                ep_batch__is_active=True,
                is_active=True
            ).order_by('id')

            
            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)
            unique_employee_list = list(set([obj.employee.id for obj in query]))
            unique_employee_list.sort()
            # print(unique_employee_list)
            emp = Employees.objects.get(id=employee_id)

            ep_types=EPTypes.objects.filter(organization=organization_id,is_active=True)
            
            serializer = SimpleUniqueEmployeesListSerializers(
                emp, 
                context = {'unique_employee_list': unique_employee_list, 'query': query,'ep_types':ep_types},
            )
            return success(serializer.data)
        except Exception as e:
            return exception(e)   
        

         

            
    
    def get_request_to_teamlead(self, request,  *args, **kwargs):
        try:
            
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']

            query = EmployeesKpis.objects.filter(
                employee__organization=organization_id, 
                evaluator=employee_id,
                ep_batch__batch_status='in-progress',
                ep_batch__is_active=True,
                kpis_status__level__in=[2,3,4,5,6],
                is_active=True
            ).order_by('id')

            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)
            
            # print(query.values())
                        
            unique_employee_list = list(set([obj.employee.id for obj in query]))

        
            employee = Employees.objects.filter(id__in=unique_employee_list)
            
            serializer = NewEmployeesKpisDataView(
                employee, 
                context = {'query': query},
                many=True
            )

            return success(serializer.data)
        except Exception as e:
            return exception(e)   
        

    def get_request_to_teamlead_data(self, request,  *args, **kwargs):
        try:
            
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            evaluator_id = token_data['employee_id']
            employee_id=self.kwargs['pk']
            query = EmployeesKpis.objects.filter(
                employee=employee_id,
                employee__organization=organization_id, 
                evaluator=evaluator_id,
                ep_batch__batch_status='in-progress',
                ep_batch__is_active=True,
                kpis_status__level__in=[2,3,4,5,6],
                is_active=True
            ).order_by('id')

            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)
            
            # print(query.values())
                        
            serializer=ListEmployeesKpisSerializers(query, many=True)
            # print(serializer.data)
            return success(serializer.data)

        except Exception as e:
            return exception(e)   
        

    def get_recheck_request_to_teamlead(self, request,  *args, **kwargs):
        try:
            
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']

            query = EmployeesKpis.objects.filter(
                employee__organization=organization_id, 
                evaluator=employee_id,
                ep_batch__is_active=True,
                kpis_status__level__in=[7,8,9,10],
                is_active=True
            ).order_by('id')

            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)

            unique_employee_list = list(set([obj.employee.id for obj in query]))
        
            employee = Employees.objects.filter(id__in=unique_employee_list)
            
            serializer = NewEmployeesKpisDataView(
                employee, 
                context = {'query': query},
                many=True
            )

            return success(serializer.data)
        except Exception as e:
            return exception(e)   
        

    def get_recheck_request_to_teamlead_data(self, request,  *args, **kwargs):
        try:
            
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            evaluator_id = token_data['employee_id']
            employee_id=self.kwargs['pk']

            query = EmployeesKpis.objects.filter(
                employee=employee_id,
                employee__organization=organization_id, 
                evaluator=evaluator_id,
                ep_batch__is_active=True,
                kpis_status__level__in=[7,8,9,10],
                is_active=True
            ).order_by('id')

            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)

            serializer=ListEmployeesKpisSerializers(query, many=True)
            # print(serializer.data)
            return success(serializer.data)

        except Exception as e:
            return exception(e)   
        
    def get_cancel_request_to_teamlead(self, request,  *args, **kwargs):
        try:
            
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']

            query = EmployeesKpis.objects.filter(
                employee__organization=organization_id, 
                evaluator=employee_id,
                ep_batch__is_active=True,
                kpis_status__level__in=[11,12],
                is_active=True
            ).order_by('id')

            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)
            unique_employee_list = list(set([obj.employee.id for obj in query]))
        
            employee = Employees.objects.filter(id__in=unique_employee_list)
            
            serializer = NewEmployeesKpisDataView(
                employee, 
                context = {'query': query},
                many=True
            )

            return success(serializer.data)
        except Exception as e:
            return exception(e)   
        
   
    def get_cancel_request_to_teamlead_data(self, request,  *args, **kwargs):
        try:
            
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            evaluator_id = token_data['employee_id']
            employee_id=self.kwargs['pk']

            query = EmployeesKpis.objects.filter(
                employee=employee_id,
                employee__organization=organization_id, 
                evaluator=evaluator_id,
                ep_batch__is_active=True,
                kpis_status__level__in=[11,12],
                is_active=True
            ).order_by('id')

            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)
            
            serializer=ListEmployeesKpisSerializers(query, many=True)
            # print(serializer.data)
            return success(serializer.data)

        except Exception as e:
            return exception(e)   
        
   
   
    def get_approval_by_team_lead_list(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            
            if 'kpis_array' not in request.data:
                return errorMessage('kpis_array does not exists')

            kpis_array = list(request.data.get('kpis_array'))
            

            if not kpis_array:
                return errorMessage("kpis array is not passed")

            kpis_status = KpisStatus.objects.filter(level=3, organization=organization_id, is_active=True)
            if not kpis_status.exists():
                return errorMessage('Kpis levels are not set yet by adminstrator')
            kpis_status = kpis_status.first()
            
            does_not_exists = []
            kpis_status_not_set = []
            kpis_levels_issue = []
            not_evaluator = []
            count = 0
            is_duration_check = False
            for kpis in kpis_array:
                query = self.get_queryset().filter(id=kpis, ep_batch__batch_status='in-progress', employee__organization=organization_id)
                if not query.exists():
                    does_not_exists.append(kpis)
                    continue

                obj = query.get()
                if not is_duration_check:
                    evaluator_brainstorming_period = obj.ep_batch.ep_yearly_segmentation.brainstorming_period_for_evaluator
                    if not evaluator_brainstorming_period:
                        return errorMessage('Brainstorming period for evaluator is not set by the admin')
                    # start_date = obj.ep_batch.start_date
                    # evaluator_brainstorming_duration = EmployeesKpisViewset.brainstorming_duration_checks(
                    #     self,
                    #     evaluator_brainstorming_period, 
                    #     start_date, 
                    #     datetime.date.today()
                    # )

                    # if evaluator_brainstorming_duration['status'] == 400:
                    #     return errorMessage(evaluator_brainstorming_duration['message'])
                    # is_duration_check = True


                if not obj.kpis_status:
                    kpis_status_not_set.append(kpis)
                    continue

                if obj.kpis_status.level == 3:
                    kpis_levels_issue.append(kpis)
                    continue
                if obj.kpis_status.level != 2:
                    kpis_levels_issue.append(kpis)
                    continue

                if not obj.evaluator.id == employee_id:
                    not_evaluator.append(kpis)
                    continue

                    
                obj.kpis_status = kpis_status
                obj.save()

                request_type = request.method
                requested_data = {
                    'kpis_status': obj.kpis_status.id
                }
                user_id = request.user.id
                kpis_logs(self, obj, requested_data, request_type, user_id)
                


                count += 1

            data = {
                    'does_not_exists': does_not_exists, 
                    'kpis_status_not_set': kpis_status_not_set,
                    'kpis_levels_issue': kpis_levels_issue,
                    'not_evaluator': not_evaluator
                }
            
            if count == len(kpis_array):
                return successMessage('All kpis status is changed successfuly')
            elif count == 0:
                return errorMessageWithData('Failed to change Kpis status', data) 
            elif count > 0:
                return successMessageWithData('Some of the data is processed successfully', data)

            return successMessage('Status changed successfully')

        except Exception as e:
            return exception(e)
        
    def update_by_team_lead(self, request, *args, **kwargs):
        try:
            
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            user_id = request.user.id
            pk = self.kwargs['pk']

            
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('Kpi does not exists')
            if not query.filter(ep_batch__batch_status='in-progress').exists():
                return errorMessage('Batch is not in in-progress state')
            obj = query.filter(ep_batch__batch_status='in-progress').get()

            if not obj.evaluator:
                return errorMessage('Please set the evaluator first')
            if obj.evaluator.id != employee_id:
                return errorMessage('You are not the evaluator')
            
            ep_type_id = request.data.get('ep_type', None)
            if ep_type_id:
                ep_type = EPTypes.objects.filter(id=ep_type_id, organization=organization_id)
                if not ep_type.exists():
                    return errorMessage('EP type does not exists')
                elif not ep_type.filter(is_active=True).exists():
                    return errorMessage('EP type is deactivated')

            ep_complexity_id = request.data.get('ep_complexity', None)
            if ep_complexity_id:
                ep_complexity = EPComplexity.objects.filter(id=ep_complexity_id, organization=organization_id)
                if not ep_complexity.exists():
                    return errorMessage('EP complexity does not exist')
                elif not ep_complexity.filter(is_active=True).exists():
                    return errorMessage('EP complexity is deactivated')

            yearly_segmentation = obj.ep_batch.ep_yearly_segmentation
            emp_brainstorming_period = yearly_segmentation.brainstorming_period
            evaluator_brainstorming_period = yearly_segmentation.brainstorming_period_for_evaluator 
            evaluator_brainstorming_period += emp_brainstorming_period
            
            if not evaluator_brainstorming_period:
                return errorMessage('Brainstorming period is not set by the admin')
            # start_date = obj.ep_batch.start_date
            # evaluator_brainstorming_duration = EmployeesKpisViewset.brainstorming_duration_checks(
            #     self,
            #     evaluator_brainstorming_period, 
            #     start_date, 
            #     datetime.date.today()
            # )

            # if evaluator_brainstorming_duration['status'] == 400:
            #     return errorMessage(evaluator_brainstorming_duration['message'])
            
            request_type = request.method
            requested_data = request.data
            user_id = request.user.id
            scale_group = request.data.get('scale_group', None)
            if scale_group is not None and scale_group!="":
                query=ScaleGroups.objects.filter(id=scale_group,organization=organization_id,is_active=True)
                if not query.exists():
                    return errorMessage('Scale Group not exixts in this organization')
                
                output=EmployeeKIPScaleGroupsViewset().update_scale_group(pk,scale_group,user_id,organization_id)
                if output['status'] == 400:
                    return errorMessage(output['message'])
            
            serializer = EmployeesEvaluationKpisSerializers(obj, data = request.data, partial=True)
            if not serializer.is_valid():                  
                return serializerError(serializer.errors)
            employee_kpis = serializer.save()
            

            comments = request.data.get('comments', None)
            if comments:
                kpis_comments = kpis_comments(obj, comments, user_id)

         

            kpis_logs(self, employee_kpis, requested_data, request_type, user_id)
            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)
    
    def cancel_request_by_team_lead(self, request,  *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            request_type = request.method

            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('kpis does not exists')
                
            obj=query.get()

            if obj.kpis_status.level ==11:
                return successMessage("Success")
            
            kpis_status = KpisStatus.objects.filter(level=11, organization=organization_id, is_active=True)
            if not kpis_status.exists():
                return errorMessage('Kpis levels are not set yet by adminstrator')
            kpis_status = kpis_status.first()

            obj.kpis_status=kpis_status

            obj.save()


            requested_data = {
            'kpis_status': obj.kpis_status.id
            }

            # print(requested_data)

            kpis_logs(self, obj, requested_data, request_type,request.user.id)

            return successMessage("Success")

        except Exception as e:
          return exception(e)    
  
  

class KpisCommentsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EmployeesKpis.objects.all()
    serializer_class = EmployeesEvaluationKpisSerializers

    def create(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            user = request.user
            user_id = user.id
            pk = self.kwargs['pk']

            query = self.queryset.filter(id=pk, employee__organization=organization_id, is_active=True)
            if not query.exists():
                return errorMessage('Does not exists')
            if not query.filter(ep_batch__batch_status='in-progress').exists():
                return errorMessage('Comments could only be added when batch is in in-progress state')
            obj = query.filter(ep_batch__batch_status='in-progress').get()

            # if not user.is_admin:
            #     user_type = self.check_user_type(request.user, obj)
            #     if user_type['status'] == 400:
            #         return errorMessage(user_type['message'])

            comments = request.data.get('comments', None)
            if not comments:
                return errorMessage('Comment is a required field')
            
            comments_data = kpis_comments(obj, comments, user_id)
            
             # Fetch comments for the KPI
            kpicomments = KpisComments.objects.filter(employee_kpi=obj).order_by('-id')

            # Serialize and return the comments
            serializer = KpisCommentsSerializers(kpicomments, many=True)
            return successMessageWithData('Successfully created', serializer.data)
        
            # return successMessage('Successfully created')
        except Exception as e:
            return exception(e)
    

    
   
    def list(self, request, *args, **kwargs):
        try:
            # print(self.queryset.values())
            token_data = decodeToken(self, self.request)
            # print(token_data)
            organization_id = token_data['organization_id']
            
            
            # employee_id = token_data['employee_id']
            # user = request.user
            # user_id = user.id
            pk = self.kwargs['pk'] 
            query = self.queryset.filter(id=pk, employee__organization=organization_id, is_active=True)
            if not query.exists():
                return errorMessage('KPI does not exist')

            obj = query.first()
            

            # Fetch comments for the KPI
            comments = KpisComments.objects.filter(employee_kpi=obj).order_by('-id')

            # Serialize and return the comments
         
            serializer = KpisCommentsSerializers(comments, many=True)
            return successMessageWithData('success', serializer.data)

        except Exception as e:
            return exception(e)
    # def check_user_type(self, user, obj):
    #     try:
    #         result = {'status': 400, 'message': ''}

    #         yearly_segmentation = obj.ep_batch.ep_yearly_segmentation
    #         brainstorming_period = yearly_segmentation.brainstorming_period
    #         start_date = obj.ep_batch.start_date

    #         if user.id == obj.employee.hrmsuser.id:            
                
    #             brainstorming_duration = EmployeesKpisViewset.brainstorming_duration_checks(
    #                 self,
    #                 brainstorming_period, 
    #                 start_date, 
    #                 datetime.date.today()
    #             )
                
    #             if brainstorming_duration['status'] == 400:
    #                 result['message'] = brainstorming_duration['message']
    #                 return result


    #         elif obj.evaluator:
    #             if obj.evaluator.hrmsuser.id == user.id:
    #                 evaluator_brainstorming_period = yearly_segmentation.brainstorming_period_for_evaluator 

    #                 if not evaluator_brainstorming_period:
    #                     result['message'] = 'Brainstorming period is not set by the admin'
    #                     return result
                    
    #                 evaluator_brainstorming_period += brainstorming_period

    #                 evaluator_brainstorming_duration = EmployeesKpisViewset.brainstorming_duration_checks(
    #                     self,
    #                     evaluator_brainstorming_period, 
    #                     start_date, 
    #                     datetime.date.today()
    #                 )

    #                 if evaluator_brainstorming_duration['status'] == 400:
    #                     result['message'] = evaluator_brainstorming_duration['message']
    #                     return result
    #             else:
    #                 result['message'] = 'This user do not have privilages to add the comments'
    #                 return result
    #         else:
    #             result['message'] = 'This user do not have privilages to add the comments'
    #             return result
            
    #         result['status'] = 200
    #         return result

    #     except Exception as e:
    #         result['status'] = 400
    #         result['message'] = str(e)
    #         return result

def kpis_comments(employee_kpis, comments, user_id):
    try:
        result = {'status': 400, 'message': '', 'data': None}
        employee_kpis_data = {
            'employee_kpi': employee_kpis.id,
            'comments': comments,
            'created_by': user_id,
        }
        # print(employee_kpis_data)
        serializer = KpisCommentsSerializers(data=employee_kpis_data)
        if not serializer.is_valid():
            result['message'] = serializer.errors
            return result
        serializer.save()
        result['data'] = serializer.data
        result['status'] = 200
        return result
    except Exception as e:
        result['message'] = e
        print(e)
        return result
  

class KpisPreDataViewset(viewsets.ModelViewSet):


    permission_classes = [IsAuthenticated]

    def  employee_update_scale_group(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk=self.kwargs['pk']

            required_fields = ['ep_batch','scale_group']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all the required fields','ep_batch,scale_group')
            
            employee=Employees.objects.filter(id=pk,organization=organization_id,is_active=True)

            if not employee.exists():
                return errorMessage("Employee not found")
            
            user_id=request.user.id
            
            scale_group=request.data['scale_group']
            ep_batch=request.data['ep_batch']
            
            # print(employee)
            
            kpis_query=EmployeesKpis.objects.filter(employee=pk,ep_batch=ep_batch,is_active=True)
            

            if not kpis_query.exists():
                return errorMessage("No kpis data found")
            # scale_group = request.data.get('scale_group', None)
            query=ScaleGroups.objects.filter(id=scale_group,organization=organization_id,is_active=True)
            if not query.exists():
                        return errorMessage('Scale Group not exixts in this organization')
            sg_obj=query.get()
            for kpi in kpis_query:
                output=EmployeeKIPScaleGroupsViewset().update_scale_group(kpi.id,scale_group,user_id,organization_id)
                if output['status'] == 400:
                        return errorMessage(output['message'])
                kpi.scale_group=sg_obj
                kpi.save()


            return successMessage("Success")

        except Exception as e:
            return exception(e)

    def  organization_update_scale_group(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            required_fields = ['ep_batch']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all the required fields','ep_batch')
            error_list=[]
            user_id=request.user.id
            employee=Employees.objects.filter(organization=organization_id,is_active=True)
            if not employee.exists():
                return errorMessage("No employee exists")
            
            scale_group_data= request.data.get('scale_group', None)
            if scale_group_data is None:
                scale_group_query=ScaleGroups.objects.filter(is_default_group=True,organization=organization_id,is_active=True).last()
                if scale_group_query is None:
                    return errorMessage("Default scale group is not configured. Please select different scale group or get in touch with the administrator") 
                scale_group_data=scale_group_query

            for emp in employee:
                # print(emp.id)

                # scale_group=request.data['scale_group']
                ep_batch=request.data['ep_batch']
                
                
                
                kpis_query=EmployeesKpis.objects.filter(employee=emp.id,ep_batch=ep_batch,is_active=True)

                if not kpis_query.exists():
                    continue
                
                
                # if not query.exists():
                #             # return errorMessage('Scale Group not exixts in this organization')
                #     continue

                
                for kpi in kpis_query:
                    # print(kpi.scale_group.id)
                   
                    
                    scale_group = scale_group_data
                    # print(scale_group)
                    if scale_group is not None:
                        output=EmployeeKIPScaleGroupsViewset().update_scale_group(kpi.id,scale_group.id,user_id,organization_id)
                        if output['status'] == 400:
                            errors={
                                "employee_id":emp.id,
                                "employee_name":emp.name,
                                "kpi_id":kpi.id,
                                "message":output['message']
                            }
                            error_list.extend(errors)
                            # return errorMessage(output['message'])
                            continue
                        
                        kpi.scale_group=scale_group
                        kpi.save()

            if len(error_list)>0:
                return errorMessageWithData("Error List",error_list)
            return successMessage("Success")

        except Exception as e:
            return exception(e)
        

    def  change_employee_eveluator(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk=self.kwargs['pk']

            required_fields = ['ep_batch','evaluator']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all the required fields','ep_batch,scale_group')
            
            employee=Employees.objects.filter(id=pk,organization=organization_id,is_active=True)
            
            if not employee.exists():
                return errorMessage("Employee not found")
            evaluator=request.data['evaluator']
            evaluator_query=Employees.objects.filter(id=evaluator,organization=organization_id,is_active=True)

            if not evaluator_query.exists():
                return errorMessage("Evaluator not found")

            evaluator_obj=evaluator_query.get()
            
            ep_batch=request.data['ep_batch']
            
            # print(employee)
            
            kpis_query=EmployeesKpis.objects.filter(employee=pk,ep_batch=ep_batch,is_active=True)
            

            if not kpis_query.exists():
                return errorMessage("No kpis data found")

            for kpi in kpis_query:
                kpi.evaluator=evaluator_obj
                kpi.save()


            return successMessage("Success")

        except Exception as e:
            return exception(e)



    def hr_requests_count(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            if not request.user.is_admin:
                return errorMessage('User is not an admin user')
            simple_approval_count= EmployeesKpis.objects.filter(
                employee__organization=organization_id, 
                evaluator__isnull=False,
                ep_batch__batch_status='in-progress',
                ep_batch__is_active=True,
                kpis_status__level__in=[3, 4,5,6],
                is_active=True,
            ).count()

            recheck_approval_count = EmployeesKpis.objects.filter(
                employee__organization=organization_id, 
                evaluator__isnull=False,
                ep_batch__is_active=True,
                kpis_status__level__in=[7,8,9,10],
                is_active=True,
            ).count()


            cancle_approval_count = EmployeesKpis.objects.filter(
                employee__organization=organization_id, 
                evaluator__isnull=False,
                ep_batch__is_active=True,
                kpis_status__level__in=[11,12],
                is_active=True,
            ).count()

            data = {
                
                'simple_approval_count': simple_approval_count,
                'recheck_approval_count':recheck_approval_count,
                'cancle_approval_count':cancle_approval_count
               
            }

            return successMessageWithData('Success',data)
        except Exception as e:
            return exception(e)
        

        


    def kpis_department_based_complexity(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            if not request.user.is_admin:
                return errorMessage('User is not an admin user')
            
          
            
            ep_yearly_segmentation=request.data.get('ep_yearly_segmentation',None)
            ep_batch=request.data.get('ep_batch',None)

            if ep_yearly_segmentation is not None:

                ep_yearly_segmentation_query=EPYearlySegmentation.objects.filter(id=ep_yearly_segmentation,organization=organization_id)
                
                if not ep_yearly_segmentation_query.exists():
                    return errorMessage('Yearly segmentation not exists')
                
                elif not ep_yearly_segmentation_query.filter(is_active=True).exists():
                    return errorMessage('Yearly segmentation is deactivated')
                
            elif ep_yearly_segmentation is None:
                year=datetime.datetime.today().year
                ep_yearly_segmentation_query=EPYearlySegmentation.objects.filter(date__year=year,organization=organization_id,is_active=True)
                if ep_yearly_segmentation_query.exists():
                    ep_yearly_segmentation=ep_yearly_segmentation_query.get()
                    ep_yearly_segmentation=ep_yearly_segmentation.id
                
            if ep_batch is not None:
                ep_batch_query = EPBatch.objects.filter(
                    id=ep_batch,
                    ep_yearly_segmentation=ep_yearly_segmentation,
                    ep_yearly_segmentation__organization=organization_id,
                )

                if not ep_batch_query.exists():
                    return errorMessage('Employee performance batch is not set yet')
                
                elif not ep_batch_query.filter(is_active=True).exists():
                    return errorMessage('EP batch is deactivated')
                elif not ep_batch_query.filter(ep_yearly_segmentation__is_lock=True).exists():
                    return errorMessage('EP batch is not locked yet')

                # print(ep_yearly_segmentation)
            elif ep_batch is None:
                ep_batch_query=EPBatch.objects.filter(ep_yearly_segmentation=ep_yearly_segmentation,batch_status="completed",is_active=True).order_by('-id')
                if ep_batch_query.exists():
                    ep_batch=ep_batch_query.first()
                    ep_batch=ep_batch.id
            # print("test")
            
            data=custom_query(ep_yearly_segmentation,ep_batch,organization_id,)
            

            return successMessageWithData('Success',data)
        except Exception as e:
            return exception(e)
        


    def kpis_segmentation_based_result_all(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id=request.data.get('employee',None)
            if employee_id is None:
                employee_id=0
 
            ep_yearly_segmentation=request.data.get('ep_yearly_segmentation',None)

            if ep_yearly_segmentation is not None:

                ep_yearly_segmentation_query=EPYearlySegmentation.objects.filter(id=ep_yearly_segmentation,organization=organization_id)
                
                if not ep_yearly_segmentation_query.exists():
                    return errorMessage('Yearly segmentation not exists')
                
                elif not ep_yearly_segmentation_query.filter(is_active=True).exists():
                    return errorMessage('Yearly segmentation is deactivated')
                
            elif ep_yearly_segmentation is None:
                year=datetime.datetime.today().year
                ep_yearly_segmentation_query=EPYearlySegmentation.objects.filter(date__year=year,organization=organization_id,is_active=True)
                if ep_yearly_segmentation_query.exists():
                    ep_yearly_segmentation=ep_yearly_segmentation_query.get()
                    ep_yearly_segmentation=ep_yearly_segmentation.id
                
            
            # print("test")
            
            data=custom_query_yearly_segmenetation(ep_yearly_segmentation,organization_id,employee_id)
            

            return successMessageWithData('Success',data)
        except Exception as e:
            return exception(e)
        

    def kpis_project_based_result(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            employee_id = request.data.get('employee',None)

            if employee_id is None:
                employee_id = token_data['employee_id']
 
            ep_yearly_segmentation=request.data.get('ep_yearly_segmentation',None)
            ep_batch=request.data.get('ep_batch',None)

            required_fields = ['project']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all the required fields','project')
            project_id=request.data['project']
            check_project=Projects.objects.filter(id=project_id,is_active=True)

            if not check_project.exists:
                return errorMessage('Project does not exists')

            if ep_yearly_segmentation is not None:

                ep_yearly_segmentation_query=EPYearlySegmentation.objects.filter(id=ep_yearly_segmentation,organization=organization_id)
                
                if not ep_yearly_segmentation_query.exists():
                    return errorMessage('Yearly segmentation not exists')
                
                elif not ep_yearly_segmentation_query.filter(is_active=True).exists():
                    return errorMessage('Yearly segmentation is deactivated')
                
            elif ep_yearly_segmentation is None:
                year=datetime.datetime.today().year
                ep_yearly_segmentation_query=EPYearlySegmentation.objects.filter(date__year=year,organization=organization_id,is_active=True)
                if ep_yearly_segmentation_query.exists():
                    ep_yearly_segmentation=ep_yearly_segmentation_query.get()
                    ep_yearly_segmentation=ep_yearly_segmentation.id

                if ep_batch is not None:
                    ep_batch_query = EPBatch.objects.filter(
                        id=ep_batch,
                        ep_yearly_segmentation=ep_yearly_segmentation,
                        ep_yearly_segmentation__organization=organization_id,
                    )

                    if not ep_batch_query.exists():
                        return errorMessage('Employee performance batch is not set yet')
                    
                    elif not ep_batch_query.filter(is_active=True).exists():
                        return errorMessage('EP batch is deactivated')
                    elif not ep_batch_query.filter(ep_yearly_segmentation__is_lock=True).exists():
                        return errorMessage('EP batch is not locked yet')

                # print(ep_yearly_segmentation)
                elif ep_batch is None:
                    # ep_batch_query=EPBatch.objects.filter(ep_yearly_segmentation=ep_yearly_segmentation,batch_status="completed",is_active=True).order_by('-id')
                    # if ep_batch_query.exists():
                    #  ep_batch=ep_batch_query.first()
                    ep_batch=0
                
            
            data=custom_query_project_based(ep_batch,ep_yearly_segmentation,project_id,employee_id,organization_id)
            

            return successMessageWithData('Success',data)
        except Exception as e:
            return exception(e)
        

    
    def employee_requests_count(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']

            employee_request_count = EmployeesKpis.objects.filter(
                employee =employee_id ,
                employee__organization=organization_id, 
                # evaluator=employee_id,
                ep_batch__batch_status='in-progress',
                ep_batch__is_active=True,
                is_active=True
            ).count()
          

            team_lead_simple_count = EmployeesKpis.objects.filter(
                employee__organization=organization_id, 
                evaluator=employee_id,
                ep_batch__batch_status='in-progress',
                ep_batch__is_active=True,
                kpis_status__level__in=[2,3,4,5,6],
                is_active=True
            ).count()

            team_lead_recheck_count = EmployeesKpis.objects.filter(
                employee__organization=organization_id, 
                evaluator=employee_id,
                ep_batch__is_active=True,
                kpis_status__level__in=[7,8,9,10],
                is_active=True
            ).count()

            team_lead_cancle_count = EmployeesKpis.objects.filter(
                employee__organization=organization_id, 
                evaluator=employee_id,
                ep_batch__is_active=True,
                kpis_status__level__in=[11,12],
                is_active=True
            ).count()

            data={
                'employee_request_count':employee_request_count,
                'team_lead_simple_count':team_lead_simple_count,
                'team_lead_recheck_count':team_lead_recheck_count,
                'team_lead_cancle_count':team_lead_cancle_count

            }
            return successMessageWithData('Success', data)
        except Exception as e:
            return exception(e)

    
    def employee_projects(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = request.data.get('employee',None)
            if employee_id is None:
                employee_id = token_data['employee_id']
            is_active=True
            employees_projects=EmployeeProjectsRolesViewset().pre_data(employee_id,organization_id,is_active)
            return success(employees_projects)
        except Exception as e:
            return exception(e)

    def list(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            is_active=True
            type = EPTypesViewset().pre_data(organization_id)
            complexity = EPComplexityViewset().pre_data(organization_id)
            scaling = EPScalingViewset().pre_data(organization_id)
            # scale_complexity=ScaleComplexityViewset().pre_data(organization_id)
            employees_projects=EmployeeProjectsRolesViewset().pre_data(employee_id,organization_id,is_active)
            ep_batch_in_progress=EPYearlySegmentationViewset().inprogress_pre_data(organization_id)
            # ep_batch_completed=EPYearlySegmentationViewset().completed_pre_data(organization_id)
            yearly_segmentation=EPYearlySegmentationViewset().pre_data(organization_id)
            # print(yearly_segmentation)
            scale_group=ScaleGroupsViewset().pre_data(organization_id)
            scale_rating=ScaleRatingViewset().pre_data(organization_id)
            kpis_group_status=StatusGroupViewset().pre_data(organization_id)
            # print("kpis_group_status:",ep_batch_completed)
            employees = Employees.objects.filter(organization=organization_id, is_active=True)
            employees_serializers = EmployeePreDataSerializers(employees, many=True)
            department=DepartmentsViewset().pre_data(organization_id)
            kpis_objectives=KpisObjectivesViewset().pre_data(organization_id)

            data = {
                'department':department,
                'type': type,
                'complexity': complexity,
                'kpis_objectives':kpis_objectives,
                'scaling': scaling,
                'yearly_segmentation':yearly_segmentation,
                'ep_batch_in_progress':ep_batch_in_progress,
                # 'ep_batch_completed':ep_batch_completed,
                'scale_group':scale_group,
                'scale_rating':scale_rating,
                'kpis_group_status':kpis_group_status,
                'employees_projects':employees_projects,
                'employees': employees_serializers.data,
                
            }

            return successMessageWithData('Success', data)
        except Exception as e:
            return exception(e)


    def kpis_report_data(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            if not request.user.is_admin:
                return errorMessage('User is not an admin user')
            employee_id=request.data.get('employee',None)
            department_id=request.data.get('department',None)
            stauts_level=request.data.get('level',None)

            ep_yearly_segmentation=request.data.get('ep_yearly_segmentation',None)
            ep_batch=request.data.get('ep_batch',None)

            if ep_yearly_segmentation is not None:

                ep_yearly_segmentation_query=EPYearlySegmentation.objects.filter(id=ep_yearly_segmentation,organization=organization_id)
                
                if not ep_yearly_segmentation_query.exists():
                    return errorMessage('Yearly segmentation not exists')
                
                elif not ep_yearly_segmentation_query.filter(is_active=True).exists():
                    return errorMessage('Yearly segmentation is deactivated')
                
            elif ep_yearly_segmentation is None:
                year=datetime.datetime.today().year
                ep_yearly_segmentation_query=EPYearlySegmentation.objects.filter(date__year=year,organization=organization_id,is_active=True)
                if ep_yearly_segmentation_query.exists():
                    ep_yearly_segmentation=ep_yearly_segmentation_query.get()
                    ep_yearly_segmentation=ep_yearly_segmentation.id
                
            if ep_batch is not None:
                ep_batch_query = EPBatch.objects.filter(
                    id=ep_batch,
                    ep_yearly_segmentation=ep_yearly_segmentation,
                    ep_yearly_segmentation__organization=organization_id,
                )

                if not ep_batch_query.exists():
                    return errorMessage('Employee performance batch is not set yet')
                
                elif not ep_batch_query.filter(is_active=True).exists():
                    return errorMessage('EP batch is deactivated')
                elif not ep_batch_query.filter(ep_yearly_segmentation__is_lock=True).exists():
                    return errorMessage('EP batch is not locked yet')

                # print(ep_yearly_segmentation)
            elif ep_batch is None:
                ep_batch_query=EPBatch.objects.filter(ep_yearly_segmentation=ep_yearly_segmentation,batch_status="completed",is_active=True).order_by('-id')
                if ep_batch_query.exists():
                    ep_batch=ep_batch_query.first()
                    ep_batch=ep_batch.id
            
            data=kpis_report_custom_query(organization_id,employee_id,department_id,ep_batch,stauts_level)
            

            return successMessageWithData('Success',data)
        except Exception as e:
            return exception(e)
        
    
    def get_kpis_data(self, request,  *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = self.kwargs['employee_id']

            
            user = request.user

            if not user.is_admin:
                return errorMessage('User is not an admin user')
            
            ep_yearly_segmentation=request.data.get('ep_yearly_segmentation',None)
            ep_batch=request.data.get('ep_batch',None)
            stauts_level=request.data.get('level',None)

            if ep_yearly_segmentation is not None:

                ep_yearly_segmentation_query=EPYearlySegmentation.objects.filter(id=ep_yearly_segmentation,organization=organization_id)
                
                if not ep_yearly_segmentation_query.exists():
                    return errorMessage('Yearly segmentation not exists')
                
                elif not ep_yearly_segmentation_query.filter(is_active=True).exists():
                    return errorMessage('Yearly segmentation is deactivated')
                
            elif ep_yearly_segmentation is None:
                year=datetime.datetime.today().year
                ep_yearly_segmentation_query=EPYearlySegmentation.objects.filter(date__year=year,organization=organization_id,is_active=True)
                if ep_yearly_segmentation_query.exists():
                    ep_yearly_segmentation=ep_yearly_segmentation_query.get()
                    ep_yearly_segmentation=ep_yearly_segmentation.id
                
            if ep_batch is not None:
                ep_batch_query = EPBatch.objects.filter(
                    id=ep_batch,
                    ep_yearly_segmentation=ep_yearly_segmentation,
                    ep_yearly_segmentation__organization=organization_id,
                )

                if not ep_batch_query.exists():
                    return errorMessage('Employee performance batch is not set yet')
                
                elif not ep_batch_query.filter(is_active=True).exists():
                    return errorMessage('EP batch is deactivated')
                elif not ep_batch_query.filter(ep_yearly_segmentation__is_lock=True).exists():
                    return errorMessage('EP batch is not locked yet')

                # print(ep_yearly_segmentation)
            elif ep_batch is None:
                ep_batch_query=EPBatch.objects.filter(ep_yearly_segmentation=ep_yearly_segmentation,batch_status="in-progress",is_active=True).order_by('-id')
                if ep_batch_query.exists():
                    ep_batch=ep_batch_query.first()
                    ep_batch=ep_batch.id

            # print(ep_batch)
            

            
            query = EmployeesKpis.objects.filter(
                employee=employee_id,
                employee__organization=organization_id, 
                evaluator__isnull=False,
                ep_batch=ep_batch,
                is_active=True,
            ).order_by('id')

            if stauts_level:
                query=query.filter(kpis_status__level__in=stauts_level)

            
            
            if not query.exists():
                return successMessageWithData('No Employees Kpis exists',query)
            

            
           
            serializer=ListEmployeesKpisSerializers(query,many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)   
        



    


# def kpis_logs(self, employee_kpis, requested_data, request_type, user_id):
#     try:
#         result = {'status': 400, 'message': '', 'data': None}
#         kpis_data = {
#             'request_type':request_type,
#             'employees_kpi': employee_kpis.id,
#             'created_by': user_id,
#         }
#         serializer = KpisLogsSerializers(data=kpis_data)
#         if not serializer.is_valid():
#             # print(serializer.errors)
#             result['message'] = serializer.errors
#             return result

#         # print(serializer.data)
        
#         kpis_obj = serializer.save()

#         serializer = KpisLogsSerializers(kpis_obj, data=requested_data, partial=True)
#         if not serializer.is_valid():
#             result['message'] = serializer.errors
#             return result
        
#         serializer.save()
#         result['data'] = serializer.data
#         result['status'] = 200
#         return result
#     except Exception as e:
#         print(e)
#         result['data'] = e
#         return result
# def custom_query(organization_id, ep_yearly_segmentation, ep_batch):
#         queryset = EmployeesKpis.objects.raw("""
#             SELECT ek.*
#             FROM EmployeesKpis ek
#             JOIN Employees e ON ek.employee_id = e.id
#             JOIN Departments d ON e.department_id = d.id
#             WHERE 
#                 d.grouphead_organization_id = %s
#                 AND d.is_active = True
#                 AND e.is_active = True
#                 AND ek.evaluator_id IS NOT NULL
#                 AND ek.ep_batch_is_active = True
#                 AND ek.kpis_status_level IN (6, 9)
#                 AND ek.is_active = True
                
#         """, [organization_id])
#         return queryset
        



def custom_query(ep_yearly_segmentation, ep_batch,organization_id):
    # print(ep_yearly_segmentation, ep_batch,organization_id)
    with connection.cursor() as cursor:
        cursor.execute("""
SELECT 
    d.id,
    d.grouphead_id,
    d.title,
    COALESCE(SUM(CAST(emp_data.total_count AS INT)), 0) AS total_count,
    COALESCE(SUM(CAST(emp_data.total_completed_kpis AS INT)), 0) AS Completed_kpis,
    COALESCE(SUM(CAST(emp_data.total_in_completed_kpis AS INT)), 0) AS total_Incompleted_kpis,
    COALESCE(SUM(CAST(emp_data.total_carry_forward_kpis AS INT)), 0) AS Carry_Forward,
    COALESCE(ROUND(AVG(CASE WHEN emp_data.total_result IS NOT NULL THEN emp_data.total_result ELSE 0 END), 2), 0) AS total_result,
    COALESCE(SUM(emp_data.total_high_complexity),0) AS total_high_complexity,
    COALESCE(SUM(emp_data.total_medium_complexity), 0) AS total_medium_complexity,
    COALESCE(SUM(emp_data.total_low_complexity), 0) AS total_low_complexity,
    STRING_AGG(
        DISTINCT JSON_BUILD_OBJECT(
            'emp_id', emp_data.emp_id,
            'name', emp_data.emp_name,
            'projects', emp_data.projects,
			'batch',emp_data.batch_title,
			'desgination',emp_data.desgination,
			'year',emp_data.year,
            'total_result', emp_data.total_result,
            'total_kpis_count', CAST(emp_data.total_count AS INT),
            'Completed_kpis', CAST(emp_data.total_completed_kpis AS INT),
            'Incompleted_kpis', CAST(emp_data.total_in_completed_kpis AS INT),
            'Carry_Forward', CAST(emp_data.total_carry_forward_kpis AS INT)
        )::TEXT, 
        ',' 
    ) AS employees_data

FROM 
    departments_departments AS d
JOIN 
    departments_groupheads AS gd ON d.grouphead_id=gd.id
JOIN 
    organizations_organization AS org ON gd.organization_id=org.id
LEFT JOIN (
    SELECT 
        e.id AS emp_id,
        e.name AS emp_name,
        e.department_id AS dp_id,
--         MAX(kpis_data.comp_level) AS comp_level,
	    COALESCE(SUM(CASE WHEN kpis_data.comp_level=1 THEN 1 ELSE 0 END), 0) AS total_high_complexity,
        COALESCE(SUM(CASE WHEN kpis_data.comp_level=2 THEN 1 ELSE 0 END), 0) AS total_medium_complexity,
        COALESCE(SUM(CASE WHEN kpis_data.comp_level=3 THEN 1 ELSE 0 END), 0) AS total_low_complexity,
        COALESCE(SUM (CASE WHEN kpis_data.kp_id IS NOT NULL AND kpis_data.evaluation_status = 1 THEN 1 ELSE 0 END), 0) AS total_completed_kpis,
        COALESCE(SUM (CASE WHEN kpis_data.kp_id IS NOT NULL AND kpis_data.evaluation_status = 2 THEN 1 ELSE 0 END), 0) AS total_in_completed_kpis,
        COALESCE(SUM(CASE WHEN kpis_data.kp_id IS NOT NULL AND kpis_data.evaluation_status = 3 THEN 1 ELSE 0 END), 0) AS total_carry_forward_kpis,
        COUNT(kpis_data.kp_id) AS total_count,
        COALESCE(ROUND(AVG(kpis_data.result::numeric), 2), 0) AS total_result,
        pd.projects AS projects,
	    kpis_data.batch_title as batch_title,
	    kpis_data.year as year,
	    stf.title as desgination
    FROM 
        employees_employees AS e
	LEFT JOIN 
	(
		select eep.employee_id,
		ARRAY_AGG(DISTINCT pp.name) AS projects
		from
		employees_employeeprojects AS eep
    INNER JOIN  
            projects_projects AS pp ON eep.project_id = pp.id
	  Where eep.is_active = True 
		group by eep.employee_id
	 )as pd on pd.employee_id=e.id
	LEFT JOIN organizations_staffclassification as stf ON e.staff_classification_id=stf.id

    LEFT JOIN (
        SELECT  
            DISTINCT (ek.id) AS kp_id,
            ek.evaluation_status,
            ek.employee_id AS employee_id,
            kc.level AS comp_level,
            ksg.result,
		    kepb.title as batch_title,
		    EXTRACT(YEAR FROM kesg.date) AS Year
        FROM  
            kpis_employeeskpis AS ek
        INNER JOIN  
            kpis_kpisstatus AS ks ON ek.kpis_status_id=ks.id
        INNER JOIN  
            employees_employees AS es ON ek.evaluator_id = es.id
        INNER JOIN  
            kpis_epbatch AS kepb ON ek.ep_batch_id = kepb.id
        INNER JOIN  
            kpis_epyearlysegmentation AS kesg ON kepb.ep_yearly_segmentation_id = kesg.id 
        INNER JOIN  
            performance_evaluation_kpiscalegroups AS ksg ON ksg.kpi_id_id=ek.id
        INNER JOIN  
            kpis_epcomplexity AS kc ON kc.id=ek.ep_complexity_id
        
        WHERE  
            ek.id IS NOT NULL AND
            kepb.is_active=True AND
		    ksg.is_active=True and
 		    kesg.id=%s AND
            kepb.id=%s AND
            ek.is_active=True 
AND
            ks.level>1 and ks.level<11
    ) AS kpis_data ON e.id = kpis_data.employee_id
    WHERE 
        e.is_active=True
    GROUP BY 
        e.id, e.name, e.department_id,kpis_data.batch_title,kpis_data.year,stf.title,pd.projects
    HAVING 
        COALESCE(ROUND(AVG(kpis_data.result::numeric), 2), 0) <> 0
) AS emp_data ON emp_data.dp_id=d.id
WHERE 
    org.id=%s AND d.is_active=True
GROUP BY 
    d.id;
        """, [ep_yearly_segmentation,ep_batch,organization_id])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Parse the employees_data field into a list of dictionaries
        for row in rows:
            row['employees_data'] = parse_employees_data(row['employees_data'])

        return rows



def custom_query_yearly_segmenetation(ep_yearly_segmentation,organization_id,employee_id):
    with connection.cursor() as cursor:
        cursor.execute("""
WITH emp_id_var AS (
    SELECT %s AS emp_id 
),
emp_data AS (
    SELECT DISTINCT
        ek.employee_id AS emp_id,
        kepb.title AS batch_title,
        kepb.batch_status as batch_status,
		ek.ep_batch_id,
		COALESCE(ROUND(Sum(ksg.result::numeric), 2), 0) AS batch_total_result,
        EXTRACT(YEAR FROM kesg.date) AS year,
        COALESCE(SUM(CASE WHEN kc.level = 1 AND ek.evaluation_status = 1 THEN 1 ELSE 0 END), 0) AS total_high_complexity_completed,
        COALESCE(ROUND(SUM(CASE WHEN kc.level = 1 AND ek.evaluation_status = 1 THEN ksg.result::numeric ELSE NULL END), 2), 0) AS total_high_complexity_result,
        COALESCE(SUM(CASE WHEN kc.level = 2 AND ek.evaluation_status = 1 THEN 1 ELSE 0 END), 0) AS total_medium_complexity_completed,
        COALESCE(ROUND(SUM(CASE WHEN kc.level = 2 AND ek.evaluation_status = 1 THEN ksg.result::numeric ELSE NULL END), 2), 0) AS total_medium_complexity_result,
        COALESCE(SUM(CASE WHEN kc.level = 3 AND ek.evaluation_status = 1 THEN 1 ELSE 0 END), 0) AS total_low_complexity_completed,
        COALESCE(ROUND(SUM(CASE WHEN kc.level = 3 AND ek.evaluation_status = 1 THEN ksg.result::numeric ELSE NULL END), 2), 0) AS total_low_complexity_result,
        COALESCE(SUM(CASE WHEN kc.level = 1 AND ek.evaluation_status = 2 THEN 1 ELSE 0 END), 0) AS total_high_complexity_incomplete,
        COALESCE(SUM(CASE WHEN kc.level = 2 AND ek.evaluation_status = 2 THEN 1 ELSE 0 END), 0) AS total_medium_complexity_incomplete,
        COALESCE(SUM(CASE WHEN kc.level = 3 AND ek.evaluation_status = 2 THEN 1 ELSE 0 END), 0) AS total_low_complexity_incomplete,
        COALESCE(SUM(CASE WHEN kc.level = 1 AND ek.evaluation_status = 3 THEN 1 ELSE 0 END), 0) AS total_high_complexity_carry_forward,
        COALESCE(SUM(CASE WHEN kc.level = 2 AND ek.evaluation_status = 3 THEN 1 ELSE 0 END), 0) AS total_medium_complexity_carry_forward,
        COALESCE(SUM(CASE WHEN kc.level = 3 AND ek.evaluation_status = 3 THEN 1 ELSE 0 END), 0) AS total_low_complexity_carry_forward,
        COALESCE(SUM(CASE WHEN ek.evaluation_status = 1 THEN 1 ELSE 0 END), 0) AS total_completed_kpis,
        COALESCE(SUM(CASE WHEN ek.evaluation_status = 2 THEN 1 ELSE 0 END), 0) AS total_incomplete_kpis,
        COALESCE(SUM(CASE WHEN ek.evaluation_status = 3 THEN 1 ELSE 0 END), 0) AS total_carry_forward_kpis,
        COUNT(ek.id) AS total_count,
        COALESCE(ROUND(
            (
                COALESCE(SUM(CASE WHEN kc.level = 1 AND ek.evaluation_status = 1 THEN ksg.result::numeric ELSE 0 END), 0) * 1.0 /
                NULLIF(COALESCE(SUM(CASE WHEN kc.level = 1 AND ek.evaluation_status = 1 THEN 1 ELSE 0 END), 0), 0) +
                COALESCE(SUM(CASE WHEN kc.level = 2 AND ek.evaluation_status = 1 THEN ksg.result::numeric ELSE 0 END), 0) * 1.0 /
                NULLIF(COALESCE(SUM(CASE WHEN kc.level = 2 AND ek.evaluation_status = 1 THEN 1 ELSE 0 END), 0), 0) +
                COALESCE(SUM(CASE WHEN kc.level = 3 AND ek.evaluation_status = 1 THEN ksg.result::numeric ELSE 0 END), 0) * 1.0 /
                NULLIF(COALESCE(SUM(CASE WHEN kc.level = 3 AND ek.evaluation_status = 1 THEN 1 ELSE 0 END), 0), 0)
            ) / 3, 2), 0) AS total_result
    FROM 
        kpis_employeeskpis AS ek
    INNER JOIN 
        kpis_kpisstatus AS ks ON ek.kpis_status_id = ks.id
    INNER JOIN 
        kpis_epbatch AS kepb ON ek.ep_batch_id = kepb.id
    INNER JOIN 
        kpis_epyearlysegmentation AS kesg ON kepb.ep_yearly_segmentation_id = kesg.id 
    INNER JOIN 
        performance_evaluation_kpiscalegroups AS ksg ON ksg.kpi_id_id = ek.id
    INNER JOIN 
        kpis_epcomplexity AS kc ON kc.id = ek.ep_complexity_id
    WHERE 
        ek.is_active = TRUE AND
        kepb.is_active = TRUE AND
        ksg.is_active = TRUE AND
        kesg.id =%s AND
        kepb.batch_status IN ('completed', 'in-progress')  
		GROUP BY 
        ek.employee_id, kepb.title,ek.ep_batch_id,kesg.date, batch_status
)
SELECT 
    e.id AS emp_id,
    e.name AS emp_name,
    stf.title AS designation,
    STRING_AGG(
         Distinct JSON_BUILD_OBJECT(
            'batch', emp_data.batch_title,
            'batch_status', emp_data.batch_status,
            'year', emp_data.year,
            'total_result', batch_total_result,
            'total_kpis_count', emp_data.total_count,
            'completed_kpis', emp_data.total_completed_kpis,
            'total_high_complexity_completed', emp_data.total_high_complexity_completed,
            'total_high_complexity_result', emp_data.total_high_complexity_result,
            'total_medium_complexity_completed', emp_data.total_medium_complexity_completed,
            'total_medium_complexity_result', emp_data.total_medium_complexity_result,
            'total_low_complexity_completed', emp_data.total_low_complexity_completed,
            'total_low_complexity_result', emp_data.total_low_complexity_result,
            'incomplete_kpis', emp_data.total_incomplete_kpis,
            'total_high_complexity_incomplete', emp_data.total_high_complexity_incomplete,
            'total_medium_complexity_incomplete', emp_data.total_medium_complexity_incomplete,
            'total_low_complexity_incomplete', emp_data.total_low_complexity_incomplete,
            'carry_forward_kpis', emp_data.total_carry_forward_kpis,
            'total_high_complexity_carry_forward', emp_data.total_high_complexity_carry_forward,
            'total_medium_complexity_carry_forward', emp_data.total_medium_complexity_carry_forward,
            'total_low_complexity_carry_forward', emp_data.total_low_complexity_carry_forward
        )::TEXT, 
        ',' 
    ) AS batches_data
FROM 
    employees_employees AS e
INNER JOIN 
    emp_data ON e.id = emp_data.emp_id
LEFT JOIN 
    organizations_staffclassification AS stf ON e.staff_classification_id = stf.id
JOIN 
    emp_id_var ON (emp_id_var.emp_id = 0 OR e.id = emp_id_var.emp_id)
WHERE 
    e.is_active = TRUE AND e.organization_id = %s
GROUP BY 
    e.id, e.name, stf.title
ORDER BY 
    e.id;
        """, [employee_id,ep_yearly_segmentation,organization_id])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Parse the employees_data field into a list of dictionaries
        for row in rows:
            row['batches_data'] = parse_employees_data(row['batches_data'])

        return rows


def custom_query_project_based(ep_batch,ep_yearly_segmentation,project_id,employee_id,organization_id):
    with connection.cursor() as cursor:
        cursor.execute("""
 WITH ep_batch_var AS (
    SELECT %s AS ep_batch 
)
SELECT 
    p.id AS project_id,
    p.name AS project_name,
	COALESCE(SUM(CASE WHEN kc.level = 1 AND ek.evaluation_status = 1 THEN 1 ELSE 0 END), 0) AS total_high_complexity_completed,
    COALESCE(ROUND(SUM(CASE WHEN kc.level = 1 AND ek.evaluation_status = 1 THEN ksg.result::numeric ELSE NULL END), 2), 0) AS total_high_complexity_result,
	COALESCE(SUM(CASE WHEN kc.level = 2 AND ek.evaluation_status = 1 THEN 1 ELSE 0 END), 0) AS total_medium_complexity_completed,
    COALESCE(ROUND(SUM(CASE WHEN kc.level = 2 AND ek.evaluation_status = 1 THEN ksg.result::numeric ELSE NULL END), 2), 0) AS total_medium_complexity_result,
	COALESCE(SUM(CASE WHEN kc.level = 3 AND ek.evaluation_status = 1 THEN 1 ELSE 0 END), 0) AS total_low_complexity_completed,
    COALESCE(ROUND(SUM(CASE WHEN kc.level = 3 AND ek.evaluation_status = 1 THEN ksg.result::numeric ELSE NULL END), 2), 0) AS total_low_complexity_result,
	COALESCE(SUM(CASE WHEN kc.level = 1 AND ek.evaluation_status = 2 THEN 1 ELSE 0 END), 0) AS total_high_complexity_incomplete,
    COALESCE(SUM(CASE WHEN kc.level = 2 AND ek.evaluation_status = 2 THEN 1 ELSE 0 END), 0) AS total_medium_complexity_incomplete,
    COALESCE(SUM(CASE WHEN kc.level = 3 AND ek.evaluation_status = 2 THEN 1 ELSE 0 END), 0) AS total_low_complexity_incomplete,
    COALESCE(SUM(CASE WHEN kc.level = 1 AND ek.evaluation_status = 3 THEN 1 ELSE 0 END), 0) AS total_high_complexity_carry_forward,
    COALESCE(SUM(CASE WHEN kc.level = 2 AND ek.evaluation_status = 3 THEN 1 ELSE 0 END), 0) AS total_medium_complexity_carry_forward,
    COALESCE(SUM(CASE WHEN kc.level = 3 AND ek.evaluation_status = 3 THEN 1 ELSE 0 END), 0) AS total_low_complexity_carry_forward,
	COALESCE(SUM(CASE WHEN ks.level IN (11, 12) THEN 1 ELSE 0 END), 0) AS cancle_kpis,
    COALESCE(SUM(CASE WHEN ek.evaluation_status = 1 THEN 1 ELSE 0 END), 0) AS completed_kpis,
    COALESCE(SUM(CASE WHEN ek.evaluation_status = 3 THEN 1 ELSE 0 END), 0) AS carry_forward_kpis,
    COALESCE(SUM(CASE WHEN ek.evaluation_status = 2 THEN 1 ELSE 0 END), 0) AS incomplete_kpis,
    COUNT(ek.id) AS total_kpis_count,
	COALESCE(ROUND(sum(ksg.result::numeric), 2), 0) AS total_resul
FROM 
    kpis_employeeskpis AS ek
LEFT JOIN  
    kpis_kpisstatus AS ks ON ek.kpis_status_id = ks.id
LEFT JOIN  
    kpis_epbatch AS kepb ON ek.ep_batch_id = kepb.id
LEFT JOIN  
    kpis_epyearlysegmentation AS kesg ON kepb.ep_yearly_segmentation_id = kesg.id 
LEFT JOIN  
    performance_evaluation_kpiscalegroups AS ksg ON ksg.kpi_id_id = ek.id
LEFT JOIN  
    kpis_epcomplexity AS kc ON kc.id = ek.ep_complexity_id
LEFT JOIN 
    employees_employeeprojects AS eep ON ek.employee_project_id = eep.id 
LEFT JOIN 
    projects_projects AS p ON p.id = eep.project_id
JOIN 
    ep_batch_var ON (ep_batch_var.ep_batch = 0 OR kepb.id = ep_batch_var.ep_batch)
WHERE  
    ek.is_active = True 
    AND kepb.is_active = True 
    AND ksg.is_active = True 
    AND kesg.id = %s
	and p.id=%s
	and ek.employee_id=%s
    AND p.is_active = True 
    AND p.organization_id = %s
    and kepb.batch_status IN ('completed', 'in-progress')
GROUP BY 
    p.id, p.name;
        """, [ep_batch,ep_yearly_segmentation,project_id,employee_id,organization_id])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows


def kpis_report_custom_query(organization_id,employee_id,department_id,ep_batch,stauts_level):
    with connection.cursor() as cursor:
        cursor.execute("""
        WITH 
            -- Declare your parameters (variables)
            params AS (
                SELECT 
                    %s::int AS organization_id,        -- Example organization ID
                    %s::int AS employee_id,            -- Example employee ID
                    %s::int AS department_id,            -- Example department ID (you can adjust the logic)
                    %s::int AS ep_batch_id,            -- Example batch ID
                    %s:: int AS status_levels  -- Example status levels (default to all levels if empty)
            ),
            
            -- Employee data
            employee_data AS (
                SELECT 
                    e.id AS employee_id,
                    e.name AS employee_name,
                    CASE
                    WHEN e.profile_image IS NOT NULL AND e.profile_image != '' THEN 
                        CONCAT('https://universal-hrms-live.sgp1.cdn.digitaloceanspaces.com/', e.profile_image)
                    ELSE 
                        NULL
                END AS profile_image,
                    ety.id as employee_type_id,
                    ety.title as employee_type_title,
                    COALESCE(d.id, 0) AS department_id,
                    COALESCE(d.title, 'No Department') AS department_title,
                    COALESCE(sc.title, 'No Designation') AS designation_title
                FROM 
                    employees_employees AS e
                LEFT JOIN departments_departments AS d ON e.department_id = d.id
                LEFT JOIN organizations_staffclassification AS sc ON e.staff_classification_id = sc.id
                LEFT JOIN employees_employeetypes AS ety ON e.employee_type_id=ety.id
                WHERE 
                    e.is_active = TRUE 
                    AND e.organization_id = (SELECT organization_id FROM params)
                    AND (e.id = COALESCE(NULLIF((SELECT employee_id FROM params), 0), e.id))
                    AND (d.id = COALESCE((SELECT department_id FROM params), d.id) OR e.department_id IS NULL AND (SELECT department_id FROM params) IS NULL)
            ),
            
            -- KPI status count
            kpi_status_count AS (
                SELECT 
                    ek.employee_id,
                    ks.id AS status_id,
                    ks.status_title,
                    ks.level AS status_level,
                    COUNT(ek.id) AS status_count
                FROM 
                    kpis_employeeskpis AS ek
                LEFT JOIN kpis_kpisstatus AS ks ON ek.kpis_status_id = ks.id
                WHERE 
                    ek.is_active = TRUE 
                    AND ek.ep_batch_id = (SELECT ep_batch_id FROM params)
                    AND (ks.level  = COALESCE(NULLIF((SELECT status_levels FROM params), 0), ks.level))
                    -- AND ks.level = ANY (SELECT status_levels FROM params)  -- Filter by status_levels
                GROUP BY 
                    ek.employee_id, ks.id, ks.status_title, ks.level
            ),
            
            -- KPI data
            kpi_data AS (
                SELECT 
                    ek.employee_id,
                    COUNT(ek.id) AS total_kpis,
                    JSON_AGG(
                        JSON_BUILD_OBJECT(
                            'id', ek.id,
                            'title', ek.title,
                            'status_id', ks.id,
                            'status_title', ks.status_title,
                            'status_level', ks.level,
                            'evaluator_id', ev.id,
                            'evaluator', ev.name
                        )
                    ) AS kpis_details
                FROM 
                    kpis_employeeskpis AS ek
                LEFT JOIN kpis_kpisstatus AS ks ON ek.kpis_status_id = ks.id
                LEFT JOIN employees_employees AS ev ON ek.evaluator_id = ev.id
                WHERE 
                    ek.is_active = TRUE 
                    AND ek.ep_batch_id = (SELECT ep_batch_id FROM params)
                    AND (ks.level  = COALESCE(NULLIF((SELECT status_levels FROM params), 0), ks.level))  -- Filter by status_levels
                GROUP BY 
                    ek.employee_id
            ),
            
            -- Status count data aggregation
            status_count_data AS (
                SELECT 
                    employee_id,
                    JSON_AGG(
                        JSON_BUILD_OBJECT(
                            'id', status_id,
                            'status_title', status_title,
                            'status_level', status_level,
                            'status_count', status_count
                        )
                    ) AS status_count_details
                FROM 
                    kpi_status_count
                GROUP BY 
                    employee_id
            )
            
        SELECT 
            ed.employee_id,
            ed.employee_name,
            ed.profile_image,
            ed.employee_type_id,
            ed.employee_type_title,
            ed.department_id,
            ed.department_title,
            ed.designation_title,
            COALESCE(kd.total_kpis, 0) AS total_kpis,
            JSON_BUILD_OBJECT(
                'kpis_details', COALESCE(kd.kpis_details, '[]'),
                'status_count_details', COALESCE(sc.status_count_details, '[]')
            ) AS employee_kpis_data
        FROM 
            employee_data AS ed
        LEFT JOIN 
            kpi_data AS kd ON ed.employee_id = kd.employee_id
        LEFT JOIN 
            status_count_data AS sc ON ed.employee_id = sc.employee_id
        ORDER BY 
            ed.employee_id;
                """, [organization_id,employee_id,department_id,ep_batch,stauts_level])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                # Parse the employees_data field into a list of dictionaries
        # for row in rows:
        #         row['employee_kpis_data'] = parse_employees_data(row['employee_kpis_data'])

        return rows



def parse_employees_data(employees_data):
    # Parse the employees_data string into a list of dictionaries
    return json.loads("[" + employees_data + "]")


