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
from jobs.serializers import JobListPostSerializers, JobTypesSerializers
from candidates.serializers import ListCandidateJobsDataSerializers, ListCandidateJobsSerializers
from helpers.status_messages import *
from helpers.custom_permissions import CheckUserOrganization
from helpers.get_org import userOrganizationChecks
import re
from django.db.models import Q
import datetime

import io, csv, pandas as pd

from scores.models import Scores
from helpers.decode_token import decodeToken
from scores.views import ScoreGetDataView


class AssessmentTypesViewset(viewsets.ModelViewSet):
    queryset = AssessmentTypes.objects.filter(is_active=True)
    serializer_class = AssessmentTypesSerializers
    permission_classes = [IsAuthenticated]



    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if AssessmentTypes.objects.filter(id=pk).exists():
                obj = AssessmentTypes.objects.get(id=pk)
                if obj.is_active == False:
                    msg = "Assessment Type is already deactivated"
                    return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
                obj.is_active = False
                obj.save()
                serializer = JobTypesSerializers(obj)
                return success(serializer.data)
            else:
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This Assessment type does not exists', 'system_status_message': ''})
        except Exception as e:
            return exception(e)

class AssessmentTestsViewset(viewsets.ModelViewSet):
	queryset = AssessmentTests.objects.filter(is_active=True)
	serializer_class = AssessmentTestsSerializers
	permission_classes = [IsAuthenticated]

	def destroy(self, request, *args, **kwargs):
		try:
			pk = self.kwargs['pk']
			if AssessmentTests.objects.filter(id=pk).exists():
				obj = AssessmentTests.objects.get(id=pk)
				if obj.is_active == False:
					msg = "Assessment Test is already deactivated"
					return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
				obj.is_active = False
				obj.save()
				serializer = JobTypesSerializers(obj)
				return success(serializer.data)
			else:
				return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This Assessment test does not exists', 'system_status_message': ''})
		except Exception as e:
			return exception(e)

