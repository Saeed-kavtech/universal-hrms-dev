from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .models import CourseModules, Courses
from .serializers import CourseModulesViewsetSerializers
from helpers.status_messages import *
from logs.views import UserLoginLogsViewset
from .pre_requisite_views import CoursePreRequisiteViewset

class CourseModulesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            slug = self.kwargs['slug']
            uuid = self.kwargs['uuid']

            data_check = CoursePreRequisiteViewset.courseChecks(self, request, slug, uuid)
            if data_check['status'] == 400:
                return Response(data_check)
            
            obj = CourseModules.objects.filter(course__uuid = uuid, course__slug_title=slug, is_active = True).order_by('id')
            serializer = CourseModulesViewsetSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
           return exception(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            slug = self.kwargs['slug']
            uuid = self.kwargs['uuid']    
            module_id = self.kwargs['module_id'] 

            data_check = CoursePreRequisiteViewset.courseChecks(self, request, slug, uuid)
            if data_check['status'] == 400:
                return Response(data_check)

            query = CourseModules.objects.filter(id=module_id, course__slug_title=slug, course__uuid=uuid)
            if not query.exists():
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'No course module exists at this id', 'system_error_message': ''})

            if not query.filter(is_active=True).exists():
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'This course module is inactive', 'system_error_message': ''})
           
            obj = CourseModules.objects.get(id=module_id, course__slug_title=slug, course__uuid=uuid)
            serializer = CourseModulesViewsetSerializers(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    
    def create(self, request, *args, **kwargs):
        try:
            slug = self.kwargs['slug']
            uuid = self.kwargs['uuid']

            data_check = CoursePreRequisiteViewset.courseChecks(self, request, slug, uuid)
            if data_check['status'] == 400:
                return Response(data_check)

            serializer = CourseModulesViewsetSerializers(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)

        except Exception as e:
            return exception(e)


    def patch(self, request, *args, **kwargs):
        try:
            slug = self.kwargs['slug']
            uuid = self.kwargs['uuid']
            module_id = self.kwargs['module_id'] 
                       
            data_check = CoursePreRequisiteViewset.courseChecks(self, request, slug, uuid)
            if data_check['status'] == 400:
                return Response(data_check)

            query = CourseModules.objects.filter(id=module_id, course__slug_title=slug, course__uuid=uuid)
            
            if not query.exists():
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'This course module does not exists', 'system_error_message': ''})

            obj = CourseModules.objects.get(id=module_id, course__slug_title=slug, course__uuid=uuid)
        
            
            serializer = CourseModulesViewsetSerializers(obj, data=request.data, partial=True)
                        
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()
            
            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)

    
    def delete(self, request, *args, **kwargs):
        try:
            slug = self.kwargs['slug']
            uuid = self.kwargs['uuid']

            module_id = self.kwargs['module_id']

            data_check = CoursePreRequisiteViewset.courseChecks(self, request, slug, uuid)
            if data_check['status'] == 400:
                return Response(data_check)
                                    
            query = CourseModules.objects.filter(id=module_id, course__slug_title=slug, course__uuid=uuid)
            
            if not query.exists():
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'This course module does not exists', 'system_error_message': ''})

            obj = CourseModules.objects.get(id=module_id, course__slug_title=slug, course__uuid=uuid)
            
            if obj.is_active == False:
                return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': '', 'message': 'This course module is already deactivated', 'system_status_message': ''})    
                        
            obj.is_active = False
            obj.save()
            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT,  'data': '', 'message': 'Successfully Deleted', 'system_status_message': ''})

        except Exception as e:
            return exception(e)



   