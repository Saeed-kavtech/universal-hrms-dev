from django.shortcuts import render
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .serializers import *
from helpers.status_messages import *
from logs.views import UserLoginLogsViewset

# Create your views here.
class ProgramsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
            obj = Programs.objects.filter(subject__organization = user_organization.id, subject__is_active = True, is_active=True).order_by('title')
            serializer = ProgramsViewsetSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
           return exception(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            slug = self.kwargs['slug']
            uuid = self.kwargs['uuid']
            
            program_data = self.programChecks(request, slug, uuid)
            if program_data['status'] == 400:
                return Response(program_data)
            
            obj = program_data['data']
            
            serializer = ProgramsViewsetSerializers(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    
    def create(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
            # This would get the value of subject from request.data
            if 'subject' in request.data: 
                subject_id = request.data.get('subject')
            else:
                return Response({'status': 400, 'system_status':400, 'data': '', 'message': 'Subject is a required field', 'system_error_message': ''})
            
            # before creating program. Program need to pass all these subject checks
            
            query = Subjects.objects.filter(id=subject_id)
            if not query.exists():
                return Response({'status': 400, 'system_status':400, 'data': '', 'message': 'No subject exists at this id', 'system_error_message': ''})

            elif not query.filter(is_active=True).exists():
                return Response({'status': 400, 'system_status':400, 'data': '', 'message': 'No active subject exists at this id', 'system_error_message': ''})
    
            query=query.first()

            if query.organization.id != user_organization.id:
                return Response({'status': 400, 'system_status':status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'User do not have previlage to access data of another organization', 'system_error_message': ''})


            serializer = ProgramsViewsetSerializers(data = request.data)
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
    
            program_data = self.programChecks(request, slug, uuid)
            if program_data['status'] == 400:
                return Response(program_data)
            
            obj = program_data['data']

            if 'subject' in request.data:
                subject_id = request.data['subject']
                if not Subjects.objects.filter(id=subject_id, is_active=True).exists():
                    return Response({'status': 400, 'system_status': 400, 'data': 'This subject id cannot be assigned. Kindly, activate the subject first', 'message': '', 'system_status_message': ''})
            
            serializer = ProgramsViewsetSerializers(obj, data=request.data, partial=True)
                        
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

            program_data = self.programChecks(request, slug, uuid)
            if program_data['status'] == 400:
                return Response(program_data)
            
            obj = program_data['data']

            if obj.is_active == False:
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Program is already deactivated', 'system_status_message': ''})    

            program_id = obj.id
            if Courses.objects.filter(program=program_id, is_active=True).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Active courses exists against this program. Kindly deactivate all the courses first', 'system_status_message': ''})
              
            obj.is_active = False
            obj.save()
            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT,  'data': '', 'message': 'Successfully Deleted', 'system_status_message': ''})

        except Exception as e:
            return exception(e)


    def programChecks(self, request, slug, uuid):   
        try: 
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return {'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''}

            query = Programs.objects.filter(slug_title=slug, uuid=uuid)
            
            if not query.exists():
                return {'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'No Program exists at this id and title', 'system_status_message': ''}

            if request.method == 'GET':
                if query.filter(is_active=False):
                    return {'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Program is inactive at this id', 'system_status_message': ''}

            obj = Programs.objects.get(slug_title=slug, uuid=uuid)
            subject_id = obj.subject.id
            if obj.subject.organization.id != user_organization.id:
                return {'status': 400, 'system_status':status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'User do not have previlage to access data of another organization', 'system_error_message': ''}

            if obj.subject.is_active == False:
                return {'status': 400,  'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Subject is inactive at this id', 'system_status_message': ''}
            
            
            if request.method == 'PATCH':
                if 'is_active' in request.data:
                    if request.data['is_active'] == True:
                        if not Subjects.objects.filter(id=subject_id, organization=user_organization.id, is_active=True).exists():
                            return {'status': 400, 'system_status': 400, 'data': '', 'message': 'To activate the program you need to activate the subject first', 'system_status_message': ''}


            return {'status': 200, 'data': obj}
        except Exception as e:
            return {'status': 400, 'system_status': 400, 'data': '', 'message': '', 'system_error_message': str(e)}


class PreProgramDataView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return {'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''}


            subject_obj = Subjects.objects.filter(is_active=True, organization=user_organization.id)
            subject_serializer = SubjectsViewsetSerializers(subject_obj, many=True)

            data = {'subject': subject_serializer.data}

            return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': data, 'message': 'Success', 'system_error_message': ''})

        except Exception as e:
            return exception(e)