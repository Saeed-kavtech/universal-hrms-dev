from rest_framework import viewsets
# from helpers.decode_token import decodeToken
from helpers.status_messages import ( 
    exception, errorMessage, serializerError, successMessageWithData,
    success, successfullyCreated, successMessage,successfullyUpdated
)
from .models import SkillTypes, KavskillsEnrollmentForm
from .serializers import (
    SkillTypesSerializers, KavskillsEnrollmentFormSerializers, SkillTypesPreDataSerializers
)
from django.core.mail import EmailMessage
import datetime

class SkillTypesViewset(viewsets.ModelViewSet):
    queryset = SkillTypes.objects.all()
    serializer_class = SkillTypesSerializers

    def list(self, request, *args, **kwargs):
        try:
            organization_id = 4
            queryset = self.queryset.filter(organization=organization_id, is_active=True)
            serializer = self.get_serializer(queryset, many=True)
            serialized_data = serializer.data

            return successMessageWithData('success', serialized_data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            organization_id = 4
            request.data['organization'] = organization_id
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return exception(e)       

        
    
class KavskillsEnrollmentFormViewset(viewsets.ModelViewSet):
    queryset = KavskillsEnrollmentForm.objects.all()
    serializer_class = KavskillsEnrollmentFormSerializers
    
    def get_queryset(self):
        try:
            organization_id = 4
            return self.queryset.filter(skill_type__organization=organization_id)
        except Exception as e:
            return None

    def list(self, request, *args, **kwargs):
        try:
            query = self.get_queryset().filter(is_active=True)
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
            
    def patch(self, request, *args, **kwargs):
        try:

            pk = self.kwargs['pk']
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('Does not exists')
            elif not query.filter(is_active=True).exists():
                return errorMessage('Deactivated at this id')
            obj = query.get()
            serializer = self.serializer_class(obj, data = request.data, partial=True)

            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            
            return successfullyUpdated(serializer.data)
      
        except Exception as e:
            return exception(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('Does not exists')
            elif not query.filter(is_active=True).exists():
                return errorMessage('Deactivated at this id')

            obj = query.get()
            serializer = self.serializer_class(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            organization_id = 4
            if request.data:
                request.data._mutable = True
                
            required_fields = [
                'skill_type', 'full_name', 'email', 'contact_number', 'cnic_no', 
                'educational_qualifications', 'university_name', 'major', 'objectives',
                'kav_skills_resume', 'joining_reason',
            ]

            if not all(field in request.data for field in required_fields):
                return errorMessage(
                    '''make sure you have added all the required fields: [skill_type, 
                    email, full_name, contact_number, cnic_no, educational_qualifications, 
                    university_name, major, objectives, kav_skills_resume, joining_reason]'''
                )

            request.data['is_active'] = True
            skill_type_id = request.data['skill_type']
            skill_type = SkillTypes.objects.filter(
                id=skill_type_id, 
                organization=organization_id,
                is_active=True
            )
            if not skill_type.exists():
                return errorMessage('skill type does not exists')
            skill_type_obj = skill_type.get()
            link = skill_type_obj.course_details
            if link:
                link = link.url
            
            joining_reason = request.data.get('joining_reason', None)
            objectives = request.data.get('objectives', None)
            financial_aid = request.data.get('financial_aid', False)

            if joining_reason:
                field_name = 'joining_reason'
                check_word_count = self.check_word_count(field_name, joining_reason, 250)
                if check_word_count['status'] == 400:
                    return errorMessage(check_word_count['message'])
                
            if objectives:
                field_name = 'objectives'
                check_word_count = self.check_word_count(field_name, objectives, 250)
                if check_word_count['status'] == 400:
                    return errorMessage(check_word_count['message'])
                
            if financial_aid:
                financial_aid_reason = request.data.get('financial_aid_reason', None)
                if financial_aid_reason:
                    field_name = 'financial_aid_reason'
                    check_word_count = self.check_word_count(field_name, objectives, 250)
                    if check_word_count['status'] == 400:
                        return errorMessage(check_word_count['message'])
            else:
                request.data['financial_aid_reason'] = None
                
            cnic_no = request.data['cnic_no']
            query = self.get_queryset().filter(skill_type=skill_type_id, cnic_no=cnic_no, is_active=True)
            if query.exists():
                return errorMessage('You are already enrolled')
            
            serializer = self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            name = request.data.get('full_name')
            email = request.data.get('email')

            send_enrollement_email = self.send_enrollement_email(name, email, link)

            return successMessageWithData('Form submitted successfully', serializer.data)
        except Exception as e:
            return exception(e)    

    def send_enrollement_email(self, name, to, link):
        try:
            result = {'status': 200, 'message': None}
            
            image = 'https://universalhrms.s3.eu-west-1.amazonaws.com/kavskill.jpg'
            pdf_link = ''
            if link:
                pdf_link = f'''
                    <center><a style="font-family: system-ui;border: 
                    dotted 3px orange;background-color:#3b0557; color:white; padding:10px;cursor: 
                    pointer;white-space:nowrap;font-size:80%;"
                    href="{link}" download="Course_details">GRAB THE COURSE DETAILS!</a></center>
                '''

            subject = 'Enrollment form confirmation email'
            body = (f"""
                       <div style="padding: 0 10px;">
                        <div style="background-color: #7900d5;">
                            <img src="{image}" style="width:100%" />
                            <div style="padding: 60px 5% 30px 5%;">
                                <div style="background-color:white; padding:25px 5%; font-size: large;">
                                        
                                            <p style="font-family: system-ui; font-weight: 500; line-height: 25px;word-spacing: 2px;"> Hi {name}! <br><br>
                                            Thank you for showing interest in the latest courses. We're
                                                thrilled to know you've taken the first step towards upgrading
                                                your skillset with KavSkills. <br><br>
                                                
                                                We assure you that after the course completion you'll be more <br>
                                                confident, have a learning mindset, and will get the job that <br>
                                                pays you well.<br><br></p>
                                                {pdf_link}
                                </div>
                                        <div style="width:100%; display: flex; padding-top:10px">
                                                    <div style="width:33.6%">
                                                        <p style="color:white;font-family: system-ui; font-weight: 500; line-height: 25px;word-spacing: 2px;">(042) 32291104</p>
                                                    </div>
                                                    <div style="width:33.6%">
                                                        <p style="color:!importantwhite;font-family: system-ui; font-weight: 500; line-height: 25px;word-spacing: 2px;">kavskills@kavmails.net</p>
                                                    </div>
                                                    <div style="width:33.6%">
                                                        <p style="color:white;font-family: system-ui; font-weight: 500; line-height: 25px;word-spacing: 1px;">Office 910, Floor 9, Haly Tower, Sector R, DHA Phase 2, Lahore</p>
                                                    </div>
                                                </div>
                            </div>
                        </div>
                    </div>
                    """)

            email = EmailMessage(
                subject=subject,
                body= body, 
                to=[to],
                from_email = "noreply@kavmails.net",
            )
            email.content_subtype = "html"
            email.send()

            return result
        except Exception as e:
            result['status'] = 400
            result['message'] = str(e)
            print(str(e))
            return result
    
    def check_word_count(self, field_name, text, words_limit):
        try:
            result = {'status': 400, 'message': None}

            word_count = len(text.split())

            if word_count > words_limit:
                result['message'] = f"Word count of {field_name} exceeds the maximum limit of {words_limit} words."
                return result

            result['status'] = 200
            return result
        except Exception as e:
            result['message'] = str(e)
            return result

    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('Does not exists at this id')
            if not query.filter(is_active=True):
                return errorMessage('Deactivated at this id')
            
            obj = query.get()
            obj.is_active = False
            obj.save()
            return successMessage('Sucessfully deactivated')
        except Exception as e:
            return exception(e)
        
class SkillTypesPreDataViewset(viewsets.ModelViewSet):
    queryset = SkillTypes.objects.all()
    serializer_class = SkillTypesPreDataSerializers

    def list(self, request, *args, **kwargs):
        try:
            organization_id = 4
            query = self.queryset.filter(organization=organization_id, is_active=True)
            serializer = self.serializer_class(query, many=True)
            serialized_data = serializer.data
            return success(serialized_data)
        except Exception as e:
            return exception(e)
        
        