from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from helpers.renderers import Renderer
from rest_framework.response import Response
from rest_framework import viewsets

import datetime

from .models import *
from organizations.models import Organization
from stages.models import Stages
from interviews.models import CandidateInterviews


from .serializers import *

from helpers.status_messages import *
from helpers.custom_permissions import *

from logs.views import UserLoginLogsViewset
from interviews.views import CandidateInterviewsViewset

from scores.models import Scores
from scores.views import ScoreGetDataView

class CandidateEvaluationViewset(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]

	

	def set_candidate_evaluation(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, candidate__organization=user_organization, is_active=True).exists():
				return errorMessage("Candidate job does not exist or inactive or not belongs to this organization.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			if not 'evaluation' in request.data:
				return errorMessage('Evaluation must be set.')

			#Check Stage
			stage = None
			if 'stage' in request.data:
				stage = CandidateInterviewsViewset().checkStage(request.data.get('stage'), user_organization.id)
				if stage.is_evaluation == False:
					return errorMessage("This stage has no evaluation process.")
				if stage is None:
					return errorMessage("Stage is not exist or match the organization")
			else:
				return errorMessage("Stage is necessary to start the evaluation process.")

			#Check if stage has interview and interview is completed
			if stage.is_interview:
				if not CandidateInterviews.objects.filter(stage=stage.id, candidate_job=candidate_job.id, is_active=True, is_completed=True).exists():
					return errorMessage("Candidate interview is not held, first interview the candidate and then process the evaluation form.")
				#TODO check if get has multi value then is it throw error or not
				candidate_interview = CandidateInterviews.objects.get(stage=stage.id, candidate_job=candidate_job.id, is_active=True, is_completed=True)
				request.data['evaluated_by'] = candidate_interview.interviewer.id
			else:
				if 'evaluated_by' not in request.data:
					return errorMessage("Evaluated by is required field.")
			
			#Process Candidate Job Stage Evaluation
			evaluation_stage = self.checkCandidateEvaluationStageStatus(stage, candidate_job)
			if evaluation_stage['status'] != 404 and evaluation_stage['status'] != 202:
				return errorMessage(evaluation_stage['message'])

			#Verify and check evaluation 
			evaluation = request.data.get('evaluation')
			if not Evaluations.objects.filter(pk=evaluation, is_active=True).exists():
				return errorMessage('Evaluation does not belongs to this organization or inactive or not found.')

			#TODO how to set the evaluation form, 
			#now the evaluation form id is sent by frontend.
			
			
			request.data['candidate'] = candidate_job.candidate.id
			request.data['candidate_job'] = candidate_job.id
			request.data['status'] = 2 # as we set the interview
			request.data['is_active'] = True
			

			serializer = CreateCandidateEvaluationsSerializers(data=request.data)
			if serializer.is_valid():
				serializer.status=2
				serializer.is_active = True
				serializer.save()
				return successfullyCreated(serializer.data)
			else:
				return serializerError(serializer.errors)


		except Exception as e:
			return exception(e)

	def list_candidate_evaluation(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, candidate__organization=user_organization, is_active=True).exists():
				return errorMessage("Candidate job does not exist or inactive or not belongs to this organization.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			candidate_evaluations = CandidateEvaluations.objects.filter(candidate_job=candidate_job.id, candidate__organization=user_organization)
			
			serializer = GetCandidateEvaluationsSerializers(candidate_evaluations, many=True)
			return success(serializer.data)

			# if request.user.id!=candidate_evaluation.evaluated_by:
			# 	return errorMessage("You have no access to evaluate the candidate.")

		except Exception as e:
			return exception(e)

	def get_by_stage_candidate_evaluation(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, candidate__organization=user_organization, is_active=True).exists():
				return errorMessage("Candidate job does not exist or inactive or not belongs to this organization.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			stage = self.kwargs['stage']

			if stage is not None:
				stage = CandidateInterviewsViewset().checkStage(stage, user_organization.id)
				if stage.is_evaluation == False:
					return errorMessage("This stage has no evaluation process.")
			else:
				return errorMessage("Stage is necessary to start the evaluation process.")

			if not CandidateEvaluations.objects.filter(stage=stage.id, candidate_job=candidate_job.id, is_active=True).exists():
				return errorMessage("Candidate evaluation stage does not exist.")

			candidate_evaluation = CandidateEvaluations.objects.filter(stage=stage.id, candidate_job=candidate_job.id, is_active=True).last()
			
			serializer = GetCandidateEvaluationsSerializers(candidate_evaluation, many=False)
			data = serializer.data
			
			if candidate_evaluation.is_completed:
				candidate_evaluation_questions = CandidateEvaluationQuestionRemarks.objects.filter(candidate_evaluation=candidate_evaluation.id, is_active=True)
				if candidate_evaluation_questions.exists():
					qserializer = ListCandidateEvaluationQuestionRemarksSerializers(candidate_evaluation_questions, many=True)
					data['evaluation_questions'] = qserializer.data
			
			return success(data)

		except Exception as e:
			return exception(e)

	def get_candidate_evaluation(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, candidate__organization=user_organization, is_active=True).exists():
				return errorMessage("Candidate job does not exist or inactive or not belongs to this organization.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			pk = self.kwargs['pk']
			if not CandidateEvaluations.objects.filter(pk=pk, candidate_job=candidate_job.id, is_active=True).exists():
				return errorMessage("Candidate evaluation does not exist or inactive.")
			candidate_evaluation = CandidateEvaluations.objects.get(pk=pk)
			
			serializer = GetCandidateEvaluationsSerializers(candidate_evaluation, many=False)
			return success(serializer.data)

			# if request.user.id!=candidate_evaluation.evaluated_by:
			# 	return errorMessage("You have no access to evaluate the candidate.")

		except Exception as e:
			return exception(e)

	def update_candidate_evaluation(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, candidate__organization=user_organization, is_active=True).exists():
				return errorMessage("Candidate job does not exist or inactive or not belongs to this organization.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			pk = self.kwargs['pk']
			if not CandidateEvaluations.objects.filter(pk=pk, candidate_job=candidate_job.id, is_active=True).exists():
				return errorMessage("Candidate evaluation does not exist or inactive.")
			candidate_evaluation = CandidateEvaluations.objects.get(pk=pk)
			if candidate_evaluation.is_start:
				return errorMessage("Candidate evaluation is already started.")
			if candidate_evaluation.stage is not None:
				if candidate_evaluation.stage.is_interview==False:
					if not 'evaluated_by' in request.data:
						return errorMessage("Evaluated by is required field.")

			if not 'evaluation' in request.data:
				return errorMessage('Evaluation must be set.')

			#Verify and check evaluation 
			evaluation = request.data.get('evaluation')
			if not Evaluations.objects.filter(pk=evaluation, is_active=True).exists():
				return errorMessage('Evaluation does not belongs to this organization or inactive or not found.')

			serializer = UpdateCandidateEvaluationsSerializers(candidate_evaluation, data=request.data)
			if serializer.is_valid():
				serializer.save()
				user_id=request.user.id
				action_name='Update candidate evaluation'
				id=candidate_job.id
				pk=pk
				output = self.candidate_job_action_logs(id,pk,action_name,user_id)
				if output['status'] == 400:
					return errorMessage(output['message'])
				return successfullyUpdated(serializer.data)
			else:
				return serializerError(serializer.errors)

			# if request.user.id!=candidate_evaluation.evaluated_by:
			# 	return errorMessage("You have no access to evaluate the candidate.")

		except Exception as e:
			return exception(e)

	def start_candidate_evaluation(self, request, *args, **kwargs):
		try:
			print('in start')
			data = {"candidate_evaluation":"", "evaluation_questions":""}
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, candidate__organization=user_organization, is_active=True).exists():
				return errorMessage("Candidate job does not exist or inactive or not belongs to this organization.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			pk = self.kwargs['pk']
			
			if not CandidateEvaluations.objects.filter(pk=pk, candidate_job=candidate_job.id, is_active=True).exists():
				return errorMessage("Candidate evaluation does not exist or inactive.")
			candidate_evaluation = CandidateEvaluations.objects.get(pk=pk)
			print(request.user.is_admin)
			if candidate_evaluation.is_completed:
				return errorMessage("Candidate evaluation is already completed.")
			
			if candidate_evaluation.evaluated_by is None:
				return errorMessage("Evaluated by is not set, please update the evaluation.")
        
			if request.user.id!=candidate_evaluation.evaluated_by.id and request.user.is_admin!=True:
				return errorMessage("You have no access to evaluate the candidate.")
			candidate_evaluation.is_start = True
			candidate_evaluation.start_date_time = datetime.datetime.now()
			candidate_evaluation.save()
			serializer = GetCandidateEvaluationsSerializers(candidate_evaluation, many=False)
			data['candidate_evaluation'] = serializer.data

			#Now process the evaluation questions
			print('in evaluation questions')
			evaluation_procedure_questions = EvaluationProcedureQuestions.objects.filter(evaluation=candidate_evaluation.evaluation.id, is_active=True)
			if not evaluation_procedure_questions.exists():
				return errorMessage("Evaluation has no questions, please contact to HR.")

			#Now first add the evaluation questions to candidate model
			question_data_array = []
			total_questions = len(evaluation_procedure_questions)
			question_added = 0
			
			for question in evaluation_procedure_questions:
				question_array = {
					"candidate_evaluation":candidate_evaluation.id,
					"evaluation_procedure_question":question.id,
					"is_active":True
				}
				if CandidateEvaluationQuestionRemarks.objects.filter(candidate_evaluation=candidate_evaluation.id, evaluation_procedure_question=question.id).exists():
					ceqr = CandidateEvaluationQuestionRemarks.objects.get(candidate_evaluation=candidate_evaluation.id, evaluation_procedure_question=question.id)
					serializer = CreateCandidateEvaluationQuestionRemarksSerializers(ceqr, data=question_array)
				else:
					serializer = CreateCandidateEvaluationQuestionRemarksSerializers(data=question_array)
				if serializer.is_valid():
					serializer.save()
					question_added += 1
				question_data_array.append(question_array)

			if total_questions==question_added:
				message = "All questions added successfully."
			else:
				message = "Out of "+str(total_questions)+" questions "+str(question_added)+" added."

			candidate_evaluation_questions = CandidateEvaluationQuestionRemarks.objects.filter(candidate_evaluation=candidate_evaluation.id, is_active=True)
			if candidate_evaluation_questions.exists():
				qserializer = ListCandidateEvaluationQuestionRemarksSerializers(candidate_evaluation_questions, many=True)
				data['evaluation_questions'] = qserializer.data
			else:
				return errorMessage("Please try again, not to get the questions.")
			
			user_id=request.user.id
			action_name='Start candidate evaluation'
			id=candidate_job.id
			pk=pk
			output = self.candidate_job_action_logs(id,pk,action_name,user_id)
			
			if output['status'] == 400:
				return errorMessage(output['message'])

			return success(data)

		except Exception as e:
			return exception(e)

	def detail_candidate_evaluation(self, request, *args, **kwargs):
		try:
			
			data = {"candidate_evaluation":"", "evaluation_questions":""}
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, candidate__organization=user_organization, is_active=True).exists():
				return errorMessage("Candidate job does not exist or inactive or not belongs to this organization.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			pk = self.kwargs['pk']
			
			if not CandidateEvaluations.objects.filter(pk=pk, candidate_job=candidate_job.id).exists():
				return errorMessage("Candidate evaluation does not exist.")
			candidate_evaluation = CandidateEvaluations.objects.get(pk=pk)
			
			serializer = GetCandidateEvaluationsSerializers(candidate_evaluation, many=False)
			data['candidate_evaluation'] = serializer.data

			#Now process the evaluation questions
			
			candidate_evaluation_questions = CandidateEvaluationQuestionRemarks.objects.filter(candidate_evaluation=candidate_evaluation.id, is_active=True)
			if candidate_evaluation_questions.exists():
				qserializer = ListCandidateEvaluationQuestionRemarksSerializers(candidate_evaluation_questions, many=True)
				data['evaluation_questions'] = qserializer.data
			
			return success(data)

		except Exception as e:
			return exception(e)

	def submit_candidate_evaluation(self, request, *args, **kwargs):
		try:
			data = {"candidate_evaluation":"", "evaluation_questions":""}
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, candidate__organization=user_organization, is_active=True).exists():
				return errorMessage("Candidate job does not exist or inactive or not belongs to this organization.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			pk = self.kwargs['pk']
			if not CandidateEvaluations.objects.filter(pk=pk, candidate_job=candidate_job.id, is_active=True).exists():
				return errorMessage("Candidate evaluation does not exist or inactive.")
			candidate_evaluation = CandidateEvaluations.objects.get(pk=pk)
			if candidate_evaluation.is_completed:
				return errorMessage("Candidate evaluation is already completed.")

			if request.user.id!=candidate_evaluation.evaluated_by.id and request.user.is_admin!=True:
				return errorMessage("You have no access to evaluate the candidate.")

			evaluation_questions_remarks = request.data.get('evaluation_questions_remarks') or None
			evaluation_questions_remarks_result = self.candidate_evaluation_questions_remarks(candidate_evaluation, evaluation_questions_remarks)

			#Return if not processed or error occurs.
			if evaluation_questions_remarks_result['status']==400 or evaluation_questions_remarks_result['status']==404:
				return errorMessage(evaluation_questions_remarks_result['message'])

			# Mark it as completed if all questions are updated successfully
			if evaluation_questions_remarks_result['status'] == 200:
				candidate_evaluation.is_completed = True
				candidate_evaluation.save()
			#TODO how to calculate the score of evaluation
			serializer = SubmitCandidateEvaluationsSerializers(candidate_evaluation, data=request.data)
			if serializer.is_valid():
				serializer.save()

				user_id=request.user.id
				action_name='Submit candidate evaluation'
				id=candidate_job.id
				pk=pk
				output = self.candidate_job_action_logs(id,pk,action_name,user_id)
				if output['status'] == 400:
					return errorMessage(output['message'])
				
				return successfullyUpdated(serializer.data)
			else:
				return serializerError(serializer.errors)
			
			


		except Exception as e:
			return exception(e)

	def cancel_candidate_evaluation(self, request, *args, **kwargs):
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
			if not CandidateEvaluations.objects.filter(pk=pk, candidate_job=candidate_job.id, is_active=True).exists():
				return errorMessage("Candidate evaluation does not exist or inactive.")
			candidate_evaluation = CandidateEvaluations.objects.get(pk=pk)
			if candidate_evaluation.is_completed:
				return errorMessage("Candidate evaluation is already completed.")

			if request.user.id!=candidate_evaluation.evaluated_by.id and request.user.is_admin!=True:
				return errorMessage("You have no access to evaluate the candidate.")
			if not 'reason_for_cancel' in request.data:
				return errorMessage("Reason for cancel is required field.")

			request.data['cancel_date_time'] = datetime.datetime.now()
			request.data['is_completed'] = False
			request.data['is_cancel'] = True
			request.data['is_active'] = False
			request.data['cancel_by'] = request.user.id
			

			serializer = CancelCandidateEvaluationsSerializers(candidate_evaluation, data=request.data)
			if serializer.is_valid():
				# candidate_evaluation.is_completed = False
				# candidate_evaluation.is_cancel = True
				# candidate_evaluation.is_active = False
				# candidate_evaluation.cancel_by = request.user
				# candidate_evaluation.cancel_date_time = datetime.datetime.now()
				# candidate_evaluation.save()
				serializer.save()

				user_id=request.user.id
				action_name='Cancle candidate evaluation'
				id=candidate_job.id
				pk=pk
				output = self.candidate_job_action_logs(id,pk,action_name,user_id)
				if output['status'] == 400:
					return errorMessage(output['message'])

				

				return successMessage("Successfully cancel the candidate evaluation.")
			else:
				return serializerError(serializer.errors)

		except Exception as e:
			return exception(e)

	def recheck_candidate_evaluation(self, request, *args, **kwargs):
		try:
			user_organization = UserLoginLogsViewset().userOrganization(request.user)
			if user_organization is None:
				return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

			#Process the candidate job uuid
			candidate_job_uuid = self.kwargs['uuid']
			if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, candidate__organization=user_organization, is_active=True).exists():
				return errorMessage("Candidate job does not exist or inactive or not belongs to this organization.")
			candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

			pk = self.kwargs['pk']
			if not CandidateEvaluations.objects.filter(pk=pk, candidate_job=candidate_job.id, is_active=True).exists():
				return errorMessage("Candidate evaluation does not exist or inactive.")
			candidate_evaluation = CandidateEvaluations.objects.get(pk=pk)
			if not candidate_evaluation.is_completed:
				return errorMessage("Candidate evaluation is not completed, already mark as rechecked or complete it first.")

			if request.user.id!=candidate_evaluation.evaluated_by.id and request.user.is_admin!=True:
				return errorMessage("You have no access to evaluate the candidate.")

			candidate_evaluation.is_rechecked = True
			candidate_evaluation.save()
			user_id=request.user.id
			action_name='Rechecked candidate evaluation'
			id=candidate_job.id
			pk=pk
			output = self.candidate_job_action_logs(id,pk,action_name,user_id)
			if output['status'] == 400:
					return errorMessage(output['message'])
			return successMessage("Successfully rechecked the candidate evaluation.")
			

		except Exception as e:
			return exception(e)

	def mark_as_done_candidate_evaluation(self, request, *args, **kwargs):
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
			if not CandidateEvaluations.objects.filter(pk=pk, candidate_job=candidate_job.id, is_active=True).exists():
				return errorMessage("Candidate evaluation does not exist or inactive.")
			candidate_evaluation = CandidateEvaluations.objects.get(pk=pk)
			if not candidate_evaluation.is_rechecked:
				return errorMessage("Candidate evaluation is not completed, already mark as done or recheck it.")

			if request.user!=candidate_evaluation.evaluated_by:
				return errorMessage("You have no access to evaluate the candidate.")

			candidate_evaluation.is_mark_done = True
			candidate_evaluation.save()
			return successMessage("Successfully mark as done the candidate evaluation.")
			
			
		except Exception as e:
			return exception(e)

	def checkCandidateEvaluationStageStatus(self, stage, candidate_job):
		result = {"status":200, "data":"", "message":"Already has candidate evaluation active stage data."}
		try:
			candidate_stage_evaluations = CandidateEvaluations.objects.filter(stage=stage.id, candidate_job=candidate_job.id)
			if not candidate_stage_evaluations.exists():
				#Has not data against this stage
				result['status'] = 404
				result['message'] = "candidate has no current stage evaluation."
				return result
			# Now checks for the Evaluation stages. 
			# First check if stage has successfully completed
			if candidate_stage_evaluations.filter(is_active=True).exists():
				#return with complete stage result
				data = candidate_stage_evaluations.filter(is_active=True).last()
				result['data'] = data
				return result
			else:
				result['status'] = 202
				result['message'] = "Have no active stage."
				return result
			# if not CandidateEvaluations.objects.filter(stage=stage.id, candidate_job=candidate_job.id).exists():

		except Exception as e:
			result['status'] = 400
			print(str(e))
			result['message'] = "Have exception errors."
			return result

	def candidate_evaluation_questions_remarks(self, candidate_evaluation, candidate_evaluation_questions):
		ceq_errors = []
		evaluation_questions = []
		response = {'status':200, 'message': '', 'question_errors': ''}

		if isinstance(candidate_evaluation_questions, str):
			candidate_evaluation_questions = json.loads(candidate_evaluation_questions)
			evaluation_questions.append(candidate_evaluation_questions)
		else:
			evaluation_questions = candidate_evaluation_questions

		scores = ScoreGetDataView().get_score_by_type(candidate_evaluation.candidate.organization.id, 2)
		
		total_marks = 0 
		total_marks_obtained = 0

		try:
			candidate_evaluation_question_array = {'candidate_evaluation': '', 'complexity_level':'',  'score': '', 'comment': ''}
			if evaluation_questions is not None:
				for ce_question in evaluation_questions:
					candidate_evaluation_question_array['candidate_evaluation'] = candidate_evaluation.id
					marks = None 
					complexity_level = None
					if 'score' in ce_question:
						candidate_evaluation_question_array['score'] = int(ce_question['score'])
						score = int(ce_question['score'])
					if 'complexity_level' in ce_question:
						candidate_evaluation_question_array['complexity_level'] = int(ce_question['complexity_level'])
						complexity_level = int(ce_question['complexity_level'])
					if 'comment' in ce_question:
						candidate_evaluation_question_array['comment'] = ce_question['comment']

					if CandidateEvaluationQuestionRemarks.objects.filter(pk=ce_question['id'], candidate_evaluation=candidate_evaluation.id, is_active=True).exists():
						ceq_obj = CandidateEvaluationQuestionRemarks.objects.get(pk=ce_question['id'], is_active=True)

						if complexity_level is not None:
							if complexity_level in scores:
								marks = scores[complexity_level]['score']*scores[complexity_level]['complexity_score']
								candidate_evaluation_question_array['score'] = round(marks,2)
							else:
								candidate_evaluation_question_array['score'] = 1
								complexity_level = 1

						elif score is not None:
							if score in scores:
								marks = scores[score]['score']*scores[score]['complexity_score']
								candidate_evaluation_question_array['score'] = round(marks,2)
								candidate_evaluation_question_array['complexity_level'] = score

						if marks is not None:
							total_marks_obtained += marks
							total_marks += scores[5]['score']*scores[5]['complexity_score']

						
						ceq_serializer = SubmitCandidateEvaluationQuestionRemarksSerializers(ceq_obj, data=candidate_evaluation_question_array, partial=True)
						if ceq_serializer.is_valid():
							ceq_serializer.save()
						else:
							ceq_errors.append(ceq_serializer.errors)
					else:
						ceq_errors.append("Evaluation question does not exist")

				

				if (len(evaluation_questions) == len(ceq_errors)):
					response['status'] = 400
					response['message'] = "No evaluation question remarks are processed, please update it again!"
				elif len(ceq_errors) > 0:
					response['status'] = 202
					response['message'] = "Some of the evaluation question remarks are not processed, please update it again!"
				else:
					candidate_evaluation.total_marks = total_marks
					candidate_evaluation.total_marks_obtained = total_marks_obtained
					candidate_evaluation.save()
					response['status'] = 200
					response['message'] = "All evaluation questions remarks data are processed Successfully."

			else:
				response['status'] = 404
				response["message"] = "No evaluation questions remarks found."
				ceq_errors.append("No evaluation questions remarks found.")

		except Exception as e:
			response['status'] = 404
			print(str(e))
			response['message'] = "Evaluation question remarks process through error, please update it again!"
			ceq_errors.append("Evaluation question remarks process has error({})".format(str(e)))

		response['question_errors'] = ceq_errors
		return response
	
	def candidate_evaluation_action_log(self,request,*args, **kwargs):
		try:
			candidate_job_uuid = self.kwargs['uuid']
			pk = self.kwargs['pk']
			query=CandidateJobActionLogs.objects.filter(candidate_job__uuid=candidate_job_uuid,candidate_evaluation=pk,is_active=True)
			if not query.exists():
				return errorMessage("Not data found")
			
			serializer=CandidateJobActionLogs(query,many=True)

			return successMessageWithData('Success',serializer.data)
        
		except Exception as e:
			return exception(e)
	
	def candidate_job_action_logs(self,id,pk,action_name, user_id):
		try:
			result = {
				'status': 400, 
				'data':[],
				'message': '', 
				'system_error_message': ''
			}
			
			data = {
				"candidate_job": id,
				"candidate_evaluation":pk,
				"title": action_name,
				"action_by": user_id,
			}
			
			serializer = CandidateJobActionLogs(data=data)
			if not serializer.is_valid():
				result['message'] = serializer.errors
				return result
			
			serializer.save()

			result['status'] = 200
			result['data'] = serializer.data

			return result

		except Exception as e:
			return exception(e)



