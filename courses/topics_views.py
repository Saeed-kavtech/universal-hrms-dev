from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .models import ModuleTopics, Courses, CourseModules
from .serializers import ModuleTopicsViewsetSerializers, CourseModulesViewsetSerializers
from helpers.status_messages import *
from logs.views import UserLoginLogsViewset

class ModuleTopicsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return {'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''}
            organization_id = user_organization.id

            module_id = self.kwargs['module_id']
            
            module_query = CourseModules.objects.filter(id=module_id)
            if module_query.exists():
                if not module_query.filter(is_active=True).exists():
                    return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Course Module does not exists', 'system_status_message': ''})
                module_obj = module_query.first()
                if module_obj.course.organization.id != organization_id:
                    return Response({'status': 400, 'system_status':status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'User do not have previlage to access data of another organization', 'system_error_message': ''})
            else:
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Course Module does not exists', 'system_status_message': ''})

            obj = ModuleTopics.objects.filter(course_module=module_id, is_active = True).order_by('id')
            serializer = ModuleTopicsViewsetSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
           return exception(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            module_id = self.kwargs['module_id']
            topic_id = self.kwargs['topic_id'] 

            topic_checks = self.topicChecks(request, module_id, topic_id)
            if topic_checks['status'] == 400:
                return Response(topic_checks)

            obj = ModuleTopics.objects.get(id=topic_id, course_module=module_id)
            serializer = ModuleTopicsViewsetSerializers(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    
    def create(self, request, *args, **kwargs):
        try:
            module_id = self.kwargs['module_id']

            query = CourseModules.objects.filter(id=module_id)
            if not query.exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'message': 'Module does not exists', 'data': '', 'system_status_message': ''})
            elif query.filter(is_active=False):
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'message': 'Module is not active', 'data': '', 'system_status_message': ''})
            request.data['course_module'] = module_id
            serializer = ModuleTopicsViewsetSerializers(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)

        except Exception as e:
            return exception(e)


    def patch(self, request, *args, **kwargs):
        try:
            module_id = self.kwargs['module_id']
            topic_id = self.kwargs['topic_id'] 

            topic_checks = self.topicChecks(request, module_id, topic_id)
            if topic_checks['status'] == 400:
                return Response(topic_checks)
            
            # if module id is passed while updating. This checks whether active module exists or not
            if 'module' in request.data:
                module_id = request.data['module']
                module_query = ModuleTopics.objects.filter(id=module_id)
                
                if not module_query.exists():
                    message = "The module does not exist"
                    return Response({'status': 400, 'system_status': 400, 'data': '', 'message': message, 'system_status_message': ''})
                if not module_query.filter(is_active=True).exists():
                    message = "The module is deactivated"
                    return Response({'status': 400, 'system_status': 400, 'data': '', 'message': message, 'system_status_message': ''})
                
            


            obj = ModuleTopics.objects.get(id=topic_id, course_module=module_id)

            serializer = ModuleTopicsViewsetSerializers(obj, data=request.data, partial=True)
                        
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()
            
            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)

    
    def delete(self, request, *args, **kwargs):
        try:
            module_id = self.kwargs['module_id']
            topic_id = self.kwargs['topic_id'] 

            topic_checks = self.topicChecks(request, module_id, topic_id)
            if topic_checks['status'] == 400:
                return Response(topic_checks)

            obj = ModuleTopics.objects.get(id=topic_id, course_module=module_id)
            
            if obj.is_active == False:
                return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': '', 'message': 'This module topic is already deactivated', 'system_status_message': ''})    
                        
            obj.is_active = False
            obj.save()
            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT,  'data': '', 'message': 'Successfully Deleted', 'system_status_message': ''})

        except Exception as e:
            return exception(e)


    def topicChecks(self, request, module_id, topic_id):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return {'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''}

            query = CourseModules.objects.filter(id=module_id)
            if not query.exists():
                return {'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'message': 'Module does not exists', 'data': '', 'system_status_message': ''}
            elif query.filter(is_active=False):
                return {'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'message': 'Module is not active', 'data': '', 'system_status_message': ''}
            
            topic_query = ModuleTopics.objects.filter(id=topic_id)
            if not topic_query.exists():
                return {'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'message': 'Topics does not exists', 'data': '', 'system_status_message': ''}

            if request.method == 'GET':
                if topic_query.filter(is_active=False).exists():
                    return {'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'message': 'Topic is not active', 'data': '', 'system_status_message': ''}
            
            module_obj = query.first()
            # if course organization id and logged in user id does not match
            if module_obj.course.organization.id != user_organization.id:
                return {'status': 400, 'system_status':status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'User do not have previlage to access data of another organization', 'system_error_message': ''}
   
            return {'status': 200}
        except Exception as e:
            return {'status': 400, 'system_status': 400, 'data': '', 'message': '', 'system_error_message': str(e)}


   