from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from organizations.models import Organization
from rest_framework import viewsets

from helpers.status_messages import *
from helpers.custom_permissions import *

from .models import *
from .serializers import *

from logs.views import UserLoginLogsViewset


class ComplexityLevelsViewset(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]

	def list(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			obj = ComplexityLevels.objects.all()
			serializer = ComplexityLevelsSerializers(obj, many=True)
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

			serializer = ComplexityLevelsSerializers(data=request.data)
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
			if ComplexityLevels.objects.filter(pk=pk).exists():
				obj = ComplexityLevels.objects.get(pk=pk)
				serializer = ComplexityLevelsSerializers(obj, many=False)
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
			if ComplexityLevels.objects.filter(pk=pk).exists():
				obj = ComplexityLevels.objects.get(pk=pk)
				serializer = ComplexityLevelsSerializers(obj, data=request.data, partial=True)
				if serializer.is_valid():
					serializer.save()
					return successfullyUpdated(serializer.data)
				else:
					return serializerError(serializer.errors)
			else:
				return errorMessage("Score does not exist.")
		except Exception as e:
			return exception(e)

	def destroy(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			pk = self.kwargs['pk']
			if ComplexityLevels.objects.filter(pk=pk).exists():
				obj = ComplexityLevels.objects.get(pk=pk)
				obj.is_active=False
				obj.save()
				serializer = ComplexityLevelsSerializers(obj, many=False)
				return success(serializer.data)
			else:
				return errorMessage("Score type does not exists.")
		except Exception as e:
			return exception(e)

class ScoreTypesViewset(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]

	def list(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			obj = ScoreTypes.objects.all()
			serializer = ScoreTypesSerializers(obj, many=True)
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

			serializer = ScoreTypesSerializers(data=request.data)
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
			if ScoreTypes.objects.filter(pk=pk).exists():
				obj = ScoreTypes.objects.get(pk=pk)
				serializer = ScoreTypesSerializers(obj, many=False)
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
			if ScoreTypes.objects.filter(pk=pk).exists():
				obj = ScoreTypes.objects.get(pk=pk)
				serializer = ScoreTypesSerializers(obj, data=request.data, partial=True)
				if serializer.is_valid():
					serializer.save()
					return successfullyUpdated(serializer.data)
				else:
					return serializerError(serializer.errors)
			else:
				return errorMessage("Score does not exist.")
		except Exception as e:
			return exception(e)

	def destroy(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			pk = self.kwargs['pk']
			if ScoreTypes.objects.filter(pk=pk).exists():
				obj = ScoreTypes.objects.get(pk=pk)
				obj.is_active=False
				obj.save()
				serializer = ScoreTypesSerializers(obj, many=False)
				return success(serializer.data)
			else:
				return errorMessage("Score type does not exists.")
		except Exception as e:
			return exception(e)

class ScoresViewset(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]

	def list(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			obj = Scores.objects.filter(organization=user_organization.id)
			serializer = ScoresSerializers(obj, many=True)
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
			if not 'complexity_level' in request.data:
				return errorMessage("Complexity level is required.")
			complexity_level = request.data.get('complexity_level')

			if not 'score_type' in request.data:
				return errorMessage("Score type is required.")
			score_type = request.data.get('score_type')

			if Scores.objects.filter(organization=user_organization.id, is_active=True, complexity_level=complexity_level, score_type=score_type).exists():
				return errorMessage("Already have data on this complexity_level")

			serializer = ScoresSerializers(data=request.data)
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
			if Scores.objects.filter(pk=pk, organization=user_organization.id).exists():
				obj = Scores.objects.get(pk=pk)
				serializer = ScoresSerializers(obj, many=False)
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
			if Scores.objects.filter(pk=pk, organization=user_organization.id).exists():
				obj = Scores.objects.get(pk=pk)

				if not 'complexity_level' in request.data:
					return errorMessage("Complexity level is required.")
				complexity_level = request.data.get('complexity_level')

				if not 'score_type' in request.data:
					return errorMessage("Score type is required.")
				score_type = request.data.get('score_type')

				if Scores.objects.exclude(pk=pk).filter(organization=user_organization.id, is_active=True, complexity_level=complexity_level, score_type=score_type).exists():
					return errorMessage("Already have data on this complexity_level")

				serializer = ScoresSerializers(obj, data=request.data, partial=True)
				if serializer.is_valid():
					serializer.save()
					return successfullyUpdated(serializer.data)
				else:
					return serializerError(serializer.errors)
			else:
				return errorMessage("Score does not exist.")
		except Exception as e:
			return exception(e)

	def destroy(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			pk = self.kwargs['pk']
			if Scores.objects.filter(pk=pk, organization=user_organization.id).exists():
				obj = Scores.objects.get(pk=pk)
				obj.is_active=False
				obj.save()
				serializer = ScoresSerializers(obj, many=False)
				return success(serializer.data)
			else:
				return errorMessage("Score does not exists.")
		except Exception as e:
			return exception(e)

class ScoreGetDataView(generics.ListAPIView):

	def get_score_by_type(self, organization_id, score_type):
		# score = {'complexity_level':1, 'score':5, 'complexity_score':1, 'score_type':score_type}
		score_card = {
			1:{'complexity_level':1, 'score':5, 'complexity_score':1, 'score_type':score_type}, 
			2:{'complexity_level':2, 'score':5, 'complexity_score':2, 'score_type':score_type}, 
			3:{'complexity_level':3, 'score':5, 'complexity_score':3, 'score_type':score_type}, 
			4:{'complexity_level':4, 'score':5, 'complexity_score':4, 'score_type':score_type}, 
			5:{'complexity_level':5, 'score':5, 'complexity_score':5, 'score_type':score_type}
		}

		try:	
			
			scores = Scores.objects.filter(organization=organization_id, score_type=score_type, is_active=True)
			# print(scores)
			for score_data in scores:
				index = score_data.complexity_level
				if index in score_card:
					score_card[index]['score'] = score_data.score 
					score_card[index]['complexity_score'] = score_data.complexity_score
					score_card[index]['complexity_level'] = score_data.complexity_level
				
			return score_card
		except Exception as e:
			return score_card