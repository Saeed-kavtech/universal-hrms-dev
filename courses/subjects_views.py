from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .serializers import *
from helpers.status_messages import *
from logs.views import UserLoginLogsViewset

# Create your views here.
class SubjectsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
            # Subjects are organization based
            obj = Subjects.objects.filter(organization = user_organization.id, is_active = True).order_by('title')
            serializer = SubjectsViewsetSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
           return exception(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            slug = self.kwargs['slug']
            uuid = self.kwargs['uuid']

            subject_data = self.subjectChecks(request, uuid, slug)
            # checks if some error exists
            if subject_data['status'] == 400:
                return Response(subject_data)

            # This returns a single object
            obj = subject_data['data']

            serializer = SubjectsViewsetSerializers(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
            request.data['organization'] = user_organization.id

            serializer = SubjectsViewsetSerializers(data = request.data)
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

            subject_data = self.subjectChecks(request, uuid, slug)
            if subject_data['status'] == 400:
                return Response(subject_data)
            
            obj = subject_data['data']
            
            serializer = SubjectsViewsetSerializers(obj, data=request.data, partial=True)
                        
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

            subject_data = self.subjectChecks(request, uuid, slug)
            if subject_data['status'] == 400:
                return Response(subject_data)

            obj = subject_data['data']

            if obj.is_active == False:
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Subject is already deactivated', 'system_status_message': ''})    

            subject_id = obj.id
            if Programs.objects.filter(subject=subject_id, is_active=True).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'To deactivate the subject, you need to deactivate the program first', 'system_status_message': ''})


            obj.is_active = False
            obj.save()
            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT,  'data': '', 'message': 'Successfully Deleted', 'system_status_message': ''})

        except Exception as e:
            return exception(e)


    def subjectChecks(self, request, uuid, slug):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return {'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''}

            query = Subjects.objects.filter(uuid=uuid, slug_title=slug)

            if not query.exists():
                return {'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This id or slug title does not exists.', 'system_error_message': ''}

            if request.method == "GET":
                if query.filter(is_active=False).exists():
                    return {'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This Subject is deactivated', 'system_error_message': ''}

            obj = Subjects.objects.get(uuid=uuid, slug_title=slug)  

            # if logged in user belongs to another organization           
            if obj.organization.id != user_organization.id:
                return {'status': 400, 'system_status':status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'User do not have previlage to access data of another organization', 'system_error_message': ''}
            
            return {'status': 200, 'message': '','data': obj}
        except Exception as e:
            return {'status': 400, 'message': str(e), 'data': ''}