class AssessmentTestFilesViewset(viewsets.ModelViewSet):
	queryset = AssessmentTestFiles.objects.filter(is_active=True)
	serializer_class = AssessmentTestFiles
	permission_classes = [IsAuthenticated, CheckUserOrganization]

	def create(self, request, *args, **kwargs):
		try:
			
			position_id = request.data.get('position')
			assessment_type_id = request.data.get('assessment_type')
			
			if assessment_type_id is None:
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Assessment type does not exists.', 'system_error_message': ''})
			#TODO assessment type by organization 
			organization = Organization.objects.filter(user__id=request.user.id, is_active=True).first()
			if not AssessmentTypes.objects.filter(id=assessment_type_id).exists():
				return errorMessage('Assessment type does not exist')
			assessment_type = AssessmentTypes.objects.get(id = assessment_type_id)
			
			if assessment_type.is_technical==True:
				if position_id is None:
					# position is empty 
					return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Position does not exists.', 'system_error_message': ''})
				
				position = Positions.objects.filter(id=position_id, is_active=True)
				if position.exists():
					if not position.filter(staff_classification__organization__id=organization.id).exists():
						return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'organization has no active position or position does not belongs to this organization.', 'system_error_message': ''})
				else:
					return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Position does not exists or inactive.', 'system_error_message': ''})
			else:
				position_id = None
				
				
			# check if assessment test exist or not
			
			assessment_test_data = self.checkAssessmentTest(assessment_type, organization.id, position_id)
			
			if assessment_test_data['status'] == 400:
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': assessment_test_data['message'], 'system_error_message': ''})
			assessment_test = assessment_test_data['data']
			
			# First in active all the assessment files belongs to that assessment test.
			atf_data = AssessmentTestFiles.objects.filter(assessment_test=assessment_test.id, is_active=True)
			if atf_data.exists():
				if atf_data.count() > 0:
					for x in atf_data:
						atf = AssessmentTestFiles.objects.get(id=x.id)
						atf.is_active = False
						atf.save()

			
			# Process the assessment test file.
			request.data['assessment_test'] = assessment_test.id
			request.data['uploaded_by'] = request.user.id
			# print(request.data)
			serializer = CUAssessmentTestFilesSerializers(data = request.data)
			file_columns = ['s.#', 'question', 'option1', 'option2', 'option3', 'option4', 'option5', 'option6', 'option7', 'option8', 'answer', 'complexity_level', 'total_options', 'clevel', 'time']
			file_col_index = {
				's.#': None, 'question': None, 'option1': None, 'option2': None,
				'option3': None, 'option4': None, 'option5': None, 'option6': None, 'option7': None, 'option8': None,  'answer': None, 
				'clevel': None, 'time': None, 'complexity_level': 1, 'total_options': 1
			}
			if serializer.is_valid():
				afile = serializer.save()
				file = afile.assessment_file
				reader = pd.read_csv(file)
				
				for i,col in enumerate(reader.columns):
					if col.lower() in file_columns:
						file_col_index[col.lower()] = i

				options_array = []
				
				question_array = {'question':'', 'assessment_test_file':afile.id, 'answer_option':'', 'answer':'', 'complexity_level':'', 'clevel':'', 'time':''}
				for row in reader.iterrows():
					
					if file_col_index['question'] is not None:
						
						total_options = int(row[1][file_col_index['total_options']])+1
						options_array = []
						if total_options>0:
							for i in range(1,total_options):
								op_value = 'option'+str(i)
								options_array.append(op_value)
						else:
							options_array = ['option1']

						
						question_array['question'] = row[1][file_col_index['question']]
						
						answer_option = int(re.search(r'\d+', str(row[1][file_col_index['answer']])).group())
						
						question_array['answer'] = row[1][file_col_index['option'+str(answer_option)]]
						
						question_array['answer_option'] = answer_option
						
						# question_array['clevel'] = row[1][file_col_index['clevel']]
						question_array['complexity_level'] = row[1][file_col_index['complexity_level']]
						question_array['total_options'] = row[1][file_col_index['total_options']]
						question_array['time'] = row[1][file_col_index['time']]
						
						
						qserializer = CreateQuestionsSerializers(data=question_array)
						qoptions = []
						if qserializer.is_valid():
							question = qserializer.save()
							
							for option in options_array:
								if row[1][file_col_index[option]] is not None:
									
									qoptions_array = {'question':question.id, 'option':None, 'value':None}
									qoptions_array['option'] = int(re.search(r'\d+', option).group())
									qoptions_array['value'] = row[1][file_col_index[option]]
									
									qoptions.append(qoptions_array)
									# continue
									qoption = CreateQuestionOptionsSerializers(data=qoptions_array)
									if qoption.is_valid():
										options = qoption.save()
									else:
										#TODO process the options
										continue
							
						else:
							# log to save the not process the questions
							continue
						

					
				return Response({'status':200, 'system_status': 200, 'data': serializer.data, 'message': 'Successfully uploaded', 'system_error_message': ''})
			else:
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Validation Error', 'system_error_message': serializer.errors})

		except Exception as e:
			return exception(e)

	def checkAssessmentTest(self, assessment_type, organization_id, position):
		try:
			at_result = {'status': 200, 'data':'', 'message':'Successfully Updated'}
			at_array = {'assessment_type':assessment_type.id, 'organization':organization_id, 'position':position, 'is_active':True}
			is_exist = False
			if assessment_type.is_technical==True:
				assessment_test = AssessmentTests.objects.filter(assessment_type=assessment_type.id, organization=organization_id, position=position)
			else:
				assessment_test = AssessmentTests.objects.filter(assessment_type=assessment_type.id, organization=organization_id)
			# print(assessment_test)
			if assessment_test.exists():
				# assessment_test = AssessmentTests.objects.get(assessment_type=assessment_type.id, organization=organization_id, position=position)
				assessment_test = assessment_test.first()
				# print(assessment_test)
				print('exists')
				if assessment_test.is_active == True:
					is_exist = True
				else:
					# update the assessment test to active
					# print('update')
					serializer = CUAssessmentTestsSerializers(assessment_test, data = at_array)
			else:
				serializer = CUAssessmentTestsSerializers(data = at_array)

			if is_exist==True:
				at_result['data'] = assessment_test
			else:
				if serializer.is_valid():
					assessment_test = serializer.save()
					at_result['data'] = assessment_test
				else:
					at_result['status'] = 400
					at_result['message'] = 'Have error in procesing.'

		except Exception as e:
			at_result['status'] = 400
			at_result['message'] = str(e)

		return at_result

	def list(self, request, *args, **kwargs):
		try:
			assessment_tests = AssessmentTests.objects.filter(is_active=True)
			serializer = AssessmentTestsSerializers(assessment_tests, many=True)
			return success(serializer.data)
		except Exception as e:
			return exception(e)

