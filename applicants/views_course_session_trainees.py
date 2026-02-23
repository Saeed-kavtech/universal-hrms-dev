from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import viewsets
from helpers.decode_token import decodeToken
from .serializers import *
from .models import *
from helpers.status_messages import *
from helpers.custom_permissions import IsAuthenticated, DoesOrgExists
import json

# Create your views here.
class CourseSessionTraineesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def list(self, request, *args, **kwargs):
        try:   
            user_organization = request.data.get('organization_profile')
            # course session trainee id
            course_session_id = self.kwargs['course_session_id']
            query = CourseSessionTrainees.objects.filter(course__organization=user_organization.id, course_applicant__employee__is_active=True, course_session=course_session_id, is_active=True).order_by('-id')
            serializer = CourseSessionTraineesViewsetSerializers(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def retrieve(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            course_session_trainee_id = self.kwargs['course_session_trainee_id']

            query = CourseSessionTrainees.objects.filter(id=course_session_trainee_id, course__organization=user_organization.id)
            if not query.exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Trainee does not exists', 'system_status_message': ''})

            if not query.filter(is_active=True):
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Trainee is deactivated', 'system_status_message': ''})

            obj = query.first()
            if obj.course_applicant.employee.is_active==False:
                return errorMessage("Employee is deactivated. Activate the employee first")

            serializer = CourseSessionTraineesViewsetSerializers(obj)
            
            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def create(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            course_applicant_id = self.kwargs['course_applicant_id']

            course_applicant_query = CourseApplicants.objects.filter(id=course_applicant_id, course__organization=user_organization.id)
            if not course_applicant_query.exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'course_applicant does not exists at this id', 'system_status_message': ''})
            if not course_applicant_query.filter(is_active=True).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'course_applicant is inactive at this id', 'system_status_message': ''})
            
            request.data['course_applicant'] = course_applicant_id
            
            obj = course_applicant_query.first()

            # checks if employee is active or not
            if obj.employee.is_active==False:
                return errorMessage('Employee is deactivated. Activate the employee first')
            
            applicant_status = obj.status
            if applicant_status != 3:
                if applicant_status == None:
                    return errorMessage('This applicant, application is still pending. First approve it by team lead and HR', 'system_status_message')
                elif applicant_status == 4:
                    return errorMessage('This applicant, application is rejected')
                elif applicant_status == 5:
                    return errorMessage('This applicant, application is currently waitlisted')
                else:
                    return errorMessage('This applicant is currently unapproved')
            else:
                pass
                #TODO if applicant is waitlisted
                # if 'applicant_status' in request.data:
                #     obj.applicant_status = 5
                #     obj.save 
                #     applicant_serializer = CourseApplicantsViewsetSerializers(obj)
                #     applicant_log = CourseApplicantsLogs.objects.filter(id = course_applicant_id, log_status=obj.status, is_active=True)
                #     applicant_log_serializer = CourseApplicantsLogsViewsetSerializers(applicant_log)
                #     data = {'course_applicant': applicant_serializer.data, 'applicant_log': applicant_log_serializer.data}
                #     return success(data)

            request.data['course'] = obj.course.id
            course_session_id = obj.course_session.id
            request.data['course_session'] = course_session_id

            cst = CourseSessionTrainees.objects.filter(course_applicant=course_applicant_id, course_session=course_session_id, course__organization=user_organization.id)
            if cst.filter(is_active=True).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'This user is already registered as trainee', 'system_status_message': ''})
            elif cst.exists():
                cst_obj = cst.first()
                cst_obj.is_active=True
                cst_obj.save()
                serializer = CourseSessionTraineesViewsetSerializers(cst)
                return success(serializer.data)

            serializer = CourseSessionTraineesViewsetSerializers(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)

        except Exception as e:
            return exception(e)


    def patch(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            course_session_trainee_id = self.kwargs['course_session_trainee_id']

            query = CourseSessionTrainees.objects.filter(id=course_session_trainee_id, course__organization=user_organization.id)
            if not query.exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Trainee does not exists', 'system_status_message': ''})

            obj = query.first()

            # checks if employee is deactivated or not
            if obj.course_applicant.employee.is_active==False:
                return errorMessage('Activate the employee first')

            serializer = UpdateCourseSessionTraineesViewsetSerializers(obj, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()
            
            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)


    def delete(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            course_session_trainee_id = self.kwargs['course_session_trainee_id']

            query = CourseSessionTrainees.objects.filter(id=course_session_trainee_id, course__organization=user_organization.id)
            if not query.exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Trainee does not exists', 'system_status_message': ''})

            if not query.filter(is_active=True):
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Trainee is deactivated', 'system_status_message': ''})

            obj = query.first()

            # employee is deactivated
            if obj.course_applicant.employee.is_active==False:
                return errorMessage('Activate the employee first')
        
            obj.is_active = False
            obj.save()
            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT,  'data': '', 'message': 'Successfully Deleted', 'system_status_message': ''})

        except Exception as e:
            return exception(e)


class MultipleTraineeSelectionViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def create_multiple_trainees(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            if organization_id == None:
                return errorMessage("User has no organization in the logs")
            course_session_id = self.kwargs['course_session_id']
            trainee_data_list = request.data
            trainee_data = self.multipleTraineeData(trainee_data_list, course_session_id, organization_id)

            if trainee_data['code'] == 400:
                return errorMessage(trainee_data['message'])
            
            return success(trainee_data['message'])
            
        except Exception as e:
            return exception(e)


    def multipleTraineeData(self, trainees_data, course_session_id, organization_id):
        trainees = []
        serializer_errors = []
        response = {'code': 200, 'message': '', 'system_error': ''}
        if isinstance(trainees_data, str):
            trainees_data = json.loads(trainees_data)
            trainees.append(trainees_data)
        else:
            trainees = trainees_data
        
        
        try:
            trainee_array = {
                'id': '',
                'course': '',
                'course_session': course_session_id,
                'course_applicant': '',
                'is_trainee': True
            }
            if trainees is not None:
                for trainee in trainees:
                    if 'course_applicant' in trainee:
                        cst = CourseSessionTrainees.objects.filter(course_applicant=trainee['course_applicant'], course_session=course_session_id, course__organization=organization_id)
                        # if trainee already exists
                        if cst.exists():
                            if cst.filter(is_active=False):
                                obj_cst = cst.first()
                                obj_cst.is_active = True
                                obj_cst.save()
                            continue

                        applicant_query = CourseApplicants.objects.filter(id=trainee['course_applicant'], course_session=course_session_id, course__organization=organization_id, employee__is_active=True)
                        if not applicant_query.exists():
                            response['code'] = 400
                            response['message'] = 'Applicant does not exists'
                            return response
                        if not applicant_query.filter(status=3).exists():
                            response['code'] = 400
                            response['message'] = 'Applicant is not approved'          
                            return response
                    else:
                        continue
                    
                    

                    obj = applicant_query.first()
                    trainee_array['course'] = obj.course.id
                    trainee_array['course_applicant'] = obj.id
                    

                    serializer = CourseSessionTraineesViewsetSerializers(data=trainee_array)

                    if serializer.is_valid():
                        serializer.save()
                        # make trainee
                        obj.is_trainee=True
                        obj.save()
                    else:
                        serializer_errors.append(serializer.errors)
                
                if (len(trainees) == len(serializer_errors)):
                    response['message'] = "No trainee data processed, please update it again!"
                elif len(serializer_errors) > 0:
                    response['message'] = "Some of the trainee data is processed, please update it again!"
                else:
                    response['message'] = "All of the trainee data is processed Successfully."
                    response['code'] = 200
            else:
                response['message'] = "No data found"

            return response
        except Exception as e:
            response['code'] = 400
            response['message'] = str(e)
            return response   



class PreCourseSessionTraineesDataView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def get(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            course_session_id = self.kwargs['course_session_id']

            course_applicant = CourseApplicants.objects.filter(course_session=course_session_id, employee__is_active=True, employee__organization=user_organization.id, is_active=True)
            course_applicant_serializer = CourseApplicantsViewsetSerializers(course_applicant, many=True)
            data = {'course_applicants': course_applicant_serializer.data} 

            return success(data)
        except Exception as e:
            return exception(e)