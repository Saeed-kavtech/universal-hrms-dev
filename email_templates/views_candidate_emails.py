from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from django.shortcuts import get_object_or_404

from .models import *
from candidate_emails.models import *
from rest_framework import viewsets
from .serializers import *

from candidates.models import CandidateJobs

from helpers.status_messages import *
from helpers.custom_permissions import *

from logs.views import UserLoginLogsViewset
from interviews.views import CandidateInterviewsViewset
from interviews.models import CandidateInterviews
from bs4 import BeautifulSoup
from django.core.mail import EmailMessage
import mimetypes

class CandidateEmailsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            # Process the candidate job uuid
            candidate_job_uuid = self.kwargs['uuid']
            if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, is_active=True, candidate__organization__id=user_organization.id).exists():
                return errorMessage("Candidate job does not exist.")
            candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

            obj = CandidateEmails.objects.filter(candidate_job=candidate_job.id)

            serializer = GetCandidateEmailsSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            # Process the candidate job uuid
            candidate_job_uuid = self.kwargs['uuid']
            if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, is_active=True, candidate__organization__id=user_organization.id).exists():
                return errorMessage("Candidate job does not exist or inactive or not belongs to this organization.")
            candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

            # Check Stage
            stage = None
            if 'stage' in request.data:
                stage = CandidateInterviewsViewset().checkStage(request.data.get('stage'), user_organization.id)

                if stage is None:
                    return errorMessage("Stage is not exist or match the organization")
                elif stage.is_email == False:
                    return errorMessage("This stage has no access to send email.")
            else:
                return errorMessage("Stage is necessary to set the Email Template.")

            # check Email Template
            email_template = None
            if 'email_template' in request.data:
                email_template = self.checkEmailTemplate(request.data.get('email_template'), user_organization.id)

                if email_template is None:
                    return errorMessage("Email Template is not exist or match the organization.")
            else:
                return errorMessage("Email Template is necessary to set the Candidate Email.")

            # Process Candidate Job Stage Emails
            email_stage = self.checkCandidateEmailStageStatus(stage, candidate_job)

            if email_stage['status'] == 200:
                if email_stage['data'].email_template.id==email_template.id:
                    serializer = GetCandidateEmailsSerializers(email_stage['data'], many=False)
                    return success(serializer.data)
                else:
                    candidate_email = CandidateEmails.objects.get(pk=email_stage['data'].id)
                    candidate_email.is_active=False
                    candidate_email.save()
                    email_stage['status']=202

            if email_stage['status'] != 404 and email_stage['status'] != 202:
                return errorMessage(email_stage['message'])
            
            request.data['candidate'] = candidate_job.candidate.id
            request.data['candidate_job'] = candidate_job.id
            request.data['status'] = 2  # as we set the interview
            request.data['is_active'] = True

            serializer = GetCandidateEmailsSerializers(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return successfullyCreated(serializer.data)
            else:
                return serializerError(serializer.errors)

        except Exception as e:
            return exception(e)

    def get_by_stage_candidate_email(self, request, *args, **kwargs):
        try:
            data = {"candidate_email": '', "candidate_email_body": ''}
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            # Process the candidate job uuid
            candidate_job_uuid = self.kwargs['uuid']
            if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, is_active=True, candidate__organization__id=user_organization.id).exists():
                return errorMessage("Candidate job does not exist or inactive or not belongs to this organization.")
            candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

            stage = self.kwargs['stage']

            if stage is not None:
                stage = CandidateInterviewsViewset().checkStage(stage, user_organization.id)
                if stage.is_email == False:
                    return errorMessage("This stage has no email process.")
            else:
                return errorMessage("Stage is necessary to start the Email.")

            # check candidate email

            if not CandidateEmails.objects.filter(stage=stage.id, is_active=True, candidate_job=candidate_job.id).exists():
                return errorMessage("Candidate has no email with this id or inactive or not belongs to this candidate job.")

            candidate_email = CandidateEmails.objects.filter(
                stage=stage.id, is_active=True, candidate_job=candidate_job.id).last()
            ce_serializer = GetCandidateEmailsSerializers(candidate_email, many=False)
            data['candidate_email'] = ce_serializer.data

            # Check Candidate Email Body
            if CandidateEmailBody.objects.filter(is_active=True, candidate_email=candidate_email.id).exists():
                candidate_email_body = CandidateEmailBody.objects.filter(
                    is_active=True, candidate_email=candidate_email.id).last()
            else:
                candidate_email_body = None

            if candidate_email_body is not None:
                serializer = GetCandidateEmailBodySerializers(candidate_email_body, many=False)
                data['candidate_email_body'] = serializer.data

            return success(data)

        except Exception as e:
            return exception(e)

    def re_set_candidate_email(self, request, *args, **kwargs):
        try:
            data = {"candidate_email": '', "candidate_email_body": ''}
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            # Process the candidate job uuid
            candidate_job_uuid = self.kwargs['uuid']
            if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, is_active=True, candidate__organization__id=user_organization.id).exists():
                return errorMessage("Candidate job does not exist or inactive or not belongs to this organization.")
            candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

            stage = self.kwargs['stage']

            if stage is not None:
                stage = CandidateInterviewsViewset().checkStage(stage, user_organization.id)
                if stage is None:
                    return errorMessage("This stage does not exist.")
                if stage.is_email == False:
                    return errorMessage("This stage has no email process.")
            else:
                return errorMessage("Stage is necessary to start the Email.")

            # check Email Template
            email_template = None
            if 'email_template' in request.data:
                email_template = self.checkEmailTemplate(
                    request.data.get('email_template'), user_organization.id)

                if email_template is None:
                    return errorMessage("Email Template is not exist or match the organization.")
            else:
                return errorMessage("Email Template is necessary to set the Candidate Email.")

            # check candidate email

            if not CandidateEmails.objects.filter(stage=stage.id, is_active=True, candidate_job=candidate_job.id).exists():
                candidate_emails = CandidateEmails.objects.filter(
                    stage=stage.id, is_active=True, candidate_job=candidate_job.id)
                for candidate_email in candidate_emails:
                    candidate_email.is_active = False
                    candidate_email.save()

            request.data['candidate'] = candidate_job.candidate.id
            request.data['candidate_job'] = candidate_job.id
            request.data['status'] = 2  # as we set the interview
            request.data['is_active'] = True

            serializer = GetCandidateEmailsSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return successfullyCreated(serializer.data)
            else:
                return serializerError(serializer.errors)

        except Exception as e:
            return exception(e)

    def view_candidate_email_template(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            # Process the candidate job uuid
            candidate_job_uuid = self.kwargs['uuid']
            if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, is_active=True, candidate__organization__id=user_organization.id).exists():
                return errorMessage("Candidate job does not exist or inactive.")
            candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

            pk = self.kwargs['pk']
            if not CandidateEmails.objects.filter(pk=pk, candidate_job=candidate_job.id, is_active=True).exists():
                return errorMessage("Candidate has no email with this id or inactive or not belongs to this candidate job.")

            candidate_email = CandidateEmails.objects.get(pk=pk)
            email_template = candidate_email.email_template

            variables = self.get_variables(user_organization.id)
            # TODO what if organization has no active variables?

            subject_line = self.get_code_text(
                candidate_email, email_template.subject_line, candidate_job, variables)
            body = self.get_code_text(
                candidate_email, email_template.body, candidate_job, variables)
            footer = self.get_code_text(
                candidate_email, email_template.footer, candidate_job, variables)

            ce_serializer = GetCandidateEmailsSerializers(candidate_email, many=False)

            data = {
                "candidate_email": ce_serializer.data,
                "subject_line": subject_line,
                "body": body,
                "footer": footer
            }

            return success(data)

        except Exception as e:
            return exception(e)

    def save_candidate_email_body(self, request, *args, **kwargs):
        # TODO Log is remaining
        try:
            if request.data:
                request.data._mutable = True

            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            # Process the candidate job uuid
            candidate_job_uuid = self.kwargs['uuid']
            if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, is_active=True, candidate__organization__id=user_organization.id).exists():
                return errorMessage("Candidate job does not exist or inactive or not belongs to this organization.")
            candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

            # check candidate email
            pk = self.kwargs['pk']

            if not CandidateEmails.objects.filter(pk=pk, is_active=True, candidate_job=candidate_job.id).exists():
                return errorMessage("Candidate has no email with this id or inactive or not belongs to this candidate job.")

            candidate_email = CandidateEmails.objects.get(pk=pk)

            if candidate_email.status == 4:
                return errorMessage("Candidate email is already sent.")

            # Check Candidate Email Body

            if CandidateEmailBody.objects.filter(is_active=True, candidate_email=candidate_email.id).exists():

                candidate_email_body = CandidateEmailBody.objects.filter(
                    is_active=True, candidate_email=candidate_email.id).last()
            else:
                candidate_email_body = None

            if 'subject' in request.data:
                request.data['candidate_email'] = candidate_email.id
            else:
                return errorMessage('Subjects is necessary')

            if candidate_email_body is not None:
                serializer = CUCandidateEmailBodySerializers(candidate_email_body, data=request.data)
            else:
                serializer = CUCandidateEmailBodySerializers(data=request.data)

            if serializer.is_valid():
                serializer.save()
                data = {'candidate_save': serializer.data, 'attachment': ''}
                #check if email template has attachment true
                # if candidate_email.email_template.has_attachments:
                #Now save the attachments
                if request.FILES:
                    request.data['candidate_email'] = candidate_email.id
                    attachment_serializer = CandidateEmailAttachmentsSerializers(data=request.data)
                    if attachment_serializer.is_valid():
                        attachment_serializer.save()
                        data['attachment'] = attachment_serializer.data
                    else:
                        return serializerError(attachment_serializer.errors)

                candidate_email.status = 3  # 3 belongs to save email status
                candidate_email.save()
                
                return success(data)
            else:
                return serializerError(serializer.errors)

        except Exception as e:
            return exception(e)

    def send_candidate_email(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            # Process the candidate job uuid
            candidate_job_uuid = self.kwargs['uuid']
            if not CandidateJobs.objects.filter(uuid=candidate_job_uuid, is_active=True, candidate__organization__id=user_organization.id).exists():
                return errorMessage("Candidate job does not exist or inactive or not belongs to this organization.")
            candidate_job = CandidateJobs.objects.get(uuid=candidate_job_uuid)

            pk = self.kwargs['pk']

            # check candidate email

            if not CandidateEmails.objects.filter(pk=pk, is_active=True, candidate_job=candidate_job.id).exists():
                return errorMessage("Candidate has no email with this id or inactive or not belongs to this candidate job.")

            candidate_email = CandidateEmails.objects.get(pk=pk)

            # check if candidate email is not save or updated.
            if candidate_email.status < 3:
                return errorMessage("Candidate email is not save, first save the email and then process.")

            if candidate_email.status == 4:
                return errorMessage("Candidate email is already sent.")

            send_email_result = self.send_email_to_candidate(candidate_email)
            if send_email_result['status']==200:
                return successMessage("Successfully sent the email.")
            else:
                return errorMessage(send_email_result['message'])

            # Check Candidate Email Body
            # if CandidateEmailBody.objects.filter(is_active=True, candidate_email=candidate_email.id).exists():
            # 	candidate_email_body = CandidateEmailBody.objects.filter(
            # 	    is_active=True, candidate_email=candidate_email.id).last()
            # else:
            # 	return errorMessage("Candidate email has no email data in email body, you have to save the Email again.")


            # # Assume candidate_email_body.body contains an HTML string
            # html_string = candidate_email_body.body  + '\n' + '\n' + candidate_email_body.footer

            # # Create a BeautifulSoup object from the HTML string
            # parsed_html_body = BeautifulSoup(html_string, 'html.parser')

            # # Now sent the email
            # data = {
   #              'subject': candidate_email_body.subject,
   #              'body':  parsed_html_body.get_text(),
   #              'to_email': candidate_email_body.candidate_email.candidate.email,
   #          }
            # Util.send_email(data)


            # return successMessage("Successfully sent the email.")

        except Exception as e:
            return exception(e)

    def send_email_to_candidate(self, candidate_email):
        result = {"status": 200, "message": "Successfully send the email."}
        try:
            if CandidateEmailBody.objects.filter(is_active=True, candidate_email=candidate_email.id).exists():
                candidate_email_body = CandidateEmailBody.objects.filter(is_active=True, candidate_email=candidate_email.id).last()
            else:
                result['status'] = 400
                result['message'] = "Candidate email has no email data in email body, you have to save the Email again."
                return result

            # Assume candidate_email_body.body contains an HTML string
            html_string = f"""
                {candidate_email_body.body}  <br><br>
            """
            attachments = CandidateEmailAttachments.objects.filter(candidate_email=candidate_email.id, is_active=True)
            if attachments.exists():
                attachment = attachments.last()
                obj = get_object_or_404(CandidateEmailAttachments, pk=attachment.id)
                if obj:
                    link = attachment.attachment
                    if link:
                        attachment_message = f'Please find the attachment link: {link.url} <br>' 
                        html_string += attachment_message
                
            html_string += candidate_email_body.footer

            email = EmailMessage(
                subject=candidate_email_body.subject,
                body=html_string,
                to=[candidate_email_body.candidate_email.candidate.email],
                from_email = "noreply@kavmails.net",
            )
            email.content_subtype = "html"
            #check if email has attachment
            # attachments = CandidateEmailAttachments.objects.filter(candidate_email=candidate_email.id, is_active=True)
            # if attachments.exists():
            #     attachment = attachments.last()
            #     obj = get_object_or_404(CandidateEmailAttachments, pk=attachment.id)
            #     file_path = obj.attachment.path
            #     print(file_path)
            #     with open(file_path, 'rb') as f:
            #         file_data = f.read()
            #         file_name = obj.attachment.name.split('/')[-1]
            #         content_type, encoding = mimetypes.guess_type(file_name)
            #         email.attach(file_name, file_data, content_type)

            # Now sent the email
            email.send()
            return result
        except Exception as e:
            result['status'] = 404
            result['message'] = str(e)
            return result

    def get_variables(self, organization_id):
        try:
            if TemplateVariables.objects.filter(is_active=True, organization=organization_id).exists():
                variables = TemplateVariables.objects.filter(is_active=True, organization=organization_id)
                
                return variables
            return None
        except Exception as e:
            return None

    @action(detail=True, methods=['get'])
    def get_code_text(self,candidate_email, code_text, candidate_job, variables):
        try:
            text = code_text
            candidate_interview = None
            if variables is None:
                return text
            
            for variable in variables:
                converted_text=''
                if variable.code is None:
                    continue
                
                if '[@position_title]' in text and variable.code=='[@position_title]':
                    position_title = self.get_position_title(candidate_job)
                    if position_title is not None:
                        text = text.replace(variable.code, position_title)
                    
                elif '[@company_name]' in text and variable.code=='[@company_name]':
                    company_name = self.get_company_name(candidate_job)
                    if company_name is not None:
                        text = text.replace(variable.code, company_name)
                    
                elif '[@candidate_name]' in text and variable.code=='[@candidate_name]':
                    candidate_name = self.get_candidate_name(candidate_job)
                    if candidate_name is not None:
                        text = text.replace(variable.code, candidate_name)
                elif '[@interview_date]' in text and variable.code=='[@interview_date]':
                    interview_date = self.get_interview_date(candidate_email)
                    if interview_date is not None:
                        text = text.replace(variable.code, interview_date)
                elif '[@interview_time_slot]' in text and variable.code=='[@interview_time_slot]':
                    interview_time_slot = self.get_interview_time_slot(candidate_email)
                    if interview_time_slot is not None:
                        text = text.replace(variable.code, interview_time_slot)
                elif '[@interview_mode]' in text and variable.code=='[@interview_mode]':
                    interview_mode = self.get_interview_mode(candidate_email)
                    if interview_mode is not None:
                        text = text.replace(variable.code, interview_mode)
                elif '[@job_track_url]' in text and variable.code=='[@job_track_url]':
                    job_track_url = self.get_job_track_url(candidate_email)
                    if job_track_url is not None:
                        text = text.replace(variable.code, job_track_url)
                
            return text
                    
        except Exception as e:
            raise e

    def get_position_title(self, candidate_job):
        try:
            if candidate_job.job_post is not None:
                if candidate_job.job_post.job.position is not None:
                    return candidate_job.job_post.job.position.title
            return None
        except Exception as e:
            return None

    def get_job_track_url(self, candidate_job):
        try:
            if candidate_job.job_post is not None:
                url = "http://hrms-react-kavtech.s3-website.ap-south-1.amazonaws.com/track/"+candidate_job.job_post.uuid+"/"
                return url
            return None
        except Exception as e:
            return None

    def get_company_name(self, candidate_job):
        
        try:
            if candidate_job.candidate is not None:
                if candidate_job.candidate.organization is not None:
                    
                    return candidate_job.candidate.organization.name
            return None
        except Exception as e:
            return None

    def get_candidate_name(self, candidate_job):
        
        try:
            if candidate_job.candidate is not None:
                
                return candidate_job.candidate.candidate_name
            return None
        except Exception as e:
            return None

    def get_interview_date(self, candidate_email):
        try:
            if candidate_email.stage is None:
                return None 
            if not CandidateInterviews.objects.filter(is_active=True, stage=candidate_email.stage.id, candidate_job=candidate_email.candidate_job.id).exists():
                return None
            candidate_interview = CandidateInterviews.objects.filter(is_active=True, stage=candidate_email.stage.id, candidate_job=candidate_email.candidate_job.id).last()
            return candidate_interview.interview_date
    
        except Exception as e:
            return None

    def get_interview_time_slot(self, candidate_email):
        try:
            if candidate_email.stage is None:
                return None 
            if not CandidateInterviews.objects.filter(is_active=True, stage=candidate_email.stage.id, candidate_job=candidate_email.candidate_job.id).exists():
                return None
            candidate_interview = CandidateInterviews.objects.filter(is_active=True, stage=candidate_email.stage.id, candidate_job=candidate_email.candidate_job.id).last()
            if candidate_interview.interview_time_slot is not None:
                return candidate_interview.interview_time_slot.title
            return None
    
        except Exception as e:
            return None

    def get_interview_mode(self, candidate_email):
        try:
            if candidate_email.stage is None:
                return None 
            if not CandidateInterviews.objects.filter(is_active=True, stage=candidate_email.stage.id, candidate_job=candidate_email.candidate_job.id).exists():
                return None
            candidate_interview = CandidateInterviews.objects.filter(is_active=True, stage=candidate_email.stage.id, candidate_job=candidate_email.candidate_job.id).last()
            if candidate_interview.interview_mode is not None:
                return candidate_interview.interview_mode.title
            return None
    
        except Exception as e:
            return None

    def checkEmailTemplate(self, email_template, organization_id):
        try:
            if EmailTemplates.objects.filter(id=email_template, organization=organization_id, is_active=True).exists():
                email_template = EmailTemplates.objects.get(id=email_template)
                return email_template
            return None
        except Exception as e:
            return None

    def checkCandidateEmailStageStatus(self, stage, candidate_job):
        result = {"status":200, "data":"", "message":"Already has candidate email active stage data."}
        try:
            candidate_stage_emails = CandidateEmails.objects.filter(stage=stage.id, candidate_job=candidate_job.id)
            if not candidate_stage_emails.exists():
                #Has not data against this stage
                result['status'] = 404
                result['message'] = "Has no candidate email current stage."
                return result
            # Now checks for the interview stages. 
            # First check if stage has successfully completed
            if candidate_stage_emails.filter(is_active=True).exists():
                #return with complete stage result
                data = candidate_stage_emails.filter(is_active=True).last()
                result['data'] = data
                return result
            else:
                result['status'] = 202
                result['message'] = "Have no active stage."
                return result
            # if not CandidateEmails.objects.filter(stage=stage.id, candidate_job=candidate_job.id).exists():

        except Exception as e:
            result['status'] = 400
            print(str(e))
            result['message'] = "Have exception errors."
            return result