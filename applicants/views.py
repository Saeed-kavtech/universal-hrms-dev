from rest_framework import generics
from rest_framework.response import Response
from rest_framework import viewsets
from helpers.decode_token import decodeToken
from .serializers import *
from .models import *
from helpers.status_messages import *
from instructors.serializers import CourseSessionsViewsetSerializers, CourseSessionsApplicantViewsetSerializers
from instructors.models import CourseSessions
from helpers.custom_permissions import IsAuthenticated
from employees.serializers import PersonalEmployeeViewsetSerializers
from django.db.models import Q
import json
import datetime

# Create your views here.
class CourseApplicantsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try: 
            course_session_id = self.kwargs['course_session_id']
            organization_id = decodeToken(self, request)['organization_id']
            obj = CourseApplicants.objects.filter(course_session=course_session_id, employee__organization=organization_id, employee__is_active=True, is_active=True).order_by('-id')       
            serializer = CourseApplicantsViewsetSerializers(obj, many=True)
            return success(serializer.data)

        except Exception as e:
            return exception(e)  


    def retrieve(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            course_applicant_id = self.kwargs['course_applicant_id']

            course_applicant_query = CourseApplicants.objects.filter(id=course_applicant_id, employee__organization=organization_id)
            if not course_applicant_query.exists():
                return errorMessage('course_applicant does not exists')
            if not course_applicant_query.filter(is_active=True):
                return errorMessage('course_applicant is deactivated')
            
            obj = course_applicant_query.first()
            if obj.employee.is_active==False:
                return errorMessage('Activate the employee First')
            serializer = CourseApplicantsViewsetSerializers(obj)
        
            return success(serializer.data)
        except Exception as e:
            return exception(e)  


    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            # employee is the required field
             
            if not 'employee' in request.data:
                return Response({'status':400, 'system_status': 400, 'data': '', 'message': 'employee is required', 'system_error_message': ''})

        
            # this checks whether active course session exists or not
            course_session_id = self.kwargs['course_session_id']
            course_session_query = CourseSessions.objects.filter(id=course_session_id, course__organization=organization_id)
            if not course_session_query.exists():
                return errorMessage('course_session does not exists')
            if not course_session_query.filter(is_active=True).exists():
                return errorMessage('course_session is inactive. Activate the course session first')
            
            request.data['course_session'] = course_session_id

            # Assigning course id to course
            course_session_obj = course_session_query.first()
            course_id = course_session_obj.course.id
            request.data['course'] = course_id

            # this checks whether active employee exists or not
            employee_id = request.data['employee']
            employee_query = Employees.objects.filter(id=employee_id, organization=organization_id)
            if not employee_query.exists():
                return errorMessage('employee does not exists')
            if not employee_query.filter(is_active=True).exists():
                return errorMessage('employee is inactive. Activate the employee first')

            # This check whether course applicant exists or not
            if CourseApplicants.objects.filter(employee=employee_id, course_session=course_session_id).exists():
                return errorMessage('This employee is already registered for the course')
 
            # When course applicant is create its status is 1
            request.data['status'] = 1
            serializer = CourseApplicantsViewsetSerializers(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)    

            serializer.save()
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'successfully created', 'system_error_message': ''})                   
        except Exception as e:
            return exception(e)

    
    # This process is handled by HR 
    def multiple_applicant_selection(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            # this checks whether active course session exists or not
            course_session_id = self.kwargs['course_session_id']
            course_session_query = CourseSessions.objects.filter(id=course_session_id, course__organization=organization_id)
            if not course_session_query.exists():
                return errorMessage('course_session does not exists')
            if not course_session_query.filter(is_active=True).exists():
                return errorMessage('course_session is inactive. Activate the course session first')
            
            # getting course_id from the course session
            course_session_obj = course_session_query.first()
            course_id = course_session_obj.course.id
            
            applicants_list = request.data
            applicant_data = self.multipleApplicantData(applicants_list, course_session_id, course_id, organization_id)
            message = applicant_data['message']
            if applicant_data['code'] == 400:
                return errorMessage(message)
            
            return success(message)
            
        except Exception as e:
            return exception(e)


    def multipleApplicantData(self, applicants_data, course_session_id, course_id, organization_id):
        applicants = []
        serializer_errors = []
        response = {'code': 200, 'message': '', 'system_error': ''}
        if isinstance(applicants_data, str):
            applicants_data = json.loads(applicants_data)
            applicants.append(applicants_data)
        else:
            applicants = applicants_data
        

        try:
            applicant_array = {
                'id': '',
                'course': course_id,
                'course_session': course_session_id,
                'employee': '',
                'data': datetime.date.today(),
                'is_active': True
            }
            if applicants is not None:
                for applicant in applicants:
                    if 'employee' in applicant:
                        if not Employees.objects.filter(id=applicant['employee'], organization=organization_id, is_active=True).exists():
                            response['code'] = 400
                            response['message'] = 'Employee does not exists at this id'
                            return response
                        applicant_query = CourseApplicants.objects.filter(employee=applicant['employee'], course_session=course_session_id, employee__organization=organization_id)
                        if applicant_query.exists():
                            continue
                    else:
                        continue

                    applicant_array['employee'] = applicant['employee']

                    serializer = CourseApplicantsViewsetSerializers(data=applicant_array)

                    if serializer.is_valid():
                        serializer.save()
                    else:
                        serializer_errors.append(serializer.errors)

                if (len(applicants) == len(serializer_errors)):
                    response['message'] = "No applicant data processed, please update it again!"
                elif len(serializer_errors) > 0:
                    response['message'] = "Some of the applicant data is processed, please update it again!"
                else:
                    response['message'] = "All of the applicant data is processed Successfully."
                    response['code'] = 200
            else:
                response['message'] = "No data found"

            return response
        except Exception as e:
            response['code'] = 400
            response['system_error'] = str(e)
            return response   




    def patch(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            course_applicant_id = self.kwargs['course_applicant_id']
            
            
            # check if applicant exists or not
            course_applicant_query = CourseApplicants.objects.filter(id=course_applicant_id, employee__organization=organization_id)
            if not course_applicant_query.exists():
                return Response({'status':400, 'system_status': 400, 'data': '', 'message': 'course_applicant does not exists', 'system_error_message': ''})


            # The applicant has become the trainee now
            if CourseSessionTrainees.objects.filter(id=course_applicant_id, course_applicant__employee__organization=organization_id).exists():
                return errorMessage('This applicant has become trainee. This applicant data cannot be modify')

            # getting the object
            obj = course_applicant_query.first()
            
            if obj.employee.is_active==False:
                return errorMessage('Activate the employee first')

            # you can change the employee and session if you did not get the approval by management
            can_modify_employee_and_session = True


            # you cannot update the status to approve, rejected or waitlisted unless you get the decision by the respective management         
            # status could be changed to accepted, rejected or waitlisted if some decision exists   
            if 'status' in request.data:
                updated_status_choice = request.data['status'] 
                if updated_status_choice not in [1, 2]:
                    updated_status = self.update_course_applicant_status(updated_status_choice, course_applicant_id)
                    if updated_status['status'] == 400:
                        return Response(updated_status)

                   
            # if some decision exists then you cannot change the course session and the employee
            if obj.status in [3, 4, 5]:
                can_modify_employee_and_session = False

            # this checks whether active course session exists or not
            if can_modify_employee_and_session == True:
                # check if active course session exists or not
                if 'course_session' in request.data:
                    course_session_id = request.data['course_session']
                    course_session_query = CourseSessions.objects.filter(id=course_session_id, course__organization = organization_id)
                    if not course_session_query.exists():
                        return errorMessage("course_session does not exists")
                    if not course_session_query.filter(is_active=True).exists():
                        return errorMessage("course_session is inactive. Activate the course session first")

                    
                    # Assigning course id to course
                    course_session_obj = course_session_query.first()
                    course_id = course_session_obj.course.id
                    request.data['course'] = course_id
                
                # this checks whether active employee exists or not
                if 'employee' in request.data:
                    employee_id = request.data['employee']
                    employee_query = Employees.objects.filter(id=employee_id, organization=organization_id)
                    if not employee_query.exists():
                        return errorMessage('employee does not exists')
                    if not employee_query.filter(is_active=True).exists():
                        return errorMessage('employee is inactive. Activate the employee first')

                serializer = CourseApplicantsViewsetSerializers(obj, data=request.data, partial=True)
            else:
                serializer = UpdateCourseApplicantsViewsetSerializers(obj, data=request.data, partial=True)
      
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()


            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)


    def delete(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            course_applicant_id = self.kwargs['course_applicant_id']

            course_applicant_query = CourseApplicants.objects.filter(id=course_applicant_id, employee__organization=organization_id)
            if not course_applicant_query.exists():
                return errorMessage('course_applicant does not exists')
            
            # The applicant has become the trainee now
            if CourseSessionTrainees.objects.filter(course_applicant=course_applicant_id, course_applicant__employee__organization=organization_id).exists():
                return errorMessage({'This applicant has become trainee. This applicant data cannot be modify'})

            obj = course_applicant_query.first()
           
            if obj.is_active==False:
                return Response({'status': 200, 'system_status': 200, 'data': '', 'message': 'course_applicant is already deactivated', 'system_error_message': ''})

            obj.is_active=False
            obj.save()
            
            return Response({'status': 200, 'system_status': 200, 'data': '', 'message': 'course_applicant got deactivated successfully ', 'system_error_message': ''})

        except Exception as e:
            return exception(e)

    
    def decision_by_management(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            course_applicant_id = self.kwargs['course_applicant_id']

            # The applicant has become the trainee now
            if CourseSessionTrainees.objects.filter(course_applicant=course_applicant_id).exists():
                return errorMessage({'This applicant has become trainee. This applicant data cannot be modify'})

            if not 'decision_by' in request.data:
                return errorMessage('Decision by and decision status are required field')

            if not 'decision_status' in request.data:
                return errorMessage('Decision status is a required field')

            if not request.data['decision_status'] in [1, 2, 3]:
                return errorMessage("Invalid input. You have entered wrong choice.")

            course_applicant = CourseApplicants.objects.filter(id=course_applicant_id, employee__organization=organization_id)
            if not course_applicant.exists():
                return errorMessage('This course applicant does not exists at this id')
            if not course_applicant.filter(is_active=True):
                return errorMessage('This course applicant is deactivated at this id')

            course_applicant = course_applicant.first()
            

            # creating the logs
            message = 'Successfully Created'
            errors = ''
            logs_serializer = None
            applicant_logs = self.applicantLogs(request, course_applicant)
            if applicant_logs['status'] == 400:
                message = applicant_logs['message']
                errors = applicant_logs['system_error_message']
                
            logs_serializer = applicant_logs['data'] 
            if logs_serializer['decision_status'] == 1:
                course_applicant.status = 3
                course_applicant.save()
            elif logs_serializer['decision_status'] == 2:
                course_applicant.status = 4
                course_applicant.save()

            course_applicant_serializer = CourseApplicantsViewsetSerializers(course_applicant, many=False)

            return success(course_applicant_serializer.data)

        except Exception as e:
            return exception(e)


    def update_course_applicant_status(self, updated_status_choice, course_applicant_id):
        try:
            applicant_logs = CourseApplicantsLogs.objects.filter(course_applicant=course_applicant_id, is_active=True)
            if not applicant_logs.exists():
                return {'status': 400, 'system_status': 400, 'data': '', 'message': 'No application log exists. So you cannot modify the status', 'system_error_message': ''}


            if updated_status_choice == 3:
                is_approved_exists = False
                for decision_obj in applicant_logs:
                    if decision_obj.decision_status == 1:
                        is_approved_exists = True
                        decision_obj.log_status = 3
                        decision_obj.save()
                        break

                if is_approved_exists == False:
                    return {'status': 400, 'system_status': 400, 'data': '', 'message': 'You cannot change the status to approved. Unless someone on the management has approved that employee', 'system_error_message': ''}


            elif updated_status_choice == 4:
                is_rejected_exists = False
                for decision_obj in applicant_logs:
                    if decision_obj.decision_status == 2:
                        is_rejected_exists = True
                        decision_obj.log_status = 4
                        decision_obj.save()
                        break
                
                if is_rejected_exists == False:
                    return {'status': 400, 'system_status': 400, 'data': '', 'message': 'You cannot change the status to rejected. Unless someone on the management has rejected that employee', 'system_error_message': ''}

            elif updated_status_choice == 5:
                is_decision_exists = False
                for decision_obj in applicant_logs:
                    if decision_obj.decision_status == 1:
                        is_decision_exists=True
                        decision_obj.log_status=5
                        decision_obj.save()
                        break
                if is_decision_exists == False:
                    return {'status': 400, 'system_status': 400, 'data': '', 'message': 'You cannot change the status to waitlist. As no one has made approval to the application', 'system_error_message': ''}
                
            return {'status': 200}
        except Exception as e:
            return {'status': 400, 'system_status': 400, 'data': '', 'message': '', 'system_error_message': str(e)}



    def applicantLogs(self, request, course_applicant):
        try:
            log_status = course_applicant.status
            course_applicant_id = course_applicant.id  
            last_log = CourseApplicantsLogs.objects.filter(course_applicant=course_applicant.id)

            # The applicant has become the trainee now
            if CourseSessionTrainees.objects.filter(course_applicant=course_applicant_id).exists():
                return errorMessage({'This applicant has become trainee. This applicant data cannot be modify'})
            
            # update if that decision_by already exists
            if 'decision_by' in request.data:
                decision = request.data['decision_by']
                if last_log.filter(decision_by=decision).exists():
                    last_log = last_log.first()
                    course_applicant_serializer = CourseApplicantsLogsViewsetSerializers(last_log, data = request.data, partial=True)
                    if course_applicant_serializer.is_valid():
                        course_applicant_serializer.save()                  

                        return {'status': 200, 'system_status': 200, 'data': course_applicant_serializer.data, 'message': 'Logs successfully updated', 'system_error_message': course_applicant_serializer.errors}
                            
                    return {'status': 400, 'system_status': 400, 'data': '', 'message': 'Applicant is successfully updated. However, ValidationError is faced while creating logs', 'system_error_message': course_applicant_serializer.errors}


            # create if decision does not exists
            decision_status=3
            course_applicant_array = {
                'course_applicant': course_applicant_id, 
                'log_status': log_status,
                'decision_status': decision_status,
                'decision_by': None,
                'decision_reason': None    
            }
            if 'decision_status' in request.data:
                course_applicant_array['decision_status'] = request.data['decision_status']
                if decision_status == 1:
                    course_applicant_array['log_status'] = 3
                elif decision_status == 2:
                    course_applicant_array['log_status'] = 4
            
            if 'decision_by' in request.data:
                course_applicant_array['decision_by'] = request.data['decision_by']
            if 'decision_reason' in request.data:
                course_applicant_array['decision_reason'] = request.data['decision_reason']

            course_applicant_serializer = CourseApplicantsLogsViewsetSerializers(data = course_applicant_array)
            if course_applicant_serializer.is_valid():
                course_applicant_serializer.save()                  

                return {'status': 200, 'system_status': 200, 'data': course_applicant_serializer.data, 'message': 'Logs successfully created', 'system_error_message': course_applicant_serializer.errors}
                    
            return {'status': 400, 'system_status': 400, 'data': '', 'message': 'Applicant is successfully created. However, ValidationError is faced while creating logs', 'system_error_message': course_applicant_serializer.errors}
        except Exception as e:
            print(str(e))
            return {'status': 400, 'system_status': 400, 'data': '', 'message': 'Applicant is successfully created. However, SystemErrorMessage is faced while creating logs', 'system_error_message': str(e)}



class PreCourseApplicantDataView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            data = {'course_session': None, 'employee': None}

            course_session = CourseSessions.objects.filter(course__organization=organization_id, is_active=True)
            course_session_serializer = CourseSessionsViewsetSerializers(course_session, many=True)
            data = {'course_session': course_session_serializer.data}

            emp = Employees.objects.filter(organization=organization_id, is_active=True)
            emp_serializer = PersonalEmployeeViewsetSerializers(emp, many=True)
            data = {'employee': emp_serializer.data} 

            return success(data)
        except Exception as e:
            return exception(e)
        

class CourseApplicantPortalViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']

            registered_course_sessions = CourseApplicants.objects.filter(employee=employee_id, employee__organization=organization_id)     

            cs = CourseSessions.objects.filter(course__organization=organization_id, is_active=True)
            cs_serializer = CourseSessionsApplicantViewsetSerializers(cs, 
                context={'registered_course_sessions': registered_course_sessions}, 
                many=True
            )

            data = {
                'course_session': cs_serializer.data
            }
            return success(data)
        except Exception as e:
            return exception(e)

    # Employee applying for the course_session from his portal
    def application_for_course(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']

            course_session_id = self.kwargs['course_session_id']
            
            employee = Employees.objects.get(id=employee_id, organization=organization_id)
            
            # emp object
            emp = employee
            
            course_session = CourseSessions.objects.filter(id=course_session_id, course__organization=organization_id)
            if not course_session.exists():
                return errorMessage("Course Session does not exists")
            elif course_session.filter(session_status='Completed').exists():
                return errorMessage("This session is already completed")
            
            if CourseApplicants.objects.filter(course_session=course_session_id, employee=employee_id).exists():
                return errorMessage(f"{emp.name} you are already registered for the session")

            cs_obj = course_session.get()
            course_id = cs_obj.course.id
            request.data['date'] = datetime.date.today()
            request.data['course_session'] = course_session_id
            request.data['course'] = course_id
            request.data['employee'] = employee_id
            request.data['status'] = 1
            serializer = CourseApplicantsViewsetSerializers(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)   
            serializer.save()
            return successfullyCreated(serializer.data)            
        except Exception as e:
            return exception(e)
        

    # def cancle_application_for_course(self, request, *args, **kwargs):
    #     try:
    #         token_data = decodeToken(self, self.request)
    #         organization_id = token_data['organization_id']
    #         employee_id = token_data['employee_id']

    #         course_session_id = self.kwargs['course_session_id']
            
    #         employee = Employees.objects.get(id=employee_id, organization=organization_id)
            
    #         # emp object
    #         emp = employee
            
    #         course_session = CourseSessions.objects.filter(id=course_session_id, course__organization=organization_id)
    #         if not course_session.exists():
    #             return errorMessage("Course Session does not exists")
    #         elif course_session.filter(session_status='Completed').exists():
    #             return errorMessage("This session is already completed")
            
    #         course_applicant = CourseApplicants.objects.filter(course_session=course_session_id, employee=employee_id)
    #         if not course_applicant.exists():
    #             return errorMessage('Applicant is not registered in this course session')
    #         if course_applicant.filter(is_trainee=True).exists():
    #             return errorMessage('Applicant is trainee you cannot unregistered now')
            
    #         obj = course_applicant.get()
    #         obj.is_submitted = False
    #         obj.is_active = False
    #         obj.save()

    #         serializer = CourseApplicantsViewsetSerializers(data = request.data)
    #         if not serializer.is_valid():
    #             return serializerError(serializer.errors)   
    #         serializer.save()
    #         return successfullyCreated(serializer.data)            
    #     except Exception as e:
    #         return exception(e)
        