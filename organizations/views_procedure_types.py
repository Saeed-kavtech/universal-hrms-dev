from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from helpers.renderers import Renderer
from rest_framework.response import Response
from .models import *
from organizations.models import Organization
from rest_framework import viewsets
from .serializers import *

from helpers.status_messages import *
from helpers.custom_permissions import *

from logs.views import UserLoginLogsViewset

class ProcedureTypesViewset(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]

	def list(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			obj = ProcedureTypes.objects.filter(organization=user_organization.id)
			serializer = ProcedureTypesSerializers(obj, many=True)
			return success(serializer.data)

		except Exception as e:
			return exception(e)

	def create(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			request.data['organization'] = user_organization.id 
			request.data['user'] = request.user.id

			serializer = ProcedureTypesSerializers(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return successfullyCreated(serializer.data)
			else:
				return serializerError(serializer.errors)

		except Exception as e:
			return exception(e)

	def get(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			pk = self.kwargs['pk']
			if ProcedureTypes.objects.filter(pk=pk, organization=user_organization.id).exists():
				obj = ProcedureTypes.objects.get(pk=pk)
				serializer = ProcedureTypesSerializers(obj, many=False)
				return success(serializer.data)
			else:
				return nonexistent(var='Role')
		except Exception as e:
			return exception(e)

	def partial_update(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			pk = self.kwargs['pk']
			if ProcedureTypes.objects.filter(pk=pk, organization=user_organization.id).exists():
				obj = ProcedureTypes.objects.get(pk=pk)
				serializer = ProcedureTypesSerializers(obj, data=request.data, partial=True)
				if serializer.is_valid():
					serializer.save()
					return successfullyUpdated(serializer.data)
				else:
					return serializerError(serializer.errors)
		except Exception as e:
			return exception(e)

	def destroy(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			pk = self.kwargs['pk']
			if ProcedureTypes.objects.filter(pk=pk, organization=user_organization.id).exists():
				obj = ProcedureTypes.objects.get(pk=pk)
				obj.is_active=False
				obj.save()
				serializer = ProcedureTypesSerializers(obj, many=False)
				return success(serializer.data)
		except Exception as e:
			return exception(e)
