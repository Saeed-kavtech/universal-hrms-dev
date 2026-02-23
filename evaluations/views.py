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



class RoleProcedureAccessViewset(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]
	prenderer_classes = [Renderer]

	def list(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			obj = RoleProcedureAccess.objects.filter(role__organization=user_organization)
			serializer = RoleProcedureAccessSerializers(obj, many=True)
			return success(serializer.data)

		except Exception as e:
			return exception(e)

	def create(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
			
			rp_obj = self.checkIfRoleProcedureAccessExist(user_organization.id, request.data)
			if rp_obj['status']==202:
				request.data['is_allow'] = True
				request.data['is_active'] = True
				serializer = RoleProcedureAccessSerializers(rp_obj['data'], data=request.data)
			elif rp_obj['status']==200:
				serializer = RoleProcedureAccessSerializers(data=request.data)
			else:
				return errorMessage(rp_obj['message'])

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
			if RoleProcedureAccess.objects.filter(pk=pk, role__organization=user_organization).exists():
				obj = RoleProcedureAccess.objects.get(pk=pk)
				serializer = RoleProcedureAccessSerializers(obj, many=False)
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

			uuid = self.kwargs['uuid']
			if RoleProcedureAccess.objects.filter(pk=pk, role__organization=user_organization).exists():
				obj = RoleProcedureAccess.objects.get(pk=pk)
				serializer = UpdateRoleProcedureAccessSerializers(obj, data=request.data, partial=True)
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
			if RoleProcedureAccess.objects.filter(pk=pk, role__organization=user_organization).exists():
				obj = RoleProcedureAccess.objects.get(pk=pk)
				obj.is_active=False
				obj.save()
				serializer = RoleProcedureAccessSerializers(obj, many=False)
				return success(serializer.data)
		except Exception as e:
			return exception(e)

	def checkIfRoleProcedureAccessExist(self, organization_id, data):
		try:
			result = {"status":200, "data":"", "message":"Successfully get the record"}
			rpa_obj = None
			role = None 
			procedure = None
			if 'id' in data:
				if RoleProcedureAccess.objects.filter(pk=data['id'], role__organization__id=organization_id).exists():
					rpa_obj = RoleProcedureAccess.objects.get(pk=data['id'])
					result['data'] = rpa_obj

				else:
					result['status']=400
					result['message'] = "Record does not exist."
					return result

			if 'role' in data:
				if Roles.objects.filter(pk=data['role'], organization=organization_id).exists():
					role = Roles.objects.get(pk=data['role'])
				else:
					result['status']=400
					result['message'] = "Role does not belong to this organization."
					return result

			if 'procedure' in data:
				if ProcedureTypes.objects.filter(pk=data['procedure'], organization=organization_id).exists():
					procedure = ProcedureTypes.objects.get(pk=data['procedure'])
				else:
					result['status']=400
					result['message'] = "ProcedureType does not belong to this organization."
					return result

			if rpa_obj is None:
				if RoleProcedureAccess.objects.filter(role=data['role'], procedure=data['procedure']).exists():
					obj = RoleProcedureAccess.objects.filter(role=data['role'], procedure=data['procedure']).first()
					result['data'] = obj
					result['status'] = 202
				else:
					result['message'] = "RoleProcedureAccess with this data processed"
				return result


			
		except Exception as e:
			result['status'] = 400
			result['message'] = str(e)
			return result


class EvaluationsViewset(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]
	prenderer_classes = [Renderer]

	def list(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			obj = Evaluations.objects.filter(organization=user_organization.id)
			serializer = EvaluationsSerializers(obj, many=True)
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

			serializer = EvaluationsSerializers(data=request.data)
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

			uuid = self.kwargs['uuid']
			if Evaluations.objects.filter(uuid=uuid, organization=user_organization.id).exists():
				obj = Evaluations.objects.get(uuid=uuid)
				serializer = EvaluationsSerializers(obj, many=False)
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

			uuid = self.kwargs['uuid']
			if Evaluations.objects.filter(uuid=uuid, organization=user_organization.id).exists():
				obj = Evaluations.objects.get(uuid=uuid)
				serializer = EvaluationsSerializers(obj, data=request.data, partial=True)
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

			uuid = self.kwargs['uuid']
			if Evaluations.objects.filter(uuid=uuid, organization=user_organization.id).exists():
				obj = Evaluations.objects.get(uuid=uuid)
				obj.is_active=False
				obj.save()
				serializer = EvaluationsSerializers(obj, many=False)
				return success(serializer.data)
		except Exception as e:
			return exception(e)


class EvaluationProcedureQuestionsViewset(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]

	def list(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			uuid = self.kwargs['uuid']
			obj = EvaluationProcedureQuestions.objects.filter(evaluation__organization__id=user_organization.id, evaluation__uuid=uuid)
			serializer = EvaluationProcedureQuestionsSerializers(obj, many=True)
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

			serializer = EvaluationProcedureQuestionsSerializers(data=request.data)
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

			uuid = self.kwargs['uuid']
			pk = self.kwargs['pk']
			if EvaluationProcedureQuestions.objects.filter(pk=pk, evaluation__organization__id=user_organization.id, evaluation__uuid=uuid).exists():
				obj = EvaluationProcedureQuestions.objects.get(pk=pk)
				serializer = EvaluationProcedureQuestionsSerializers(obj, many=False)
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

			uuid = self.kwargs['uuid']
			pk = self.kwargs['pk']
			if EvaluationProcedureQuestions.objects.filter(pk=pk, evaluation__organization__id=user_organization.id, evaluation__uuid=uuid).exists():
				obj = EvaluationProcedureQuestions.objects.get(pk=pk)
				serializer = EvaluationProcedureQuestionsSerializers(obj, data=request.data, partial=True)
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

			uuid = self.kwargs['uuid']
			pk = self.kwargs['pk']
			if EvaluationProcedureQuestions.objects.filter(pk=pk, evaluation__organization__id=user_organization.id, evaluation__uuid=uuid).exists():
				obj = EvaluationProcedureQuestions.objects.get(pk=pk)
				obj.is_active=False
				obj.save()
				serializer = EvaluationProcedureQuestionsSerializers(obj, many=False)
				return success(serializer.data)
		except Exception as e:
			return exception(e)


class PreDataEvaluationsView(generics.ListAPIView):
	permission_classes = [IsAuthenticated]

	def pre_data(self, organization_id):
		try:
			data = Evaluations.objects.filter(is_active=True, organization=organization_id)
			serializer = PreDataEvaluationsSerializers(data, many=True)
			return serializer.data
		except Exception as e:
			return []
