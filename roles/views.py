from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from helpers.renderers import Renderer
from rest_framework.response import Response
from .models import *
from helpers.custom_permissions import IsAuthenticated, DoesOrgExists
from organizations.models import Organization
from rest_framework import viewsets
from .serializers import *

from helpers.status_messages import *
from helpers.custom_permissions import *

# queryset = RolesTypes.objects.all()
# 	serializer_class = RolesTypesSerializer

# routers


class RoleTypesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]
    queryset = RoleTypes.objects.all()
    serializer_class = RoleTypesSerializer

    def list(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            request.data['organization'] = user_organization.id
            roles = RoleTypes.objects.filter(organization=user_organization.id, is_active=True)
            serializer = RoleTypesSerializer(roles, many=True)
            return success(serializer.data)
        except Exception as e:
            return Response({'status': 400, 'system_error_message': str(e)})

    def create(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            request.data['organization'] = user_organization.id
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({'status': 400, 'system_error_message': str(e)})



class RolesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def list(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')

            obj = Roles.objects.filter(organization=user_organization.id, is_active=True, role_type__title__iexact='project roles')
            serializer = RolesSerializers(obj, many=True)
            return success(serializer.data)

        except Exception as e:
            return exception(e)
        
    def systemrolelist(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')

            obj = Roles.objects.filter(organization=user_organization.id, is_active=True, role_type__title__iexact='system roles')
            serializer = RolesSerializers(obj, many=True)
            return success(serializer.data)

        except Exception as e:
            return exception(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            uuid = self.kwargs['uuid']
            if Roles.objects.filter(uuid=uuid, organization=user_organization.id).exists():
                obj = Roles.objects.get(uuid=uuid)
                serializer = RolesSerializers(obj, many=False)
                return success(serializer.data)
            else:
                return nonexistent(var='Role')
        except Exception as e:
            return exception(e)

    
    def create(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            request.data['organization'] = user_organization.id
            request.data['user'] = request.user.id

            if not 'role_type' in request.data:
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Role types is required field', 'system_status_message': ''})


            role_types_id = request.data['role_type']
            if not RoleTypes.objects.filter(id=role_types_id, organization=user_organization.id).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Role type does not exists at this id', 'system_status_message': ''})


            serializer = RolesSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return successfullyCreated(serializer.data)
            else:
                return serializerError(serializer.errors)

        except Exception as e:
            return exception(e)


    def patch(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            uuid = self.kwargs['uuid']

            if 'role_type' in request.data:
                role_types_id = request.data['role_type']
                if not RoleTypes.objects.filter(id=role_types_id, organization=user_organization.id).exists():
                    return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Role does not exists at this id', 'system_status_message': ''})

            if Roles.objects.filter(uuid=uuid, organization=user_organization.id).exists():
                obj = Roles.objects.get(uuid=uuid)
                serializer = RolesSerializers(
                    obj, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return successfullyUpdated(serializer.data)
                else:
                    return serializerError(serializer.errors)
        except Exception as e:
            return exception(e)
        


    def delete(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            uuid = self.kwargs['uuid']
            if Roles.objects.filter(uuid=uuid, organization=user_organization.id).exists():
                obj = Roles.objects.get(uuid=uuid)
                obj.is_active = False
                obj.save()
                serializer = RolesSerializers(obj, many=False)
                return success(serializer.data)
        except Exception as e:
            return exception(e)


class PreDataRolesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def pre_data(self, organization_id):
        try:
            data = Roles.objects.filter(
                is_active=True, organization=organization_id)
            serializer = PreDataRolesSerializers(data, many=True)
            return serializer.data
        except Exception as e:
            return []
