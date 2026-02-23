from rest_framework import viewsets
from helpers.custom_permissions import IsAuthenticated
from helpers.status_messages import exception, errorMessage, success, successMessage, successfullyCreated, successfullyUpdated, serializerError, successMessageWithData
from helpers.decode_token import decodeToken
from email_templates.models import EmailTemplates, TemplateVariables
from employees.models import Employees
from profiles_api.utils import Util
from profiles_api.models import HrmsUsers
from rest_framework.response import Response
from profiles_api.serializers_users import HrmsUserEmployeesRegisterationSerializers
from django.contrib.auth.hashers import make_password
import uuid
from django.core.mail import EmailMessage
import mimetypes
import boto3

class EmployeeEmailsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        try:
            pass
            # token_data = decodeToken(self, self.request)
            # organization_id =  token_data['organization_id']

            # email_template = EmailTemplates.objects.filter(
            #     template_type = 3, 
            #     organization=organization_id,
            #     is_active=True,
            # )

            # variables = TemplateVariables.objects.filter(
            #     template_type=3,
            #     organization=organization_id,
            #     is_active=True
            # )

            # if not email_template.exists():
            #     return errorMessage('Email Templates does not exists')
            # if not variables.exists():
            #     return errorMessage('Template Variables does not exists')
            
            # email_template = email_template.first()

            # employees = Employees.objects.filter(
            #     official_email__in = [
            #         "sarmad.karim@kavmails.net",
            #     ],
            #     organization=organization_id, 
            #     is_active=True
            # )

            # for employee in employees:
            #     new_password = str(uuid.uuid4())[:8] 
            #     hashed_password = make_password(new_password)
            #     employee.hrmsuser.password = hashed_password
            #     employee.hrmsuser.save()


            #     subject_line = self.get_code_text(
            #     email_template.subject_line, variables, employee, new_password)
            #     body = self.get_code_text(
            #         email_template.body, variables, employee, new_password)
            #     footer = self.get_code_text(
            #         email_template.footer, variables, employee, new_password)

            #     if not footer:
            #         footer = ''
            #     if not body:
            #         body = ''
                
            #     html_string = body + '\n' + '\n' + footer
                
                

            #     email = EmailMessage(
            #     subject=subject_line,
            #     body= html_string,
            #     to=[employee.official_email],
            #     from_email = "noreply@kavmails.net",
            #     )
            #     email.content_subtype = "html"   
            #     email.send()

            # return successMessage('Password changed successfully')
        except Exception as e:
            return exception(e)
        


    # def get_code_text(self, code_text, variables, employee, password):
    #     try:
    #         text = code_text
    #         for variable in variables:
    #             if variable.code == '[@employee_name]' and '[@employee_name]' in text:
    #                 text = text.replace('[@employee_name]', employee.name)
    #             if employee.official_email:
    #                 if variable.code == '[@official_email]' and '[@official_email]' in text:
    #                     text = text.replace('[@official_email]', employee.official_email)
    #             if variable.code == '[@password]' and '[@password]' in text:
    #                 text = text.replace('[@password]', password)

    #         return text

    #     except Exception as e:
    #         print(e)
    #         return None
        
