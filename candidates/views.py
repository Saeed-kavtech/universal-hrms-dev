from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from helpers.decode_token import decodeToken
from departments.views import DepartmentsViewset
# from jobs.views import JobsViewset
from email_templates.models import EmailRecipients
from organizations.staff_classification_views import StaffClassificationViewset
from positions.views import PositionViewset
from .serializers import *
from helpers.status_messages import *
from .models import *
from jobs.models import * 
from stages.models import Stages, StageTypeTemplates
from time_intervals.models import TimeIntervals
from logs.views import UserLoginLogsViewset
# Create your views here.
from time_intervals.views import TimeSlotsViewset
from employees.views import PreEmployeesDataView
from roles.views import PreDataRolesView
from email_templates.views import PreDataEmailTemplatesView
from evaluations.views import PreDataEvaluationsView
from interviews.views import PreInterviewDataView

from email_templates.views_candidate_emails import CandidateEmailsViewset
from email_templates.serializers import CUCandidateEmailBodySerializers, GetCandidateEmailsSerializers
from jd.serializers import JdDescriptionsSerializers
from time_intervals.serializers import ChoicesTimeIntervalsSerializers

from django.core.paginator import Paginator
from employees.models import Employees
from employees.serializers import EmployeePreDataSerializers
import datetime
import json
from candidate_emails.models import CandidateEmails
from jobs.serializers import JobTypesSerializers
from helpers.email_data import notify_candidates_and_admin_by_email, notify_candidates_by_email

