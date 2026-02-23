from rest_framework import viewsets
from helpers.decode_token import decodeToken
from .serializers import CourseApplicantCustomEmailsSerializers
from .models import CourseApplicantCustomEmails
from applicants.models import CourseApplicants, CourseSessionTrainees
from helpers.status_messages import exception, errorMessage, success, successMessageWithData, serializerError
from helpers.decode_token import decodeToken
from helpers.custom_permissions import IsAuthenticated
# from bs4 import BeautifulSoup
from django.core.mail import EmailMessage
import mimetypes


class CourseApplicantCustomEmailsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = CourseApplicantCustomEmails.objects.all()
    serializer_class = CourseApplicantCustomEmailsSerializers

    def get_queryset(self):
        organization_id = decodeToken(self, self.request)['organization_id']
        return self.queryset.filter(course_applicant__employee__organization=organization_id)

    def list(self, request, *args, **kwargs):
        try:
            query = self.get_queryset().filter(is_active=True)
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def get_list_of_applicant(self, request, *args, **kwargs):
        try:
            course_applicant_id = self.kwargs['course_applicant_id']
            query = self.get_queryset().filter(course_applicant=course_applicant_id, is_active=True)
            if not query.exists():
                return errorMessage('No custom email exists against this applicant')

            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
    
    def get_email_list_against_course_session(self, request, *args, **kwargs):
        try:
            if 'course_session_id' in self.kwargs:
                course_session_id = self.kwargs['course_session_id']
            else:
                return errorMessage('Course session is the required field')
            
            query = self.get_queryset().filter(course_applicant__course_session=course_session_id, is_active=True)
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)

        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            if request.data:
                request.data._mutable = True
                course_applicant_id = request.data['course_applicant']

            required_fields = ['course_applicant', 'subject', 'body']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [course_applicant, subject, body]')
                        
            course_session_trainee = CourseSessionTrainees.objects.filter(course_applicant=course_applicant_id)
            if course_session_trainee.exists():
                request.data['is_trainee'] = True
            else:
                applicant_query = CourseApplicants.objects.filter(id=course_applicant_id, employee__organization=organization_id)
                if not applicant_query.exists():
                    return errorMessage('Applicant does not exists')
                elif not applicant_query.filter(is_active=True):
                    return errorMessage('Applicant is deactivated')

            request.data['action_by'] = request.user.id
            request.data['is_active'] = True
            serializer = self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            custom_email_data = serializer.save()
            is_email_sent_successfully = self.send_email_to_course_applicant(custom_email_data)
            if is_email_sent_successfully['status'] != 200:
                message = 'Email content is successfully saved. However email is not sent successfully'
                error_msg = is_email_sent_successfully['message']
                data = {'message': message, 'error_msg': error_msg} 
                return successMessageWithData(data, serializer.data)
            
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def send_email_to_course_applicant(self, custom_email_data):
        try:
            result = {"status": 200, "message": "Successfully send the email."}
            
            # Assume candidate_email_body.body contains an HTML string
            if not custom_email_data.footer:
                custom_email_data.footer = ''
            html_string = custom_email_data.body  + '\n' + '\n' + custom_email_data.footer
            # Create a BeautifulSoup object from the HTML string
            # parsed_html_body = BeautifulSoup(html_string, 'html.parser')
            email = EmailMessage(
                subject=custom_email_data.subject,
                body= html_string, #parsed_html_body.get_text(),
                to=[custom_email_data.course_applicant.employee.official_email],
                from_email = "noreply@kavmails.net",
            )
            email.content_subtype = "html"

            #check if email has attachment
            if custom_email_data.attachment:
                attachment = custom_email_data.attachment
                file_path = attachment.path
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    file_name = attachment.name.split('/')[-1]
                    content_type, encoding = mimetypes.guess_type(file_name)
                    email.attach(file_name, file_data, content_type)

            # Now sent the email
            email.send()
            return result
        except Exception as e:
            result['status'] = 404
            result['message'] = str(e)
            return result