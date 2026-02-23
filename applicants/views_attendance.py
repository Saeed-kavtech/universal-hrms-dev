from django.shortcuts import render
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import viewsets
from .serializers import *
from .models import *
from helpers.status_messages import *
from helpers.custom_permissions import IsAuthenticated, DoesOrgExists
from instructors.models import Lectures
from instructors.serializers import LecturesViewsetSerializers, ModeOfInstructionsViewsetSerializers
import datetime

# Create your views here.
class CourseSessionTraineeAttendanceViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def list(self, request, *args, **kwargs):
        try:  
            user_organization = request.data.get('organization_profile')
            lecture_id = self.kwargs['lecture_id']

            # if lecture exists or not
            lecture = Lectures.objects.filter(id=lecture_id, course_session_instructor__course_session__course__organization=user_organization.id)
            if not lecture.exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Lecture does not exists', 'system_status_message': ''})
            elif not lecture.filter(is_active=True).exists():
                return {'status':400, 'system_status': 400, 'data': '', 'message': 'lecture is deactivate at this id', 'system_error_message': ''}
            
            lecture = lecture.first()
            lecture_serializer = LecturesViewsetSerializers(lecture)
            cs_id = lecture.course_session_instructor.course_session.id
            
            query =  CourseSessionTraineeAttendance.objects.filter(lecture=lecture_id, course_session_trainee__course_session=cs_id, course_session_trainee__course_session__course__organization=user_organization.id, is_active=True).order_by('id') 
            if not query.exists():
                return errorMessage("Attendance does not exists")
            serializer = CourseSessionTraineeAttendanceViewsetSerializers(query, many=True)


            result = {'attendance': serializer.data, 'lectures': lecture_serializer.data}

            return success(result)
        except Exception as e:
            return exception(e)


    def retrieve(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            cst_attendance_id = self.kwargs['cst_attendance_id']
            
            cst_attendance = CourseSessionTraineeAttendance.objects.filter(id=cst_attendance_id, course_session_trainee__course_session__course__organization=user_organization.id)
            if not cst_attendance.exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'No attendance exists at this id', 'system_status_message': ''})
            if not cst_attendance.filter(is_active=True):
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'No active attendance exists', 'system_status_message': ''})


            obj = cst_attendance.first()
            serializer = CourseSessionTraineeAttendanceViewsetSerializers(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def patch(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            cst_attendance_id = self.kwargs['cst_attendance_id']
            
            cst_attendance = CourseSessionTraineeAttendance.objects.filter(id=cst_attendance_id, course_session_trainee__course_session__course__organization=user_organization.id)
            if not cst_attendance.exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'No attendance exists at this id', 'system_status_message': ''})
            
            flag = 0
            if 'is_active' in request.data:
                if request.data['is_active'] == True:
                    flag=1
                    attendance_activate = cst_attendance.first()
                    attendance_activate.is_active=True
                    attendance_activate.save()
            else:
                if flag != 1:
                    if not cst_attendance.filter(is_active=True):
                        return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'No active attendance exists', 'system_status_message': ''})


            obj = cst_attendance.first()
            request.data['date'] = datetime.date.today()
            
            serializer = CourseSessionTraineeAttendanceViewsetSerializers(obj, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()
            
            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)


    def delete(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            cst_attendance_id = self.kwargs['cst_attendance_id']
            cst_attendance = CourseSessionTraineeAttendance.objects.filter(id=cst_attendance_id, course_session_trainee__course_session__course__organization=user_organization.id)
            if not cst_attendance.exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'No attendance exists at this id', 'system_status_message': ''})
            if not cst_attendance.filter(is_active=True):
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'No active attendance exists', 'system_status_message': ''})


            obj = cst_attendance.first()
            if obj.is_active==False:
                return Response({'status':400, 'system_status': 400, 'data': '', 'message': 'Attendance at this id is already deactivated', 'system_status_message': ''})
            
            obj.is_active = False
            obj.save()
            return Response({'status':200, 'system_status': 200, 'data': '', 'message': 'Successfully deactivated', 'system_status_message': ''})
        except Exception as e:
            return exception(e)



    def start_lecture(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            lecture_id = self.kwargs['lecture_id']

            lecture_data = self.lectureChecks(lecture_id, user_organization.id)
            if lecture_data['status'] == 400:
                return Response(lecture_data)

            lecture = lecture_data['data']

            cs_id = lecture.course_session_instructor.course_session.id

            # if course session trainee exists or not
            cst_query = CourseSessionTrainees.objects.filter(course_session=cs_id, course_applicant__employee__is_active=True, course__organization=user_organization.id)
            if not cst_query.exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Course Session Trainee does not exists', 'system_status_message': ''})
            if not cst_query.filter(is_active=True).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Course Session Trainee is deactivated', 'system_status_message': ''})


            
            attendance_data = []
            # if lecture has already started
            total_count = CourseSessionTraineeAttendance.objects.filter(lecture=lecture, course_session_trainee__course__organization=user_organization.id)
            if total_count.count() == total_count.filter(is_active=True).count() and total_count.count() > 0:
                attendance_serializer = CourseSessionTraineeAttendanceViewsetSerializers(total_count, many=True)
                lecture_serializer = LecturesViewsetSerializers(lecture) 
                result = {'attendance': attendance_serializer.data, 'lectures': lecture_serializer.data}
                return Response({'status': 200, 'system_status': '', 'data': result, 'message': 'You have already started the Lecture', 'system_status_message': ''})


            for obj in cst_query:
                cst_id = obj.id
                cst = CourseSessionTrainees.objects.get(id=cst_id, course_applicant__employee__is_active=True, course__organization=user_organization.id)
                
                # session trainee
                session_trainee = CourseSessionTraineeAttendance.objects.filter(lecture=lecture, course_session_trainee=cst,  course_session_trainee__course__organization=user_organization.id)
                if session_trainee.filter(is_active=True).exists():
                    continue                   
                # is active turned to true
                elif session_trainee.filter(is_active=False):
                    session_trainee = session_trainee.first()
                    session_trainee.is_active=True
                    session = session_trainee.save()
                    session = CourseSessionTraineeAttendanceViewsetSerializers(attendance, many=False).data
                    attendance_data.append(session)

                attendance = CourseSessionTraineeAttendance.objects.create(
                    lecture=lecture,
                    course_session_trainee=cst,
                    attendance_status=None,
                    is_active=True
                )
                attendance.save()
                cs_trainee = CourseSessionTraineeAttendanceViewsetSerializers(attendance, many=False).data
                # changing the lecture status to inprogress
                lecture.status = 3
                lecture.save()
                attendance_data.append(cs_trainee)

            # when lecture is started session status moved to in progress   
            if lecture.lecture_no == 1:
                cs = CourseSessions.objects.filter(id=cs_id)
                if cs.exists():
                    cs_obj = cs.first()
                    cs_obj.session_status = 'InProgress'
                    cs_obj.save()

            lecture_serializer = LecturesViewsetSerializers(lecture) 
            result = {'attendance': attendance_data, 'lectures': lecture_serializer.data}
                
            return Response({'status': 200, 'system_status': '', 'data': result, 'message': '', 'system_status_message': ''})
        except Exception as e:
            return exception(e)


    def end_lecture(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            lecture_id = self.kwargs['lecture_id']

            # checks if lectures exists or not
            lecture = Lectures.objects.filter(id=lecture_id, course_session_instructor__course_session__course__organization=user_organization.id)
            if not lecture.exists():
                return errorMessage("Lecture does not exists")
            elif not lecture.filter(is_active=True).exists():
                return errorMessage("lecture is deactivate at this id")

            lecture_obj = lecture.first()
           
            # getting lecture id from lecture objects
            cs_id = lecture_obj.course_session_instructor.course_session.id

            # if course session trainee exists or not
            cst_query = CourseSessionTrainees.objects.filter(course_session=cs_id, course_applicant__employee__is_active=True, course__organization=user_organization.id)
            if not cst_query.exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Course Session Trainee does not exists', 'system_status_message': ''})
            if not cst_query.filter(is_active=True).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Course Session Trainee is deactivated', 'system_status_message': ''})
            
            attendance_query = CourseSessionTraineeAttendance.objects.filter(lecture=lecture_id, course_session_trainee__course_session=cs_id, course_session_trainee__course__organization=user_organization.id)
            if attendance_query.filter(is_active=False):
                return errorMessage("kindly, change the status of trainee to activate first")
            if attendance_query.filter(attendance_status=None):
                return errorMessage("Kindly, mark all the attendance first")

            if lecture_obj.status == 4:
                
                return Response({'status': 200, 'system_status': 200, 'data': '', 'message': 'Previous lecture status is already changed to completed', 'system_status_message': ''})



            message = 'Success'
            if lecture_obj.status == 3:
                lecture_obj.status = 4
                lecture_obj.is_taken = True
                lecture_obj.save()
            else:
                return errorMessage('Lecture is not yet started. Kindly change the status to complete first')


            # getting total lectures and lecture number from lectures
            total_lectures = lecture_obj.course_session_instructor.course_session.total_lectures
            lecture_number = lecture_obj.lecture_no
            # This will change the status of course session to 
            if lecture_number == total_lectures:
                cs_query = CourseSessions.objects.filter(id=cs_id, is_active=True)
                if cs_query.exists():
                    cs_obj = cs_query.first()
                    cs_obj.session_status = "Completed"
                    cs_obj.save()

            lecture_serializer = LecturesViewsetSerializers(lecture_obj)
            return Response({'status': 200, 'system_status': '', 'data': lecture_serializer.data, 'message': message, 'system_status_message': ''})
        except Exception as e:
            return exception(e)


    def lectureChecks(self, lecture_id, organization_id):
        try:
            # if lecture exists or not
            lecture = Lectures.objects.filter(id=lecture_id, course_session_instructor__course_session__course__organization=organization_id)
            if not lecture.exists():
                return {'status': 400, 'system_status': 400, 'data': '', 'message': 'Lecture does not exists', 'system_status_message': ''}
            elif not lecture.filter(is_active=True).exists():
                return {'status':400, 'system_status': 400, 'data': '', 'message': 'lecture is deactivate at this id', 'system_error_message': ''}

            lecture_obj = lecture.first()


            lecture_number = lecture_obj.lecture_no

            csi_id = lecture_obj.course_session_instructor.id
            # if the previous lecture status is not yet completed
            if lecture_number != 1:
                prev_lecture = lecture_number-1
                prev_lecture = Lectures.objects.filter(course_session_instructor=csi_id, lecture_no=prev_lecture)           
                prev_lecture_obj = prev_lecture.first()
                if prev_lecture_obj.status != 4:
                    return {'status':400, 'system_status': 400, 'data': '', 'message': 'Kindly mark the status of previous lecture as complete first', 'system_error_message': ''}
            
            if lecture_obj.date == None:
                return {'status':400, 'system_status': 400, 'data': '', 'message': 'Lecture is not assigned any date yet. Please update that date first', 'system_error_message': ''}
            elif lecture_obj.start_time == None:
                return {'status':400, 'system_status': 400, 'data': '', 'message': 'Lecture is not assigned any time yet. Please update lecture time first', 'system_error_message': ''}
            
            # elif lecture.date < datetime.date.today():
            #     return {'status':400, 'system_status': 400, 'data': '', 'message': 'Lecture has not yet started', 'system_error_message': ''}
            
            return {'status':200, 'system_status': 200, 'data': lecture_obj, 'message': '', 'system_error_message': ''}
        except Exception as e:
            return {'status':400, 'system_status': 400, 'data': '', 'message': '', 'system_error_message': str(e)}



 
    def isLectureStarted(self, lecture_date):
        try:
            if lecture_date < datetime.date.today():
                return True
            return False

        except Exception as e:
            return str(e)
   
    


class PreAttendanceDataView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def get(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            lecture_id = self.kwargs['lecture_id']

            result = {'lectures': None, 'course_session_trainee': None, 'mode_of_instructions': None}

            lecture_query = Lectures.objects.filter(id=lecture_id, is_active=True)
            lecture_serializer = LecturesViewsetSerializers(lecture_query, many=True)
            result['lectures'] = lecture_serializer.data

            if not lecture_query.exists():
                return errorMessage('No active lectures exists at this id')
                
            lecture_obj = lecture_query.first()
            cs_id = lecture_obj.course_session_instructor.course_session.id
            obj = CourseSessionTrainees.objects.filter(course_session=cs_id, is_active=True)
            serializer = CourseSessionTraineesViewsetSerializers(obj, many=True)
            result['course_session_trainee'] = serializer.data

            mode_query = ModeOfInstructions.objects.all()
            mode_serializer = ModeOfInstructionsViewsetSerializers(mode_query, many=True)
            result['mode_of_instructions'] = mode_serializer.data

            return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': result, 'message': 'Success', 'system_error_message': ''})

        except Exception as e:
            return exception(e)