class CandidatesViewset(viewsets.ModelViewSet):

    def filter_pre_data(self,request,*args, **kwargs):
        try:
            # print("In")
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
           
            department=DepartmentsViewset().pre_data(user_organization)
          
            staff_classification=StaffClassificationViewset().pre_data(user_organization)
           
            position_query= Positions.objects.filter(staff_classification__organization=user_organization,is_active=True).order_by('-id')
            position=position_query.values("id","title")

            jobs_query = Jobs.objects.filter(staff_classification__organization=user_organization,is_active=True).order_by('-id')
            job=jobs_query.values("id","title")
            
            

            data={
                "department":department,
                "staff_classification":staff_classification,
                "position":position,
                "job":job
                
            }
            return success(data)
        except Exception as e:
            return exception(e)


    def list(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            status = request.data.get('status')
            if status not in ['all', 'active', 'inactive']:
                status = None
            # print("Test")

            
            page_number = request.data.get('page', None)
            if page_number is not None:
                page_number = int(page_number)
            else:
                page_number = 1

            

            


            results_per_page = request.data.get('pagination_limit', None)
            if results_per_page is not None:
                results_per_page = int(results_per_page)
            else:
                results_per_page = 50

            evaluation_score= request.data.get('evaluation_score', None)

            job_id = request.data.get('job', None)

            if job_id  is not None:   
                job_query=Jobs.objects.filter(id=job_id,staff_classification__organization=user_organization,is_active=True)
                if not job_query.exists():
                    return errorMessage("Job not exists")


            department_id = request.data.get('department')

            # print("Test",department_id)

            

            if department_id is not None:   
                
                departments_query=Departments.objects.filter(id=department_id,grouphead__organization=user_organization,is_active=True)
                if not departments_query.exists():
                    return errorMessage("Department not exists")
                

            staff_classification_id = request.data.get('staff_classification', None)

            if staff_classification_id is not None:   
                staff_classification_query=StaffClassification.objects.filter(id=staff_classification_id,organization=user_organization,is_active=True)
                if not staff_classification_query.exists():
                    return errorMessage("Staff classification not exists")
                
            position_id = request.data.get('position', None)

            if position_id  is not None:   
                position_query=Positions.objects.filter(id=position_id,grouphead__organization=user_organization,is_active=True)
                if not position_query.exists():
                    return errorMessage("Position not exists")
                


            candidate_job_list = CandidateJobs.objects.filter(
                is_active=True, 
                candidate__organization=user_organization, 
                job_post__is_active=True
            )

            if department_id is not None:
                candidate_job_list=candidate_job_list.filter(job_post__job__department=department_id)

            if staff_classification_id is not None:
                candidate_job_list=candidate_job_list.filter(job_post__job__staff_classification=staff_classification_id)

            if position_id is not None:
                candidate_job_list=candidate_job_list.filter(job_post__job__position=position_id)

            if job_id is not None:
                candidate_job_list=candidate_job_list.filter(job_post__job=job_id)

            if evaluation_score is not None:
                candidate_job_list=candidate_job_list.filter(evaluation_score=evaluation_score)



            result = {'candidate_job_list_qualified': None, 'candidate_job_list_disqualified': None}
            candidate_job_list_qualified = candidate_job_list.filter(is_qualified=True).order_by('-id')
            candidate_job_list_disqualified = candidate_job_list.filter(is_qualified=False).order_by('-id')
            
            paginator_qualified = Paginator(candidate_job_list_qualified, results_per_page)
            total_pages_qualified = paginator_qualified.num_pages

            paginator_disqualified = Paginator(candidate_job_list_disqualified, results_per_page)
            total_pages_disqualified = paginator_disqualified.num_pages

            is_qualified = True
            if page_number < 1 or page_number > total_pages_qualified:
                is_qualified = False

            is_disqualified = True
            if page_number < 1 or page_number > total_pages_disqualified:
                is_disqualified = False
            
            if not is_qualified and not is_disqualified:
                return errorMessage('Invalid page number') 
            
            candidate_assessment_test_data = CandidateAssessmentTest.objects.filter(candidate__organization=user_organization)
            if is_qualified:
                qualified_page_obj = paginator_qualified.get_page(page_number) 
                serializer_qualified = ListCandidateJobsSerializers(
                    qualified_page_obj, 
                    context = {
                        'total_pages_qualified': total_pages_qualified, 
                        'total_pages_disqualified': total_pages_disqualified, 
                        # 'candidate_assessment_test_data': candidate_assessment_test_data
                    },
                    many=True
                )
                result['candidate_job_list_qualified'] = serializer_qualified.data
                
            if is_disqualified:
                disqualified_page_obj = paginator_disqualified.get_page(page_number)
                serializer_disqualified = ListCandidateJobsSerializers(
                    disqualified_page_obj, 
                    context = {
                        'total_pages_qualified': total_pages_qualified, 
                        'total_pages_disqualified': total_pages_disqualified, 
                        # 'candidate_assessment_test_data': candidate_assessment_test_data
                    },
                    many=True
                )
                result['candidate_job_list_disqualified'] = serializer_disqualified.data

            return success(result)
        except Exception as e:
            return exception(e)

    def get(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
            pk = self.kwargs['uuid']
            candidate = Candidates.objects.filter(uuid=pk)
            if not candidate.exists():
                return errorMessage('Candidate does not exists')
            if not candidate.filter(organization=user_organization).exists():
                return errorMessage('This candidate does not belong to this organization')
            if not candidate.filter(is_active=True):
                return errorMessage('This candidate is deactivated')
            
            obj = Candidates.objects.get(uuid=pk)
            serializer = CandidatesViewsetSerializers(obj)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

  
                
    def create(self, request, *args, **kwargs):
        try:
            
            job_post_uuid = self.kwargs['uuid']
            
            job_post_check = self.checkJobPost(job_post_uuid)
            if job_post_check['status'] == 400:
                return Response({'status':404, 'message':"the job you apply does not exists or have some error to apply."})
            job_post = job_post_check['data']
            
            organization_id = job_post.job.staff_classification.organization.id
            
            request.data._mutable = True
            request.data['organization'] = organization_id
            stage = None
            
          
            stages = Stages.objects.filter(organization=organization_id, level=0, is_active=1)
            
            if stages.exists():
                stage = stages.first()
                request.data['stage'] = stage.id
            else:
                request.data['stage'] = None
            
            request.data._mutable = False

            candidate_check = self.checkCandidate(request.data)
            if candidate_check['status'] == 200:
                candidate = candidate_check['data']
                
                candidate_job_post = self.candidateJobPostApply(candidate, job_post, request.data, stage)

                return Response(candidate_job_post)

            
            else:
                return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Validation Error', 'system_error_message': candidate_check['message']})
        except Exception as e:
            return exception(e)

    def candidate_job_pre_data(self, request, *args, **kwargs):
        result = {'job_description':None, 'time_intervals':None}
        try:
            job_post_uuid = self.kwargs['uuid']
            job_post = JobPosts.objects.filter(uuid=job_post_uuid)
            if not job_post.exists():
                return errorMessage("Job post does not exists")
            elif not job_post.filter(is_active=True).exists():
                return errorMessage("job post is deactivated against this uuid")
            job_post = job_post.get()

            organization_id = job_post.job.staff_classification.organization.id
            
            jd_description = JdDescriptions.objects.filter(id=job_post.jd_selection.id)
            serializer = JdDescriptionsSerializers(jd_description, many=True)
            result['job_description'] = serializer.data

            time_intervals = TimeIntervals.objects.filter(organization=organization_id, is_active=True)
            serializer = ChoicesTimeIntervalsSerializers(time_intervals, many=True)
            result['time_intervals'] = serializer.data

            return success(result)
        except Exception as e:
            return exception(e)

    def update(self, request, *args, **kwargs):
        message = 'Update function is not offered in this path.'
        return Response({'status': 400, 'system_status': 403, 'data': '','message': message, 'system_error_message': ''})

    def patch(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if Candidates.objects.filter(id=pk).exists():
                obj = Candidates.objects.get(id=pk)
                serializer = UpdateCandidatesViewsetSerializers(obj, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'status':200, 'system_status': 200, 'data': serializer.data, 'message': 'Updated Successfully', 'system_error_message': ''})
                else:
                    return Response({'status':400, 'system_status': 400, 'data': '' ,'message':serializer.errors, 'system_error_message': ''})
            
            else:
                return Response({'status': 400, 'system_status': 404, 'data': '' ,'message': "Candidate does not exist at this index", 'system_error_message': ''}) 


        except Exception as e:
            return exception(e)

    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if Candidates.objects.filter(id=pk).exists(): 
                obj = Candidates.objects.get(id=pk)
                if obj.is_active == False:
                    msg = "This Candidate is already deactivated"
                    return Response({'status':400, 'system_status': 400, 'data': '', 'message':msg, 'system_error_message': ''})
        
                obj.is_active = False
                obj.save()
                serializer = CandidatesViewsetSerializers(obj, many=False)
                return Response({'status':200, 'system_status': 200, 'data': serializer.data, 'message': 'Successfully Deleted', 'system_error_message': ''})
            else:
                return Response({'status':400, 'system_status': 404, 'data': '','message': "Candidate does not exist at this index", 'system_error_message': ''}) 
        except Exception as e:
            return exception(e)

    def checkCandidate(self, data):
        cnic_no = data.get('cnic_no')
        organization_id = data.get('organization')
        result = {'status':200, 'data':'', 'message': 'Successfully get candidate.'}
        if Candidates.objects.filter(cnic_no=cnic_no, organization=organization_id,is_active=True).exists():
            data._mutable = True
            candidate = Candidates.objects.get(cnic_no = cnic_no, organization=organization_id,is_active=True)
            data['is_already_applied']=True
            # print("Test1",candidate)
            serializer = UpdateCandidatesViewsetSerializers(candidate, data=data,partial=True)
        else: 
            # print("Test")
            serializer = CreateCandidatesViewsetSerializers(data = data)

        if serializer.is_valid():
            result['data'] = serializer.save()
        else:
            result['status'] = 400
            result['message'] = serializer.errors
        
        return result

    def checkJobPost(self, job_post_uuid):
        try:
            
            result = {'status':200, 'data':'', 'message': 'Successfully get job post.'}
            # check if job post is active,
            # TODO check if job post date to apply is expired or not. 
            # TODO check if job is completed or not
            if JobPosts.objects.filter(uuid=job_post_uuid).exists():
                job_post = JobPosts.objects.get(uuid=job_post_uuid)
                result['data'] = job_post
                if job_post.is_active:
                    pass 
                elif job_post.expiry_date is not None:
                    if job_post.expiry_date.date() < datetime.today().date():
                        result['status'] = 202
                        result['message'] = 'The job you apply is expired'
                else:
                    result['status'] = 202
                    result['message'] = 'The job you apply is no longer active'
                
            else:
                result['status'] = 400
                result['message'] = 'The job you apply does not exists.'
        except Exception as e:
            result['status'] = 400
            result['message'] = str(e)
        # print(result)
        return result

    def candidateJobPostApply(self, candidate, job_post, data, stage):
        apply_job_error = []
        apply_jobs = []
        result = {"status":200, "data":"", "message":"", "apply_job_error":"", "email_error_message": ""}
        try:
            #check if candidate apply and something not completed or any field is missing or HR mark it's status
            # to in-active or deleted, then what's the action is applied by system. 
            # these are updated or checked on checkJobPost function.
            emailmessage=""

            candidate_jp = {"candidate": candidate.id, "job_post": job_post.id, "time_interval": data.get('time_interval'), "stage": data.get('stage'), "resume": data.get('resume')}
            has_first_attempt = True
            if CandidateJobs.objects.filter(candidate=candidate.id, job_post=job_post.id).exists():
                candidate_job = CandidateJobs.objects.get(candidate=candidate.id, job_post=job_post.id)
                serializer = CreateUpdateCandidateJobsSerializers(candidate_job, data = candidate_jp)
                result['message'] = "Your job post application is updated, as you already applied for this job."
                has_first_attempt = True
            else:
                serializer = CreateUpdateCandidateJobsSerializers(data = candidate_jp)
                serializer.candidate = candidate 
                serializer.job_post = job_post 
                result['message'] = "You Successfully applied for this job."
            if serializer.is_valid():
                cd = serializer.save()
                candidate_job_data_get = CandidateJobs.objects.get(pk=cd.id)

                
                if stage is not None:
                    if stage.is_email :
                        if stage.email_template is not None:
                            email_template = CandidateEmailsViewset.checkEmailTemplate(self, stage.email_template.id, stage.organization.id)
                            if email_template is not None:
                                email_template_data = {"candidate": candidate.id, "candidate_job": candidate_job_data_get.id, "stage": stage.id, "email_template":stage.email_template.id}
                                serializer = GetCandidateEmailsSerializers(data=email_template_data)
                                if serializer.is_valid():
                                    ce_serializer = serializer.save()
                                    candidate_email = serializer.data
                                    variables = CandidateEmailsViewset().get_variables(stage.organization.id)
                                    
                                    subject_line = CandidateEmailsViewset().get_code_text(candidate_email, email_template.subject_line, candidate_job_data_get, variables)
                                    body = CandidateEmailsViewset().get_code_text(candidate_email, email_template.body, candidate_job_data_get, variables)
                                    footer = CandidateEmailsViewset().get_code_text(candidate_email, email_template.footer, candidate_job_data_get, variables)

                                    # print(candidate_email['id'])

                                    email_body = {'candidate_email':candidate_email['id'], 'subject': subject_line, 'body': body, 'footer': footer}
                                    eb_serializer = CUCandidateEmailBodySerializers(data=email_body)
                                    if eb_serializer.is_valid():
                                        eb_serializer.save()

                                        html_string = body  + '\n' + '\n' + footer
                                        # Now sent the email
                                        if stage.notify_to_admin:
                                            cc=[]
                                            cc_employee=EmailRecipients.objects.filter(employee__organization=stage.organization.id,level=4,is_active=True)
                                            if not cc_employee.exists():
                                                    emailmessage="Admin email is not set against this module"
                                            if cc_employee.exists():     
                                                eobj=cc_employee.get()
                                                cc=[eobj.employee.official_email]

                                            email_data = notify_candidates_by_email(subject_line, html_string, [candidate.email],cc)
                                        
                                        else:
                                             email_data = notify_candidates_by_email(subject_line, html_string, [candidate.email])
                                        result['email_error_message'] = email_data['email_error']  

                candidate_job_data = ListCandidateJobsSerializers(candidate_job_data_get, many=False)
                result['data'] = candidate_job_data.data
            else:
                result['status'] = 400
                result['system_error_message'] = serializer.errors
                result['message'] = "Job is not applied, please contact to administered or try again."

        except Exception as e:
            result['status'] = 400
            result['message'] = "Job is not applied, please contact to administered or try again."
            result['system_error_message'] = str(e)
        
        return result



class RecruitmentStagesViewSet(viewsets.ModelViewSet):
    queryset = RecruitmentStages.objects.filter(is_active=True)
    # serializer_class = RecruitmentStagesSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if RecruitmentStages.objects.filter(id=pk).exists():
                obj = RecruitmentStages.objects.get(id=pk)
                if obj.is_active == False:
                    msg = "Recruitment Stage is already deactivated"
                    return Response({'status':200, 'message':msg})
                obj.is_active = False
                obj.save()
                serializer = JobTypesSerializers(obj)
                return Response({'status':200, 'data': serializer.data, 'message': 'Deleted Successfully'})
            else:
                return Response({'status':404, 'message': 'This Recruitment Stage does not exists'})
        except Exception as e:
            return exception(e)


class CandidateStagesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            # print("Test")
            

            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            uuid = request.data['uuid']            
            # checks if candidate job exists or not and if that particular candidate job exists or not
            if not CandidateJobs.objects.filter(uuid = uuid, is_active=True).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Candidate Job does not exists or inactive', 'system_status_message': ''})
            
            stage_id = request.data['stage']
            email_error_message = ""
            emailmessage=""
            # checks if stage exists or not and if that particular recruitment stage is active or not
            if not Stages.objects.filter(id=stage_id, organization=user_organization.id, is_active=True).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'No stage exists at this id or inactive or in organization', 'system_status_message': ''})
            stage = Stages.objects.get(pk=stage_id)
            obj = CandidateJobs.objects.get(uuid=uuid)
            candidate_job_data_get = obj
            # print(obj)
            # checks if candidates exists or not and checks if candidate is active or not. 
            
            if not Candidates.objects.filter(id=obj.candidate.id).exists():
                return Response({'status': 400, 'system_status': 404, 'data': '', 'message': 'Candidate does not exist at this id or change the status to active first', 'system_status_message': ''})
            
            serializers = UpdateCandidateStagesSerializers(obj , data=request.data)
            
            if serializers.is_valid():
                serializers.save()

                # print("Test1")

                if stage is not None:
                    # print(stage)
                    if stage.is_email and stage.is_auto_sent_email:
                        # print(stage.is_email,stage.is_auto_sent_email)
                        if stage.email_template is not None:
                            # print(stage.email_template)
                            candidate_email = CandidateEmails.objects.filter(stage=stage.id, candidate_job=obj.id)
                            # print(stage.id,obj.id)
                            email_template = CandidateEmailsViewset.checkEmailTemplate(self, stage.email_template.id, stage.organization.id)
                            # print(email_template)
                            if email_template is not None and candidate_email.exists():
                                email_template_data = {"candidate": obj.candidate.id, "candidate_job": candidate_job_data_get.id, "stage": stage.id, "email_template":stage.email_template.id}
                                
                                serializer = GetCandidateEmailsSerializers(data=email_template_data)

                                if serializer.is_valid():
                                    ce_serializer = serializer.save()
                                    candidate_email = serializer.data
                                    variables = CandidateEmailsViewset().get_variables(stage.organization.id)
                                    
                                    subject_line = CandidateEmailsViewset().get_code_text(candidate_email, email_template.subject_line, candidate_job_data_get, variables)
                                    body = CandidateEmailsViewset().get_code_text(candidate_email, email_template.body, candidate_job_data_get, variables)
                                    footer = CandidateEmailsViewset().get_code_text(candidate_email, email_template.footer, candidate_job_data_get, variables)

                                    # print(subject_line,body,footer)

                                    email_body = {'candidate_email':candidate_email['id'], 'subject': subject_line, 'body': body, 'footer': footer}
                                    eb_serializer = CUCandidateEmailBodySerializers(data=email_body)
                                    if eb_serializer.is_valid():
                                        eb_serializer.save()
                                        # Assume candidate_email_body.body contains an HTML string
                                        html_string = body  + '\n' + '\n' + footer
                                        
                                        # Now sent the email
                                        if stage.notify_to_admin:
                                            cc=[]
                                            cc_employee=EmailRecipients.objects.filter(employee__organization=user_organization,level=4,is_active=True)
                                            if not cc_employee.exists():
                                                    emailmessage="Admin email is not set against this module"
                                            if cc_employee.exists():     
                                                eobj=cc_employee.get()
                                                cc=[eobj.employee.official_email]

                                            email_data = notify_candidates_and_admin_by_email(subject_line, html_string, [obj.candidate.email],cc)
                                        else:    
                                            email_data = notify_candidates_by_email(subject_line, html_string, [obj.candidate.email])
                                        email_error_message = email_data['email_error']  
                message3="Successfully Updated"+emailmessage
                return Response({'status': 200, 'system_status': 200, 'data': serializers.data, 'message': message3, 'system_error_message': '', 'email_error_message': email_error_message})
            else:
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Serializer Error', 'system_status_message': serializer.errors})
            
        except Exception as e:
            return exception(e)

class CandidateStatusActionsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    # Qualified or disqualified the candidate
    def update_candidate_status(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            emailmessage=""
            email_error_message = ""
            #Process the candidate job uuid
            candidate_job_uuid = self.kwargs['uuid']
            if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, candidate__organization=user_organization, is_active=True).exists():
                return errorMessage("Candidate job does not exist or inactive or not belongs to this organization.")
            candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

            if not 'candidate_status' in request.data:
                return errorMessage("candidate_status is required to update the status.")

            candidate_status = request.data.get('candidate_status', None)
            if candidate_status is None:
                return errorMessage("Candidate status is required.")

            candidate_status = bool(candidate_status)
            if candidate_status is not None and isinstance(candidate_status, bool):
                candidate_job.is_qualified = candidate_status
                candidate_job.disqualified_time = datetime.datetime.now()
                candidate_job.save()

                if not candidate_status:
                    # Now send the disqualification email to that candidate.
                    print('candidate_status')
                    # stage_types = StageTypeTemplates._meta.get_field('stage_type').choices
                    disqualified_type = 1
                    disqualified_template = StageTypeTemplates.objects.filter(organization=user_organization.id, stage_type=disqualified_type)
                    if disqualified_template.exists():
                        stage_type = disqualified_template.last()

                        if stage_type.is_email and stage_type.is_auto_sent_email and stage_type.email_template is not None:
                            if stage_type.email_template.is_active:
                                email_template = stage_type.email_template
                                email_template_data = {"candidate": candidate_job.candidate.id, "candidate_job": candidate_job.id, "stage_type": stage_type.id, "email_template":stage_type.email_template.id}
                                serializer = GetCandidateEmailsSerializers(data=email_template_data)
                                print('update candidate email')
                                if serializer.is_valid():
                                    ce_serializer = serializer.save()
                                    candidate_email = serializer.data
                                    variables = CandidateEmailsViewset().get_variables(stage_type.organization.id)

                                    subject_line = CandidateEmailsViewset().get_code_text(candidate_email, email_template.subject_line, candidate_job, variables)
                                    body = CandidateEmailsViewset().get_code_text(candidate_email, email_template.body, candidate_job, variables)
                                    footer = CandidateEmailsViewset().get_code_text(candidate_email, email_template.footer, candidate_job, variables)

                                    # print(candidate_email['id'])

                                    email_body = {'candidate_email':candidate_email['id'], 'subject': subject_line, 'body': body, 'footer': footer}
                                    
                                    eb_serializer = CUCandidateEmailBodySerializers(data=email_body)
                                    if eb_serializer.is_valid():
                                        eb_serializer.save()
                                        
                                        # Assume candidate_email_body.body contains an HTML string
                                        html_string = body  + '\n' + '\n' + footer
                                        cc=[]
                                        cc_employee=EmailRecipients.objects.filter(employee__organization=user_organization,level=4,is_active=True)
                                        if not cc_employee.exists():
                                                emailmessage="Admin email is not set against this module"
                                        if cc_employee.exists():     
                                            eobj=cc_employee.get()
                                            cc=[eobj.employee.official_email]

                                        email_data = notify_candidates_and_admin_by_email(subject_line, html_string, [candidate_job.candidate.email],cc)
                                        email_error_message = email_data['email_error']
            else:
                return errorMessage("Candidate status must be a bool value.")

            if candidate_status:
                action = 'Qualified'
            else:
                action = 'Dis-qualified'
            reason = ''
            if 'reason' in request.data:
                reason = request.data.get('reason')
            # print('data save candidate job')

            candidate_job_data = ListCandidateJobsSerializers(candidate_job, many=False)
            data = {'candidate_job': candidate_job_data.data, 'candidate_job_log':''}

            candidate_status_log_array = {'candidate': candidate_job.candidate.id, 'candidate_job': candidate_job.id, 
                'action': action, 'action_by':request.user.id, 'action_reason':reason }
            # print(candidate_status_log_array)

            serializer = CreateCandidateStatusLogSerializers(data=candidate_status_log_array)
            if serializer.is_valid():
                serializer.save()

                data['candidate_job_log'] = serializer.data
                message1="Successfully update the candidate status and log."+emailmessage
                return Response({'status': 400, 'system_status': 400, 'data': data, 'message': message1, 'system_error_message': '', 'email_error_message': email_error_message})
            else:
                message2="Candidate status Successfully updated, but log is not updated."+emailmessage
                return successMessageWithData(message2, data )
            

        except Exception as e:
            return exception(e)

    def candidate_status_on_job_update(self, job_post):
        result = {'data':'', 'message':'', 'status':200}
        try:
            
            candidate_list = CandidateJobs.objects.filter(job_post=job_post.id, is_active=True, is_qualified=True)
            if candidate_list.exists():
                for candidate_job in candidate_list:
                    job_type = 2 #Job Close
                    job_template = StageTypeTemplates.objects.filter(organization=user_organization.id, stage_type=job_type)
                    if job_template.exists():
                        stage_type = job_template.last()
                        if stage_type.is_email and stage_type.is_auto_sent_email and stage_type.email_template is not None:
                            if stage_type.email_template.is_active:
                                email_template = stage_type.email_template
                                email_template_data = {"candidate": candidate_job.candidate.id, "candidate_job": candidate_job.id, "stage_type": stage_type.id, "email_template":stage_type.email_template.id}
                                serializer = GetCandidateEmailsSerializers(data=email_template_data)

                                if serializer.is_valid():
                                    ce_serializer = serializer.save()
                                    candidate_email = serializer.data
                                    variables = CandidateEmailsViewset().get_variables(stage_type.organization.id)

                                    subject_line = CandidateEmailsViewset().get_code_text(candidate_email, email_template.subject_line, candidate_job, variables)
                                    body = CandidateEmailsViewset().get_code_text(candidate_email, email_template.body, candidate_job, variables)
                                    footer = CandidateEmailsViewset().get_code_text(candidate_email, email_template.footer, candidate_job, variables)

                                    # print(candidate_email['id'])

                                    email_body = {'candidate_email':candidate_email['id'], 'subject': subject_line, 'body': body, 'footer': footer}
                                    eb_serializer = CUCandidateEmailBodySerializers(data=email_body)
                                    if eb_serializer.is_valid():
                                        eb_serializer.save()
                                        # Assume candidate_email_body.body contains an HTML string
                                        html_string = body  + '\n' + '\n' + footer

                                        notify_candidates_by_email(subject_line, html_string, [candidate_job.candidate.email])
                                        
                    # Now update the candidate job status
                    candidate_job.is_active=False
                    candidate_job.save()

            return result

        except Exception as e:
            result['status'] = 400
            result['message'] = str(e)
            return result

    def list_candidate_by_job_post(self, request, *args, **kwargs):
        try:
            job_post_uuid = self.kwargs['uuid']
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            job_post = JobPosts.objects.filter(uuid=job_post_uuid)
            if job_post.exists():
                job_post = job_post.first()

                candidate_job_list = CandidateJobs.objects.filter(is_active=True, candidate__organization=user_organization, job_post=job_post.id).order_by('-id')
                serializer = ListCandidateJobsSerializers(candidate_job_list, many=True)
                
                return success(serializer.data)

            return errorMessage("Job doesn't exist.")
        except Exception as e:
            return exception(e)

    def list_candidate_by_position_exclude_job_candidates(self, request, *args, **kwargs):
        try:
            #Exclude the 
            job_post_uuid = self.kwargs['uuid']

            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            job_post = JobPosts.objects.filter(uuid=job_post_uuid)
            if job_post.exists():
                job_post = job_post.first()
                
                candidate_list = CandidateJobs.objects.filter(is_active=True, candidate__organization=user_organization.id, is_qualified=True, job_post__job__position=job_post.job.position.id).exclude(job_post=job_post.id).order_by('-id')
                unique_candidate_list = {}
                candidate_job_count = {}
                for candidate_job in candidate_list:
                    candidate_id = candidate_job.candidate.id
                    if candidate_id not in unique_candidate_list:
                        unique_candidate_list[candidate_id] = candidate_job
                        candidate_job_count[candidate_id] = 1
                    else:
                        candidate_job_count[candidate_id] += 1

                unique_candidates_queryset = [candidate_job for candidate_job in unique_candidate_list.values()]

                for candidate_job in unique_candidates_queryset:
                    candidate_job.total_job_count = candidate_job_count[candidate_job.candidate.id]


                serializer = ListCandidateByPositionSerializers(unique_candidates_queryset, many=True)
                
                return success(serializer.data)

            return errorMessage("Job doesn't exist.")
        except Exception as e:
            return exception(e)

    def add_candidate_to_job_post(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            job_post_uuid = self.kwargs['uuid']
            job_post_check = self.checkOrganizationJobPost(job_post_uuid, user_organization.id)

            if job_post_check['status'] == 400:
                return Response({'status':404, 'message':"the job you apply does not exists or have some error to apply."})
            job_post = job_post_check['data']

            if 'candidate_uuid' not in request.data:
                return errorMessage("Candidate must be send as candidate_uuid.")

            candidate_uuid = request.data.get('candidate_uuid')
            candidate_result = self.checkOrganizationCandidate(candidate_uuid, user_organization.id)
            if candidate_result['status'] != 200:
                return errorMessage("Candidate does not exist or belongs to this organization.")
            candidate = candidate_result['data']

            candidate_jobs = CandidateJobs.objects.filter(candidate=candidate.id)
            if candidate_jobs.filter(job_post=job_post.id).exists():
                return errorMessage("Candidate already applied for this job.")

            # Get last candidate job data
            if not candidate_jobs.exists():
                return errorMessage("Candidate does not applied to any job")

            candidate_job = candidate_jobs.last()
            new_instance = candidate_job.copy()
            new_instance.pk = None
            new_instance.job_post = job_post.id
            new_instance.stage = 1
            new_instance.evaluation_score = None
            new_instance.is_qualified = True
            new_instance.disqualified_time = None
            new_instance.is_active = True
            new_instance.created_at = datetime.datetime.now()
            new_instance.save()

            return successMessage("Successfully add the candidates to job post")

        except Exception as e:
            return exception(e)

    def add_list_of_candidate_to_job_post(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            job_post_uuid = self.kwargs['uuid']
            job_post_check = self.checkOrganizationJobPost(job_post_uuid, user_organization.id)

            if job_post_check['status'] == 400:
                return Response({'status':404, 'message':"the job you apply does not exists or have some error to apply."})
            job_post = job_post_check['data']

            if 'candidates' not in request.data:
                return errorMessage("Candidate must be send as candidate_uuid.")

            candidate_list = request.data.get('candidates')

            if isinstance(candidate_list, str):
                candidate_list = json.loads(candidate_list)
                candidates.append(candidate_list)
            else:
                candidates = candidate_list

            total_counts = len(candidates) if candidates else 0
            i=0
            data = {'total_counts':total_counts, 'processed':0, 'un-processed':0}
            
            for candidate in candidates:
                candidate_result = self.checkOrganizationCandidate(candidate, user_organization.id)
            
                if candidate_result['status']!=200:
                    return errorMessage("Candidate does not exist or belongs to this organization.")
                candidate = candidate_result['data']

                candidate_jobs = CandidateJobs.objects.filter(candidate=candidate.id)
                if candidate_jobs.filter(job_post=job_post.id).exists():
                    # return errorMessage("Candidate already applied for this job.")
                    data['un-processed'] += 1
                    continue

                # Get last candidate job data
                if not candidate_jobs.exists():
                    # return errorMessage("Candidate does not applied to any job")
                    data['un-processed'] += 1
                    continue

                candidate_job = candidate_jobs.last()

                stage = Stages.objects.filter(id=candidate_job.stage.id, organization=user_organization)
                if stage.exists():
                    stage_obj = stage.first()
                else:
                    continue

                job_posts = JobPosts.objects.filter(id=job_post.id, job__staff_classification__organization=user_organization)
                if job_posts.exists():
                    job_post_obj = job_posts.last()
                else:
                    continue

                new_instance = CandidateJobs.objects.create(
                    job_post = job_post_obj,
                    candidate = candidate_job.candidate,
                    stage = stage_obj,
                    evaluation_score = None,
                    is_qualified = True,
                    disqualified_time = None,
                    is_active = True,
                    created_at = datetime.datetime.now(),
                )

                # new_instance = candidate_job.copy()
                # new_instance.pk = None
                # new_instance.job_post = job_post.id
                # new_instance.stage = 1
                # new_instance.evaluation_score = None
                # new_instance.is_qualified = True
                # new_instance.disqualified_time = None
                # new_instance.is_active = True
                # new_instance.created_at = datetime.datetime.now()
                new_instance.save()
                i+=1
                data['processed'] += 1

            if total_counts==data['processed']:
                return successMessage("Successfully add the candidates to job post")
            else:
                return successMessage("Candidates add but not all.")
                
        except Exception as e:
            return exception(e)


    def checkOrganizationJobPost(self, job_post_uuid, organization_id):
        try:
            
            result = {'status':200, 'data':'', 'message': 'Successfully get job post.'}
            # check if job post is active,
            # TODO check if job post date to apply is expired or not. 
            # TODO check if job is completed or not
            if JobPosts.objects.filter(uuid=job_post_uuid, job__staff_classification__organization=organization_id).exists():
                job_post = JobPosts.objects.get(uuid=job_post_uuid)
                result['data'] = job_post
                if job_post.is_active:
                    pass 
                elif job_post.expiry_date is not None:
                    if job_post.expiry_date.date() < datetime.today().date():
                        result['status'] = 202
                        result['message'] = 'The job you apply is expired'
                else:
                    result['status'] = 202
                    result['message'] = 'The job you apply is no longer active'
                
            else:
                result['status'] = 400
                result['message'] = 'The job you apply does not exists.'
        except Exception as e:
            result['status'] = 400
            result['message'] = str(e)
        # print(result)
        return result

    def checkOrganizationCandidate(self, candidate_uuid, organization_id):
        
        result = {'status':200, 'data':'', 'message': 'Successfully get candidate.'}
        if Candidates.objects.filter(uuid=candidate_uuid, organization=organization_id).exists():
            candidate = Candidates.objects.get(uuid = candidate_uuid)
            result['data'] = candidate
        else: 
            result['status'] = 404
            result['message'] = "Candidate does not exist."
        
        return result

class PreDataCandidateJobsActions(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return {'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''}
            #timeslots
            time_slots = TimeSlotsViewset().pre_data(user_organization.id, None)

            #interviewers
            hrmsusers = PreEmployeesDataView().pre_data(user_organization.id, request.user.id, None)

            #roles
            roles = PreDataRolesView().pre_data(user_organization.id)

            #email_templates
            email_templates = PreDataEmailTemplatesView().pre_data(user_organization.id)

            #evaluations
            evaluations = PreDataEvaluationsView().pre_data(user_organization.id)

            #interview modes
            interview_modes = PreInterviewDataView().pre_data_mode(user_organization.id)

            # employees
            emp = Employees.objects.filter(organization=user_organization,is_active=True)
            emp_serializer = EmployeePreDataSerializers(emp, many=True)

            data = {
                "time_slots":time_slots, "hrmsusers":hrmsusers, "roles":roles, 
                "email_templates":email_templates, "evaluations":evaluations,
                "interview_modes": interview_modes, 'employees': emp_serializer.data
            }

            return success(data)


        except Exception as e:
            return exception(e)


# class CandidateEmailActionViewset(viewsets.ModelViewSet):