class CandidateAssessmentTestViewset(viewsets.ModelViewSet):
	queryset = CandidateAssessmentTest.objects.filter(is_active=True)

	def checkCandidateElligiblility(self, request, *args, **kwargs):
		# candidate_uuid = self.kwargs['uuid']
		job_post_uuid = self.kwargs['post_uuid']
		job_post = None
		result = {'candidate_job_post':None, 'job_post':None, 'candidate_non_test':None, 'candidate_tech_test':None}
		
		try:
			if JobPosts.objects.filter(uuid=job_post_uuid).exists():
				job_post = JobPosts.objects.get(uuid=job_post_uuid)
				organization_id = job_post.job.staff_classification.organization.id
				position_id = job_post.job.position.id
			else:
				return errorMessage("Candidate applied for job does not exists or the link you generate is wrong.")
				# return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Candidate applied for job does not exists or the link you generate is wrong.', 'system_error_message': ''})

			if 'cnic' in kwargs:
				cnic_no = self.kwargs['cnic']
				candidates = Candidates.objects.filter(cnic_no=cnic_no, organization=organization_id, is_active=True)
				# if candidate.count() >1:
					#TODO inactive the extra candidate records.
					# candidate = candidate.last()
				
			elif 'uuid' in kwargs:
				candidate_uuid = self.kwargs['uuid']
				candidates = Candidates.objects.filter(uuid=candidate_uuid, organization=organization_id, is_active=True)
				
			else:
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'You hit the wrong url or please contact to administered.', 'system_error_message': ''})


			
			if not candidates.exists():
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Candidate does not exists.', 'system_error_message': ''})
			
			candidate = candidates.last()
			
			
			candidate_job = None

			if job_post is not None:
				candidate_job = CandidateJobs.objects.filter(candidate=candidate.id, job_post=job_post.id)
				if candidate_job.exists():
					if candidate_job.filter(is_active=True).exists():
						candidate_job = candidate_job.filter(is_active=True).last()
					else:
						candidate_job = candidate_job.last()
				else:
					return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Candidate does not applied for this job, please first apply for the job.', 'system_error_message': ''})
			else:
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Candidate applied for job does not exists or the link you generate is wrong.', 'system_error_message': ''})

			
			assessment_types = AssessmentTypes.objects.filter(is_active=True)
			
			technical_type = assessment_types.filter(is_technical=True).first()
			
			non_technical_type = assessment_types.filter(is_technical=False).first()
			
			candidate_non_test = []
			candidate_tech_test = []
			
			non_tech_test = AssessmentTests.objects.filter(is_active=True, organization=organization_id, assessment_type=non_technical_type.id, position=None)
			
			non_tech_result = self.getCandidateAssessmentTests(non_tech_test, candidate, candidate_job)
			result['non_tech_test'] = non_tech_result
			candidate_non_test = non_tech_result['data']
			
			#process the technical tests
			# first we check the job post activate or not then process the test

			if job_post is not None:
				
				position_id = job_post.job.position.id
				
				tech_test = AssessmentTests.objects.filter(is_active=True, assessment_type=technical_type.id, position=position_id)
				
				tech_result = self.getCandidateAssessmentTests(tech_test, candidate, candidate_job)

				candidate_tech_test = tech_result['data']

				result['tech_test_message'] = tech_result['message']
		

			if candidate_job is not None:
				candidate_job = ListCandidateJobsSerializers(candidate_job)
				result['candidate_job_post'] = candidate_job.data

			if job_post is not None:
				job_post = JobListPostSerializers(job_post)
				result['job_post'] = job_post.data

			result['candidate_tech_test'] = candidate_tech_test
			result['candidate_non_test'] = candidate_non_test
			result['non_tech_test_message'] = non_tech_result['message']

			# print(result)


			return Response({'status':200, 'system_status': 200, 'data': result, 'message': result['non_tech_test_message'], 'system_error_message': ''})

		except Exception as e:
			return exception(e)
	



    
	def checkCandidateJobRecords(self, request, *args, **kwargs):
		# candidate_uuid = self.kwargs['uuid']
		token_data = decodeToken(self, self.request)
		organization_id = token_data['organization_id']
		# job_post = None
		# result = {'candidate_job_post':None, 'job_post':None, 'candidate_non_test':None, 'candidate_tech_test':None}
		
		try:
			if 'cnic' in kwargs:
				cnic_no = self.kwargs['cnic']
				candidates = Candidates.objects.filter(cnic_no=cnic_no, organization=organization_id, is_active=True)
				# if candidate.count() >1:
					#TODO inactive the extra candidate records.
					# candidate = candidate.last()
				
			elif 'uuid' in kwargs:
				candidate_uuid = self.kwargs['uuid']
				candidates = Candidates.objects.filter(uuid=candidate_uuid, organization=organization_id, is_active=True)
				
			else:
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'You hit the wrong url or please contact to administered.', 'system_error_message': ''})


			
			if not candidates.exists():
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Candidate does not exists.', 'system_error_message': ''})
			
			candidate = candidates.last()
			
			
			candidate_job = None

			candidate_job = CandidateJobs.objects.filter(candidate=candidate.id)
			if candidate_job.exists():
					if candidate_job.filter(is_active=True).exists():
						candidate_job = candidate_job.filter(is_active=True)
					else:
						candidate_job = candidate_job
			else:
					return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Candidate does not applied for this job, please first apply for the job.', 'system_error_message': ''})

			candidate_job = ListCandidateJobsSerializers(candidate_job,many=True)

			return success(candidate_job.data)

		except Exception as e:
			return exception(e)
		



	def getCandidateAssessmentTests(self, assessment_tests, candidate, candidate_job):
		result = {'status':200, 'data':'', 'message':'Successfully get the assessment tests'}
		try:
			test_list = []
			if assessment_tests.exists():
				
				for nt_test in assessment_tests:
					
					candidate_tests = CandidateAssessmentTest.objects.filter(candidate=candidate.id, assessment_test=nt_test.id).exclude(is_completed=False, is_active=False)
					
					if candidate_tests.exists():
						if candidate_tests.filter(is_completed=False, is_active=True).exists():
							#check if candidate has multi active tests against single test
							total_tests = candidate_tests.count()
							
							i = 1
							if total_tests > 1:
								
								for test in candidate_tests:
									if i < total_tests:
										test.is_active=False
										test.save()
									i+=1

							
							candidate_test = candidate_tests.filter(is_completed=False, is_active=True).last()

							serializer = ListCandidateAssessmentTestSerializers(candidate_test, many=False)
							test_list.append(serializer.data)
							result['message'] = "Welcome, click on start to attempt the test ."

							
						elif candidate_tests.filter(is_completed=True, is_active=False).exists():
							candidate_test = candidate_tests.filter(is_completed=True, is_active=False).last()
							candidate_test = ListCandidateAssessmentTestSerializers(candidate_test, many=False)
							test_list.append(candidate_test.data)
							
						else:
							candidate_tests=None
							
					else:
						candidate_tests = None
						

					if candidate_tests is None:
						# create candidate assessment test
						
						candidate_test_array = {
							'candidate': candidate.id, 'assessment_test':nt_test.id, 'organization':candidate.organization.id,
							'is_email_sent': False, 'duration': nt_test.duration, 'candidate_job':None
						}
						if candidate_job is not None:
							candidate_test_array['candidate_job'] = candidate_job.id
						
						candidate_test_serializer = CreateCandidateAssessmentTestSerializers(data=candidate_test_array)
						if candidate_test_serializer.is_valid():
							cts = candidate_test_serializer.save()
							
							ct = CandidateAssessmentTest.objects.get(id=cts.id)
							if ct is not None:
								cts = ListCandidateAssessmentTestSerializers(ct, many=False)
								test_list.append(cts.data)
						else:
							result['status'] = 400
							result['message'] = candidate_test_serializer.errors
			
			result['data'] = test_list

		except Exception as e:
			result['status'] = 400
			result['message'] = str(e)

		return result

	def deactivateCandidateTest(self, request, *args, **kwargs):
		
		try:
			candidate_uuid = self.kwargs['uuid']
			candidate = Candidates.objects.filter(uuid=candidate_uuid)
			if not candidate.exists():
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Candidate does not exists.', 'system_error_message': ''})
			candidate = candidate.first()
			candidate_tests = CandidateAssessmentTest.objects.filter(candidate=candidate.id)
			
			if candidate_tests.exists():
				for test in candidate_tests:
					
					candidate_test = CandidateAssessmentTest.objects.get(id=test.id)
					candidate_test.is_active=False
					candidate_test.is_completed=False
					candidate_test.save()
			message = "Successfully deactivate all the test of candidates."
			return Response({'status':200, 'system_status': 200, 'data': '', 'message': message, 'system_error_message': ''})
		except Exception as e:
			return exception(e)

	def listCandidateAssessmentTests(self, request, *args, **kwargs):
		try:
			candidate_job_uuid = self.kwargs['uuid']
			print(candidate_job_uuid)
			candidate = CandidateJobs.objects.filter(uuid=candidate_job_uuid)
			if not candidate.exists():
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Candidate Job does not exists.', 'system_error_message': ''})
			candidate = candidate.first()

			candidate_tests = CandidateAssessmentTest.objects.filter(candidate_job=candidate.id).exclude(is_completed=False, is_active=False).order_by('-id')
			
			serializer = ListCandidateAssessmentTestSerializers(candidate_tests, many=True)
			return Response({'status':200, 'system_status': 200, 'data': serializer.data, 'message': 'Successfully get the candidate assessment tests', 'system_error_message': ''})

		except Exception as e:
			return exception(e)

	def startCandidateAssessmentTest(self, request, *args, **kwargs):
		try:
			candidate_test_uuid = self.kwargs['uuid']
			question_data = None
			candidate_test = CandidateAssessmentTest.objects.filter(uuid=candidate_test_uuid)
			if not candidate_test.exists():
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Candidate assessment test does not exists.', 'system_error_message': ''})
			candidate_test = CandidateAssessmentTest.objects.get(uuid=candidate_test_uuid)
			
			if candidate_test.candidate.is_active == False:
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Candidate is inactive and has no permission to start the test.', 'system_error_message': ''})

			if candidate_test.is_completed==True and candidate_test.is_active==False:
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Candidate already complete this test.', 'system_error_message': ''})

			assessment_file = AssessmentTestFiles.objects.filter(assessment_test=candidate_test.assessment_test, is_active=True)
			if not assessment_file.exists():
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Test has no active file.', 'system_error_message': ''})
			
			assessment_file = assessment_file.last()

			questions = Questions.objects.filter(assessment_test_file=assessment_file.id, is_active=True)

			if not questions.exists():
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Test has no active questions.', 'system_error_message': ''})

			for question in questions:
				candidate_question_array = {
					'candidate_assessment_test': candidate_test.id, 
					'question': question.id, 
					'time': question.time
				}
				if not CandidateAssessmentQuestions.objects.filter(candidate_assessment_test=candidate_test.id, question=question.id).exists():
					serializer = CreateCandidateAssessmentQuestionsSerializers(data = candidate_question_array)
					if serializer.is_valid():
						serializer.save()
					else:
						# what if not added.
						pass
			# candidate_questions = CandidateAssessmentQuestions.objects.filter(candidate_assessment_test=candidate_test.id, complete_date_time=None, answer_option=None, answer=None)
			# # candidate_question = CandidateAssessmentQuestions.objects.filter(candidate_assessment_test=candidate_test.id)
			# if candidate_questions.exists():
			# 	candidate_question = candidate_questions.first()
			# 	candidate_question.start_date_time = datetime.datetime.now()
			# 	candidate_question.save()
			# 	question = Questions.objects.get(id=candidate_question.question.id)
			# 	question_data = ShowQuestionSerializers(question)

			if candidate_test.start_date_time is None:
				candidate_test.start_date_time = datetime.datetime.now()
				candidate_test.save()

			serializer = CandidateAssessmentTestSerializers(candidate_test)
			
			next_question = self.getNotAnsNextQuestion(candidate_test.id)
			
			
			return Response({'status':next_question['status'], 'system_status': next_question['system_status'], 'file_data':serializer.data, 'data': next_question['data'], 'message': next_question['message'], 'system_error_message': ''})
			
		except Exception as e:
			return exception(e)

	def saveAndNextQuestion(self, request, *args, **kwargs):
		try:
			candidate_test_uuid = self.kwargs['uuid']
			is_last_question = False

			candidate_test = CandidateAssessmentTest.objects.filter(uuid=candidate_test_uuid)
			if not candidate_test.exists():
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Candidate assessment test does not exists.', 'system_error_message': ''})
			candidate_test = CandidateAssessmentTest.objects.get(uuid=candidate_test_uuid)
			
			if candidate_test.candidate.is_active == False:
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Candidate is inactive and has no permission to start the test.', 'system_error_message': ''})
			
			# Now check the question
			question_id = request.data.get('question')
			if not Questions.objects.filter(id=question_id, is_active=True).exists():
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Candidate question is inactive or does not exists.', 'system_error_message': ''})
			prev_question = Questions.objects.get(id=question_id)

			# Now check does candidate assessment test has this question
			if not CandidateAssessmentQuestions.objects.filter(candidate_assessment_test=candidate_test.id, question=question_id).exists():
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'the question does not belong to the candidate assessment test.', 'system_error_message': ''})

			candidate_question = CandidateAssessmentQuestions.objects.filter(candidate_assessment_test=candidate_test.id, question=question_id).last()

			serializer = AnswerCandidateAssessmentQuestionsSerializers(candidate_question, data=request.data)
			if serializer.is_valid():
				candidate_answer = serializer.save()
				if candidate_question.complete_date_time is None:
					candidate_question.complete_date_time = datetime.datetime.now()
				# Now check if candidate answer is correct or not
				if candidate_answer.answer_option==prev_question.answer_option:
					candidate_question.is_correct=True
				else:
					candidate_question.is_correct=False
				candidate_question.save()
			else:
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': '', 'system_error_message': serializer.errors})
			
			# Now fetch the next question and check if it's last
			# candidate_questions = CandidateAssessmentQuestions.objects.filter(candidate_assessment_test=candidate_test.id, complete_date_time=None, answer_option=None, answer=None)
			# if not candidate_questions.exists():
			# 	# No question is left now show the result.
			# 	# process the result
			# 	return Response({'status':200, 'system_status': 404, 'data': '', 'message': 'All questions are answered now, please process the result.', 'system_error_message': ''})

			# if candidate_questions.count() == 1:
			# 	is_last_question = True

			# candidate_question = candidate_questions.last()
			# question = Questions.objects.filter(id=candidate_question.question.id, is_active=True)
			# if not question.exists():
			# 	return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Question does not exists.', 'system_error_message': ''})

			
			# question = question.last()
			# question_data = ShowQuestionSerializers(question)

			# candidate_question.start_date_time = datetime.datetime.now()
			# candidate_question.save()


			next_question = self.getNotAnsNextQuestion(candidate_test.id)
			print(next_question['data']['result'])
			
			if next_question['data']['is_result']==True:
				candidate_test.is_completed=True
				candidate_test.is_active=False
				candidate_test.is_passed = next_question['data']['result']['is_passed']
				candidate_test.total_marks_obtained = next_question['data']['result']['total_marks_obtained']
				candidate_test.total_marks = next_question['data']['result']['total_marks']
				candidate_test.result = next_question['data']['result']['result']
				if candidate_test.complete_date_time is None:
					candidate_test.complete_date_time = datetime.datetime.now()
				candidate_test.save()
			
			return Response({'status':next_question['status'], 'system_status': next_question['system_status'], 'data': next_question['data'], 'message': next_question['message'], 'system_error_message': ''})
			

		except Exception as e:
			return exception(e)

	def getNotAnsNextQuestion(self, candidate_test_id):
		try:
			data = {'question':'', 'is_last_question':False, 'is_result':False, 'result':''}
			is_last_question = False
			# Now fetch the next question and check if it's last
			candidate_questions = CandidateAssessmentQuestions.objects.filter(candidate_assessment_test=candidate_test_id, complete_date_time=None, answer_option=None, answer=None)
			if not candidate_questions.exists():
				# No question is left now show the result.
				# process the result
				data['is_result'] = True
				candidate_result = self.processCandidateAssessmentTestResult(candidate_test_id)
				print(candidate_result)
				data['result'] = candidate_result

				return {'status':200, 'system_status':200, 'data': data, 'message': 'All questions are answered now, please process the result.', 'system_error_message':''}

			if candidate_questions.count() == 1:
				data['is_last_question'] = True

			candidate_question = candidate_questions.last()
			question = Questions.objects.filter(id=candidate_question.question.id, is_active=True)
			if not question.exists():
				return {'status':400, 'system_status': 404, 'data': data, 'message': 'Question does not exists.', 'system_error_message':''}

			
			question = question.last()
			question_data = ShowQuestionSerializers(question)
			
			if candidate_question.start_date_time is None:
				candidate_question.start_date_time = datetime.datetime.now()
				candidate_question.save()

			data['question'] = question_data.data

			return {'status':200, 'system_status':200, 'data': data, 'message': 'Next Question Successfully Get.', 'system_error_message':''}

		except Exception as e:
			return {'status':400, 'system_status': 404, 'data': '', 'message': 'Exception Error', 'system_error_message': 'Exception Error: ('+str(e)+')'}

	def processCandidateAssessmentTestResult(self, candidate_test_id):
		try:
			
			result = {'status':True, 'total_questions':0, 'correct_questions':0, 'message':'Successfully process the result.'}
			candidate_questions = CandidateAssessmentQuestions.objects.filter(candidate_assessment_test=candidate_test_id)
			if not candidate_questions.exists():
				return False
			
			candidate_assessment_test = CandidateAssessmentTest.objects.get(pk = candidate_test_id)
			
			total_questions = candidate_questions.count()
			correct_questions = 0
			total_marks = 0
			total_marks_obtained = 0
			score_type = 1
			scores = ScoreGetDataView().get_score_by_type(candidate_assessment_test.candidate.organization.id, 1)
			
			for candidate_question in candidate_questions:
				if candidate_question.question.complexity_level is not None:
					if candidate_question.question.complexity_level in scores:
						marks = scores[candidate_question.question.complexity_level]['score']*scores[candidate_question.question.complexity_level]['complexity_score']
					else:
						marks = 1
				else:
					marks = 1

				total_marks += marks
				
				if candidate_question.question.answer_option==candidate_question.answer_option:
					candidate_question.is_correct=True
					candidate_question.marks=marks
					candidate_question.marks_obtained=marks
					candidate_question.save()

					total_marks_obtained += marks
					correct_questions += 1
				else:
					candidate_question.is_correct=False
					candidate_question.marks = marks
					candidate_question.marks_obtained = 0
					candidate_question.save()

			result['total_questions'] = total_questions
			result['correct_questions'] = correct_questions
			result['total_marks'] = total_marks
			result['total_marks_obtained'] = total_marks_obtained
			result['result'] = str(round(total_marks_obtained,2))+'/'+str(round(total_marks, 2))

			percentage = round((total_marks_obtained/total_marks)*100, 2)
			result['percentage'] = percentage
			if percentage >= 50:
				result['is_passed'] = True
			else:
				result['is_passed'] = False

		except Exception as e:
			result['status'] = 400
			result['message'] = "Exception Error: ("+str(e)+")"

		return result



