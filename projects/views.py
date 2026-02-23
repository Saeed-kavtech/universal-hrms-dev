from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from .models import *
from helpers.status_messages import *
from helpers.custom_permissions import IsAuthenticated, DoesOrgExists
from rest_framework import generics

# Create your views here.
class ProjectsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def list(self, request, *args, **kwargs):
        try:
            # comment for git pull
            user_organization = request.data.get('organization_profile')
            obj = Projects.objects.filter(organization=user_organization.id, is_active=True)
            serializer = ProjectsViewsetSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            uuid = self.kwargs['uuid']

            query = Projects.objects.filter(uuid=uuid,  organization=user_organization.id)
            if not query.exists():
                return errorMessage('No projects exists at this uuid')
                
            if query.filter(is_active=False).exists():
                return errorMessage('The project is deactivated at this uuid')
                
            obj = query.first()
            serializer = ProjectsViewsetSerializers(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)   


    def create(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            request.data['organization'] = user_organization.id

            if 'code' in request.data:
                code = request.data['code']
                project_query = Projects.objects.filter(organization=user_organization.id, code=code)
                if project_query.filter(is_active=True).exists():
                    return errorMessage('Project is deactivated')
                if project_query.exists():
                    return errorMessage('This code already exists')


            serializer = ProjectsViewsetSerializers(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)      
            
        except Exception as e:
            return exception(e)
        

    def patch(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            uuid = self.kwargs['uuid']

            query = Projects.objects.filter(uuid=uuid, organization=user_organization.id)
            if not query.exists():
                return errorMessage('No projects exists at this uuid')
            
            if 'code' in request.data:
                project_query = Projects.objects.filter(organization=user_organization.id, code=request.data['code'])
                if project_query.filter(is_active=True).exists():
                    return errorMessage('Project is deactivated')
                if project_query.exists():
                    return errorMessage('This code already exists')


            obj = query.first()
            serializer = ProjectsViewsetSerializers(obj, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()
            
            return successfullyUpdated(serializer.data)

        except Exception as e:
            return exception(e)
        

    def delete(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            uuid = self.kwargs['uuid']

            query = Projects.objects.filter(uuid=uuid, organization=user_organization.id)
            if not query.exists():
                return errorMessage('No project exists at this uuid')
            if query.filter(is_active=False):
                return errorMessage('Project is already deactivated')

            obj = query.first()
            obj.is_active = False
            obj.save()
            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT,  'data': '', 'message': 'Successfully Deleted', 'system_status_message': ''})

        except Exception as e:
            return exception(e)


class PreProjectDataView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def get(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            obj = Projects.objects.filter(organization=user_organization.id, is_active=True)
            serializer = PreProjectDataViewSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def pre_data(self,user_organization):
        try:
            # user_organization = request.data.get('organization_profile')
            obj = Projects.objects.filter(organization=user_organization, is_active=True)
            serializer = PreProjectDataViewSerializers(obj, many=True)
            return serializer.data
        except Exception as e:
            return exception(e)
