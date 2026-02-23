from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .serializers import *
from helpers.status_messages import *
from logs.views import UserLoginLogsViewset

class CoursePreRequisiteViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            slug = self.kwargs['slug']
            uuid = self.kwargs['uuid']

            data_check = self.courseChecks(request, slug, uuid)
            if data_check['status'] == 400:
                return Response(data_check)
            
            obj = CoursePreRequisite.objects.filter(course__uuid = uuid, course__slug_title=slug, is_active = True).order_by('pre_requisite')
            serializer = CoursePreRequisiteViewsetSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
           return exception(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            slug = self.kwargs['slug']
            uuid = self.kwargs['uuid']    
            pre_req_id = self.kwargs['pre_req'] 

            data_check = self.courseChecks(request, slug, uuid)
            if data_check['status'] == 400:
                return Response(data_check)

            query = CoursePreRequisite.objects.filter(id=pre_req_id, course__slug_title=slug, course__uuid=uuid)
            if not query.exists():
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'No pre requisite exists at this id', 'system_error_message': ''})

            if not query.filter(is_active=True).exists():
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'This pre-requisite is inactive', 'system_error_message': ''})
           
            obj = CoursePreRequisite.objects.get(id=pre_req_id, course__slug_title=slug, course__uuid=uuid)
            serializer = CoursePreRequisiteViewsetSerializers(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    
    def create(self, request, *args, **kwargs):
        try:
            slug = self.kwargs['slug']
            uuid = self.kwargs['uuid']

            data_check = self.courseChecks(request, slug, uuid)
            if data_check['status'] == 400:
                return Response(data_check)

            serializer = CoursePreRequisiteViewsetSerializers(data = request.data)
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
            pre_req_id = self.kwargs['pre_req'] 
                       
            data_check = self.courseChecks(request, slug, uuid)
            if data_check['status'] == 400:
                return Response(data_check)

            query = CoursePreRequisite.objects.filter(id=pre_req_id, course__slug_title=slug, course__uuid=uuid)
            
            if not query.exists():
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'This course does not exists', 'system_error_message': ''})

            obj = CoursePreRequisite.objects.get(id=pre_req_id, course__slug_title=slug, course__uuid=uuid)
        
            
            serializer = CoursePreRequisiteViewsetSerializers(obj, data=request.data, partial=True)
                        
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

            pre_req_id = self.kwargs['pre_req']

            data_check = self.courseChecks(request, slug, uuid)
            if data_check['status'] == 400:
                return Response(data_check)
                                    
            query = CoursePreRequisite.objects.filter(id=pre_req_id, course__slug_title=slug, course__uuid=uuid)
            
            if not query.exists():
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'This course pre-requisite does not exists', 'system_error_message': ''})

            obj = CoursePreRequisite.objects.get(id=pre_req_id, course__slug_title=slug, course__uuid=uuid)
                     

            if obj.is_active == False:
                return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': '', 'message': 'This course pre-requisite is already deactivated', 'system_status_message': ''})    
                        
            obj.is_active = False
            obj.save()
            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT,  'data': '', 'message': 'Successfully Deleted', 'system_status_message': ''})

        except Exception as e:
            return exception(e)


    def courseChecks(self, request, slug, uuid):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return {'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''}
      
            query = Courses.objects.filter(uuid=uuid, slug_title=slug)
            
            if not query.exists():
                return {'status':400, 'system_status':400, 'data': '', 'message': 'uuid or slug title is incorrect or does not exists', 'system_error_message': ''}

            # if request.method != 'PATCH':
            #     if not query.filter(is_active=True):
            #         return {'status':400, 'system_status':400, 'data': '', 'message': 'This course is inactive', 'system_error_message': ''}
            
            # if no organization exists against this course
            query = Courses.objects.get(uuid=uuid, slug_title=slug)
            
            # Course child would get id assign based on uuid and slug
            if request.method == 'POST':
                request.data['course'] = query.id

            # # if subject is inactive then he cannot access the course
            # if query.program.subject.is_active == False:
            #     return {'status': 400, 'system_status': 400, 'message': 'The Subject is deactivated', 'data': '', 'system_error_message': ''}

            # # if program is inactive. Then he cannot access the course
            # if query.program.is_active == False:
            #     return {'status': 400, 'system_status': 400, 'data': '', 'message': 'The Program is deactivated', 'system_error_message': ''}
            
            # organization cannot be null
            if query.organization is None:
                return {'status': 400, 'system_status': 400, 'data': '', 'message': 'No organization is assigned to this course', 'system_error_message': ''}

            # if course organization id and logged in user id does not match
            if query.organization.id != user_organization.id:
                return {'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'User do not have previlage to access data of another organization', 'system_error_message': ''}

            return {'status': 200}
        except Exception as e:
            return {'status': 400, 'system_status': 400, 'data': '', 'message': '', 'system_error_message': str(e)}

