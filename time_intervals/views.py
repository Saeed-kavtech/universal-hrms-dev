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


class TimeIntervalsViewset(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]
	prenderer_classes = [Renderer]

	def list(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			obj = TimeIntervals.objects.filter(organization=user_organization.id).order_by('-id')
			serializer = TimeIntervalsSerializers(obj, many=True)
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

			serializer = TimeIntervalsSerializers(data=request.data)
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
			if TimeIntervals.objects.filter(pk=pk, organization=user_organization.id).exists():
				obj = TimeIntervals.objects.get(pk=pk)
				serializer = TimeIntervalsSerializers(obj, many=False)
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
			if TimeIntervals.objects.filter(pk=pk, organization=user_organization.id).exists():
				obj = TimeIntervals.objects.get(pk=pk)
				serializer = TimeIntervalsSerializers(obj, data=request.data, partial=True)
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
			if TimeIntervals.objects.filter(pk=pk, organization=user_organization.id).exists():
				obj = TimeIntervals.objects.get(pk=pk)
				obj.is_active=False
				obj.save()
				serializer = TimeIntervalsSerializers(obj, many=False)
				return success(serializer.data)
		except Exception as e:
			return exception(e)


class TimeSlotsViewset(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]
	prenderer_classes = [Renderer]

	def list(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			ti_pk = self.kwargs['ti_pk']
			if not TimeIntervals.objects.filter(organization=user_organization.id, pk=ti_pk).exists():
				return nonexistent(var="TimeInterval")
			obj = TimeSlots.objects.filter(time_interval = ti_pk)
			serializer = TimeSlotsSerializers(obj, many=True)
			return success(serializer.data)

		except Exception as e:
			return exception(e)

	def create(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			ti_pk = self.kwargs['ti_pk']
			if not TimeIntervals.objects.filter(organization=user_organization.id, pk=ti_pk).exists():
				return errorMessage("TimeInterval does not exists.")
			
			if int(ti_pk)!=request.data.get('time_interval'):
				return errorMessage("TimeInterval does not match")

			serializer = TimeSlotsSerializers(data=request.data)
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

			ti_pk = self.kwargs['ti_pk']
			if not TimeIntervals.objects.filter(organization=user_organization.id, pk=ti_pk).exists():
				return errorMessage("TimeInterval does not exists.")

			pk = self.kwargs['pk']
			if TimeSlots.objects.filter(pk=pk, time_interval=ti_pk).exists():
				obj = TimeSlots.objects.get(pk=pk)
				serializer = TimeSlotsSerializers(obj, many=False)
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

			ti_pk = self.kwargs['ti_pk']
			if not TimeIntervals.objects.filter(organization=user_organization.id, pk=ti_pk).exists():
				return errorMessage("TimeInterval does not exists.")

			pk = self.kwargs['pk']
			if TimeSlots.objects.filter(pk=pk, time_interval=ti_pk).exists():
				obj = TimeSlots.objects.get(pk=pk)
				serializer = TimeSlotsSerializers(obj, data=request.data, partial=True)
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
			if TimeSlots.objects.filter(pk=pk, organization=user_organization.id).exists():
				obj = TimeSlots.objects.get(pk=pk)
				obj.is_active=False
				obj.save()
				serializer = TimeSlotsSerializers(obj, many=False)
				return success(serializer.data)
		except Exception as e:
			return exception(e)

	def pre_data(self, organization_id, interval=None):
		try:
			if interval is not None:
				data = TimeSlots.objects.filter(interval=interval, is_active=True, time_interval__organization__id=organization_id)
			else:
				data = TimeSlots.objects.filter(is_active=True, time_interval__organization__id=organization_id)

			serializer = PreDataTimeSlotsSerializers(data, many=True)
			return serializer.data

		except Exception as e:
			return []

