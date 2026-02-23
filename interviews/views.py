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
from django.db.models import Q
from candidates.models import CandidateJobs
from evaluations.models import CandidateEvaluations

from helpers.status_messages import *
from helpers.custom_permissions import *

from logs.views import UserLoginLogsViewset
from employees.models import Employees
import datetime


class InterviewModeViewset(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]

	def list(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			obj = InterviewMode.objects.filter(organization=user_organization.id)
			serializer = InterviewModeSerializers(obj, many=True)
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

			serializer = InterviewModeSerializers(data=request.data)
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
			if InterviewMode.objects.filter(pk=pk, organization=user_organization.id).exists():
				obj = InterviewMode.objects.get(pk=pk)
				serializer = InterviewModeSerializers(obj, many=False)
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
			if InterviewMode.objects.filter(pk=pk, organization=user_organization.id).exists():
				obj = InterviewMode.objects.get(pk=pk)
				serializer = InterviewModeSerializers(obj, data=request.data, partial=True)
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
			if InterviewMode.objects.filter(pk=pk, organization=user_organization.id).exists():
				obj = InterviewMode.objects.get(pk=pk)
				obj.is_active=False
				obj.save()
				serializer = InterviewModeSerializers(obj, many=False)
				return success(serializer.data)
		except Exception as e:
			return exception(e)


class CandidateInterviewsViewset(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]
	#TODO 1 Cancel Re-schedule Interview
	#Done 2 Cancel Interview Stage 
	#TODO 3 Re-schedule Interview Stage
	#TODO 4 View Evaluation Score in list
	#TODO 5 Active the evaluation process

	def list(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid).exists():
				return errorMessage("Candidate job does not exist.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			obj = CandidateInterviews.objects.filter(candidate_job=candidate_job.id).order_by('id')
			
			serializer = GetCandidateInterviewsSerializers(obj, many=True)
			return success(serializer.data)

		except Exception as e:
			return exception(e)

	def create(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, is_active=True).exists():
				return errorMessage("Candidate job does not exist or inactive.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			#Check Stage
			stage = None
			if 'stage' in request.data:
				stage = self.checkStage(request.data.get('stage'), user_organization.id)
				
				if stage is None:
					return errorMessage("Stage is not exist or match the organization")
				elif stage.is_interview==False:
					return errorMessage("This stage has no interview.")
			else:
				return errorMessage("Stage is necessary to set the interview.")

			#TODO check interviewer 
			interviewer = None
			if 'interviewer' in request.data:
				if not Employees.objects.filter(hrmsuser=request.data.get('interviewer'), is_active=True).exists():
					return errorMessage("Interviewer is inactive or does not exists.")
			else:
				return errorMessage("Interviewer is necessary to set the interview.")


			#Process Candidate Job Interview Stage
			interview_stage = self.checkCandidateInterviewStageStatus(stage, candidate_job)
			if interview_stage['status'] == 200:
				serializer = GetCandidateInterviewsSerializers(interview_stage['data'], many=False)
				# serializer = GetCandidateInterviewsSerializers(candidate_interview, many=False)
				return success(serializer.data)
			if interview_stage['status'] != 404 and interview_stage['status'] != 202:
				# print(interview_stage['data'])
				return errorMessage(interview_stage['message'])

			request.data['candidate'] = candidate_job.candidate.id
			request.data['candidate_job'] = candidate_job.id
			request.data['status'] = 2 # as we set the interview
			request.data['is_active'] = True

			serializer = CandidateInterviewsSerializers(data=request.data)
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

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid).exists():
				return errorMessage("Candidate job does not exist.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			pk = self.kwargs['pk']
			if not CandidateInterviews.objects.filter(pk=pk, candidate_job=candidate_job.id).exists():
				return errorMessage("Candidate interview stage does not exist.")

			candidate_interview = CandidateInterviews.objects.get(pk=pk)
			serializer = GetCandidateInterviewsSerializers(candidate_interview, many=False)
			return success(serializer.data)



		except Exception as e:
			return exception(e)

	def get_by_stage(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid).exists():
				return errorMessage("Candidate job does not exist.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			stage = self.kwargs['stage']

			#Check Stage
			
			if stage is not None:
				stage = self.checkStage(stage, user_organization.id)
				
				if stage is None:
					return errorMessage("Stage is not exist or match the organization")
				elif stage.is_interview==False:
					
					return errorMessage("This stage has no interview.")
			else:
				return errorMessage("Stage is necessary to set the interview.")

			if not CandidateInterviews.objects.filter(stage=stage.id, candidate_job=candidate_job.id, is_active=True).exists():
				return errorMessage("Candidate interview stage does not exist.")

			candidate_interview = CandidateInterviews.objects.get(stage=stage.id, candidate_job=candidate_job.id, is_active=True)
			serializer = GetCandidateInterviewsSerializers(candidate_interview, many=False)
			return success(serializer.data)



		except Exception as e:
			return exception(e)

	def partial_update(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, is_active=True).exists():
				return errorMessage("Candidate job does not exist or inactive.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			pk = self.kwargs['pk']
			if not CandidateInterviews.objects.filter(pk=pk, candidate_job=candidate_job.id, is_active=True).exists():
				return errorMessage("Has no access to update the interview or not found.")
			#TODO candidate has no more than 1 interview stage in active form
			candidate_interview = CandidateInterviews.objects.get(pk=pk)
			
			if candidate_interview.status!=1 and candidate_interview.status!=2:
				return errorMessage("Candidate interview is not to be update.")

			serializer = UpdateCandidateInterviewsSerializers(candidate_interview, data=request.data, partial=True)
			if serializer.is_valid():
				serializer.save()
				return successfullyUpdated(serializer.data)
			else:
				return serializerError(serializer.errors)


		except Exception as e:
			return exception(e)

	def start_candidate_interview(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, is_active=True).exists():
				return errorMessage("Candidate job does not exist or inactive.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			pk = self.kwargs['pk']
			if not CandidateInterviews.objects.filter(pk=pk, candidate_job=candidate_job.id, is_active=True).exists():
				return errorMessage("Has no access to update the interview or not found.")
			#TODO candidate has no more than 1 interview stage in active form
			candidate_interview = CandidateInterviews.objects.get(pk=pk)
			if candidate_interview.status!=2 and candidate_interview.start_date_time is not None:
				return errorMessage("Candidate interview is already started or in other statge.")

			cci_array = {"start_date_time":datetime.datetime.now(), "status":3}
			

			serializer = StartCandidateInterviewsSerializers(candidate_interview, data=cci_array, partial=True)
			if serializer.is_valid():
				serializer.save()
				#TODO Add data to log
				return successMessage("Successfully start the candidate interview.")
			else:
				return serializerError(serializer.errors)

		except Exception as e:
			return exception(e)

	def cancel_candidate_interview(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, is_active=True).exists():
				return errorMessage("Candidate job does not exist or inactive.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			pk = self.kwargs['pk']
			if not CandidateInterviews.objects.filter(pk=pk, candidate_job=candidate_job.id, is_active=True).exists():
				return errorMessage("Has no access to update the interview or not found.")
			#TODO candidate has no more than 1 interview stage in active form
			candidate_interview = CandidateInterviews.objects.get(pk=pk)
			if candidate_interview.status==4 and candidate_interview.complete_date_time is not None:
				return errorMessage("Candidate interview is not to be cancel.")

			if 'reason_for_cancel' in request.data:
				request.data['is_cancel'] = True
				request.data['is_active'] = False
				request.data['status'] = 5
			else:
				return errorMessage("Reason is necessary.")


			serializer = CancelCandidateInterviewsSerializers(candidate_interview, data=request.data, partial=True)
			if serializer.is_valid():
				serializer.save()
				#TODO if user want to reschedule then add the data for next schedule the interview
				return successfullyUpdated(serializer.data)
			else:
				return serializerError(serializer.errors)

		except Exception as e:
			return exception(e)

	def mark_complete_candidate_interview(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, is_active=True).exists():
				return errorMessage("Candidate job does not exist or inactive.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			pk = self.kwargs['pk']
			if not CandidateInterviews.objects.filter(pk=pk, candidate_job=candidate_job.id, is_active=True).exists():
				return errorMessage("Has no access to update the interview or not found.")
			#TODO candidate has no more than 1 interview stage in active form
			candidate_interview = CandidateInterviews.objects.get(pk=pk)
			if candidate_interview.status!=3 and candidate_interview.start_date_time is None:
				return errorMessage("First you have to start the interview to mark it complete.")

			#TODO update the log for this
			cci_array = {"is_completed":True, "complete_date_time":datetime.datetime.now(), "status":4}

			serializer = CompleteCandidateInterviewsSerializers(candidate_interview, data=cci_array, partial=True)
			if serializer.is_valid():
				serializer.save()
				#TODO if user want to reschedule then add the data for next schedule the interview
				return successfullyUpdated(serializer.data)
			else:
				return serializerError(serializer.errors)

		except Exception as e:
			return exception(e)

	def reschedule_candidate_interview(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, is_active=True).exists():
				return errorMessage("Candidate job does not exist or inactive.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)


			
			#Check Stage
			stage = None
			if 'stage' in request.data:
				stage = self.checkStage(request.data.get('stage'), user_organization.id)
				if stage is None:
					return errorMessage("Stage is not exist or match the organization")
				elif stage.is_interview==False:
					return errorMessage("This stage has no interview.")
			else:
				return errorMessage("Stage is necessary to reschedule the interview.")

			interviewer = None
			if 'interviewer' in request.data:
				if not HrmsUsers.objects.filter(pk=request.data.get('interviewer'), is_active=True).exists():
					return errorMessage("Interviewer is inactive or does not exists.")
			else:
				return errorMessage("Interviewer is necessary to set the interview.")

			pk = int(self.kwargs['pk'])
			
			print('reschedule')

			if CandidateInterviews.objects.filter(stage=stage.id, candidate_job=candidate_job.id, is_active=True).exists():
				
				candidate_interviews = CandidateInterviews.objects.filter(stage=stage.id, candidate_job=candidate_job.id, is_active=True)
				
				for candidate_interview in candidate_interviews:
					candidate_interview.is_active = False
					candidate_interview.is_reschedule = True
					candidate_interview.reschedule_date = datetime.datetime.now()
					candidate_interview.save()

				print('inactive the candidate interview')
					
			#Inactive the interview evaluation
			print('evaluations')
			if CandidateEvaluations.objects.filter(stage=stage.id, candidate_job=candidate_job.id, is_active=True).exists():
				print('has evaluations')
				candidate_evaluations = CandidateEvaluations.objects.filter(stage=stage.id, candidate_job=candidate_job.id, is_active=True)
				print(len(candidate_evaluations))
				for candidate_evaluation in candidate_evaluations:
					candidate_evaluation.is_active = False
					candidate_evaluation.save()

				print('save the inactive state of candidate_evaluations')

			#Process Candidate Job Interview Stage
			interview_stage = self.checkCandidateInterviewStageStatus(stage, candidate_job)
			if interview_stage['status'] != 404 and interview_stage['status'] != 202:
				return errorMessage(interview_stage['message'])

			request.data['candidate'] = candidate_job.candidate.id
			request.data['candidate_job'] = candidate_job.id
			request.data['status'] = 2 # as we set the interview
			request.data['is_active'] = True

			#TODO email the candidate or team lead
			print('request')
			print(request.data)

			serializer = CandidateInterviewsSerializers(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return successfullyCreated(serializer.data)
			else:
				print(serializer.errors)
				return serializerError(serializer.errors)	
			

		except Exception as e:
			return exception(e)

	def checkStage(self, stage_id, organization_id):
		try:
			if Stages.objects.filter(id=stage_id, organization=organization_id, is_active=True).exists():
				stage = Stages.objects.get(id=stage_id)
				return stage
			else:
				return None
		except Exception as e:
			return None

	def checkCandidateInterviewStageStatus(self, stage, candidate_job):
		result = {"status":200, "data":"", "message":"Already has candidate interview active stage data."}
		try:
			candidate_stage_interviews = CandidateInterviews.objects.filter(stage=stage.id, candidate_job=candidate_job.id)
			if not candidate_stage_interviews.exists():
				#Has not data against this stage
				result['status'] = 404
				result['message'] = "Has no candidate interview current stage."
				return result
			# Now checks for the interview stages. 
			# First check if stage has successfully completed
			if candidate_stage_interviews.filter(is_active=True).exists():
				#return with complete stage result
				data = candidate_stage_interviews.filter(is_active=True).last()
				result['data'] = data
				return result
			else:
				result['status'] = 202
				result['message'] = "Have no active stage."
				return result
			# if not CandidateInterviews.objects.filter(stage=stage.id, candidate_job=candidate_job.id).exists():

		except Exception as e:
			result['status'] = 400
			print(str(e))
			result['message'] = "Have exception errors."
			return result

  
    # Interviewer functions
	def get_upcoming_interviews(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
			current_date = datetime.datetime.today().date()
			upcoming_interviews_data=[]
			previous_interviews_data=[]
			upcoming_interviews = CandidateInterviews.objects.filter(interviewer=request.user.id,is_active=True).order_by('id')
			# print(upcoming_interviews.values)
			for result in upcoming_interviews:
				query=upcoming_interviews.filter(interview_date__gte=current_date,is_active=True)
				if query.exists():
					upcoming_interviews_data.append(result)
				else:
					previous_interviews_data.append(result)

			serializer_upcoming_interviews = GetCandidateInterviewsSerializers(upcoming_interviews_data, many=True).data
			serializer_previous_interviews = GetCandidateInterviewsSerializers(previous_interviews_data, many=True).data
			data={
            "upcoming_interviews":serializer_upcoming_interviews,
			"previous_interviews":serializer_previous_interviews
			}

			return success(data)

		except Exception as e:
			return exception(e)

	def get_today_interviews(self,request,*args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
			current_date = datetime.datetime.today().date()
			upcoming_interviews_data=[]
			upcoming_interviews = CandidateInterviews.objects.filter(interviewer=request.user.id,interview_date=current_date,is_active=True).order_by('id')
			for result in upcoming_interviews:
				query=CandidateEvaluations.objects.filter(candidate=result.candidate,candidate_job=result.candidate_job,is_completed=False,is_active=True)
				if query.exists():
					upcoming_interviews_data.append(result)

			serializer_upcoming_interviews = GetCandidateInterviewsSerializers(upcoming_interviews_data, many=True).data

			return success(serializer_upcoming_interviews)

		except Exception as e:
			return exception(e)



class PreInterviewDataView(generics.ListAPIView):

	def pre_data_mode(self, organization_id):
		try:
			data = InterviewMode.objects.filter(is_active=True, organization=organization_id)
			serializers = PreDataInterviewModeSerializers(data, many=True)
			return serializers.data
		except Exception as e:
			return []
		
class InterviewMediumViewSet(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]
	queryset = InterviewMedium.objects.all()
	serializer_class = InterviewMediumSerializer

	def create(self,request,*args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			if "title" not in request.data:
				return errorMessage("title is required field")
			
			request.data['organization']=user_organization.id

			serializer=InterviewMediumSerializer(data=request.data)
			
			if not serializer.is_valid():
				return errorMessage(serializer.errors)
			
			serializer.save()
			
			return success(serializer.data)

		except Exception as e:
			return exception(e)
		
	def list(self,request,*args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
			query=InterviewMedium.objects.filter(organization=user_organization.id,is_active=True)

			serializer=InterviewMediumSerializer(query,many=True)

			return successMessageWithData("Success",serializer.data)

		except Exception as e:
			return exception(e)