class OnboardingCandidatesviewset(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]

	def get_onboarding_candidates(self, request, *args, **kwargs):
		try:
			organization_id = decodeToken(self, self.request)['organization_id']
			cj_id=self.kwargs['candidate_job_id']
			c_id=self.kwargs['candidate_id']
			candidate_job_list = CandidateJobs.objects.filter(id=cj_id,candidate=c_id,is_active=True,candidate__organization=organization_id,stage__is_onboard=True).order_by('-id')
			if not candidate_job_list.exists():
				return errorMessage('No data found')

			serializer = ListCandidateJobsDataSerializers(candidate_job_list, many=True)
			return success(serializer.data)
		except Exception as e:
			return exception(e)
	
	

class AssessmentTestFileQuestionsViewset(viewsets.ModelViewSet):

	permission_classes = [IsAuthenticated, CheckUserOrganization]

	def listAssessmentTestQuestions(self, request, *args, **kwargs):
		try:
			assessment_type_id = self.request.data['assessment_type']
			position_id = self.request.data['position']
			# organization_id = self.kwargs['organization']
			check_organization = userOrganizationChecks(self, request)
			if check_organization['status']==400:
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': "you do not have an active organization.", 'system_error_message': ''})
			user_organization = check_organization['organization']

			if not AssessmentTypes.objects.filter(id=assessment_type_id, is_active=True).exists():
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Assessment type does not exists', 'system_error_message': ''})
			assessment_type = AssessmentTypes.objects.get(id=assessment_type_id)

			assessment_tests = AssessmentTests.objects.filter(assessment_type=assessment_type_id, organization=user_organization.id, is_active=True)
			
			if assessment_type.is_technical==True:
				position = Positions.objects.filter(id=position_id, is_active=True, staff_classification__organization__id=user_organization.id)
				if not position.exists():
					return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Position does not exists or inactive', 'system_error_message': ''})
				position = Positions.objects.get(id=position_id)

				assessment_tests = assessment_tests.filter(position=position_id)

			if not assessment_tests.exists():
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Found no active assessment test', 'system_error_message': ''})

			assessment_test = assessment_tests.first()

			assessment_test_files = AssessmentTestFiles.objects.filter(assessment_test=assessment_test.id, is_active=True).order_by('-id')

			if not assessment_test_files.exists():
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'No assessment test file exists.', 'system_error_message': ''})

			assessment_test_file = assessment_test_files.first()

			questions = Questions.objects.filter(assessment_test_file=assessment_test_file.id, is_active=True)
			if not questions.exists():
				return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'No question exists against assessment test.', 'system_error_message': ''})

			file_data = CUAssessmentTestFilesSerializers(assessment_test_file)
			questions_data = AdminViewQuestionSerializers(questions, many=True)

			return Response({'status':200, 'system_status': 200, 'data': questions_data.data, 'file_data':file_data.data, 'message': 'Successfully get all questions.', 'system_error_message': ''})

		except Exception as e:
			return exception(e)