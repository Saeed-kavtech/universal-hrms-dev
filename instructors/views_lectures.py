from rest_framework.response import Response
from rest_framework import generics
from rest_framework import viewsets
from .serializers import *
from helpers.status_messages import *
from helpers.custom_permissions import IsAuthenticated, DoesOrgExists
from .models import *
import datetime

class LecturesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def listAllLectures(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
    
            obj = Lectures.objects.filter(course_session_instructor__course_session__course__organization=user_organization.id, is_active=True)
            serializer = LecturesViewsetSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def list(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            course_session_id = self.kwargs['course_session_id']
    
            cs_obj =  CourseSessions.objects.filter(id =course_session_id, course__organization=user_organization.id)
            if not cs_obj.exists():
                return errorMessage('Course Session Instructor does not exists')
            if not cs_obj.filter(is_active=True).exists():
                return errorMessage('Course Session Instructor is deactivated')
        
            obj = Lectures.objects.filter(course_session_instructor__course_session=course_session_id, course_session_instructor__course_session__course__organization=user_organization.id, course_session_instructor__is_active=True, is_active=True).order_by('id')
            serializer = LecturesViewsetSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def retrieve(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            lecture_id = self.kwargs['lecture_id']

            query = Lectures.objects.filter(id=lecture_id, course_session_instructor__course_session__course__organization=user_organization.id)
            if not query.exists():
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'This lecture does not exists', 'system_error_message': ''})
            if query.filter(is_active=False).exists():
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'The lecture is deactivated', 'system_error_message': ''})

            obj = query.first()
            if obj.course_session_instructor.is_active == False:
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Activate the course session instructor first', 'system_status_message': ''})

            serializer = LecturesViewsetSerializers(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def create(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            course_session_id = self.kwargs['course_session_id']
            query = CourseSessions.objects.filter(id=course_session_id, course__organization=user_organization.id)

            if not query.exists():
                return errorMessage("This course session does not exists")
            if not query.filter(is_active=True).exists():
                return errorMessage('This course session is deactivated')
 
            csi = CourseSessionInstructors.objects.filter(course_session=course_session_id, course_session__course__organization=user_organization.id)
            if not csi.exists():
                return errorMessage("First add session instructor. No course session instructor exists")
            if not csi.filter(is_active=True).exists():
                return errorMessage("No active course session instructor exists")

            csi_obj = csi.filter(is_active=True).first()
            course_session = query.first()
            total_lectures = course_session.total_lectures
            
            if total_lectures == None:
                return errorMessage("Please define the total number of lectures first in the course session")
    
            lecture_query = Lectures.objects.filter(course_session_instructor = csi_obj.id, course_session_instructor__course_session__course__organization=user_organization.id)

            # TODO inside a function
            if lecture_query.exists():
                return errorMessage("Lectures already created")

            lectures_data = []
            for i in range(1, course_session.total_lectures + 1):
                if lecture_query.filter(lecture_no=i, is_active=True).exists():
                    continue
                elif lecture_query.filter(lecture_no=i).exists():
                    lecture_obj = lecture_query.first()
                    lecture_obj.is_active=True
                    lecture_obj.save()
                    continue

                lectures = Lectures.objects.create(
                    course_session_instructor = csi_obj,
                    lecture_no = i,
                    title = 'title {}'.format(i),
                    description = 'description {}'.format(i),
                    status = 2 # Not Scheduled
                )
                lectures.save()
                cs_lectures = CreateLecturesViewsetSerializers(lectures, many=False).data
                lectures_data.append(cs_lectures)
             
            return successfullyCreated(lectures_data)

        except Exception as e:
            return exception(e)


    def patch(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            lecture_id = self.kwargs['lecture_id']

            query = Lectures.objects.filter(id=lecture_id, course_session_instructor__course_session__course__organization=user_organization.id)
            
            if not query.exists():
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'This lecture does not exists', 'system_error_message': ''})

            obj = query.first()
            # once  the status is completed data cannot get updated
            if obj.status == 4:
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Lecture cannot be updated now as its status is completed', 'system_status_message': ''})


            if obj.course_session_instructor.is_active == False:
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Activate the course session instructor first', 'system_status_message': ''})

            # If course_session_instructor id is provided. This would check if active course session instructor exists or not
            if 'course_session_instructor' in request.data:
                course_session_instructor_id = request.data['course_session_instructor']
                
                if course_session_instructor_id != obj.course_session_instructor.id:
                    course_session_instructor_query = CourseSessionInstructors.objects.filter(id=course_session_instructor_id)
                    if not course_session_instructor_query.exists():
                        return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'The course session instructor does not exist', 'system_status_message': ''})
                    if not course_session_instructor_query.filter(is_active=True).exists():
                        return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'The course session instructor is inactive', 'system_status_message': ''})

                # if course session instructor is changed
                prev_cs = obj.course_session_instructor.course_session.id
                new_obj = course_session_instructor_query.first()
                current_cs = new_obj.course_session.id
                if prev_cs != current_cs:
                    return errorMessage("You cannot change the course session once assigned")

            # status can't be changed to completed if date and time is not entered
            if 'status' in request.data:
                if request.data['status'] == 4:
                    if 'date' not in request.data:
                        if obj.date==None:
                            return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Status cannot be change to completed unless you entered the date', 'system_status_message': ''})
                    elif 'time' not in request.data:
                        if obj.start_time == None:
                            return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Status cannot be change to completed unless you entered the time', 'system_status_message': ''})
            
            # If the date is set then the lecture is scheduled
            if 'date' in request.data:
                date = datetime.datetime.strptime(request.data['date'], '%Y-%m-%d').date()
                if not date >= datetime.date.today():
                    return errorMessage('Date should be greater than the current date')
                obj.status = 1    
            
            serializer = LecturesViewsetSerializers(obj, data=request.data, partial=True)

            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()
            
            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)


    def delete(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            lecture_id = self.kwargs['lecture_id']
            
            query = Lectures.objects.filter(id=lecture_id, course_session_instructor__course_session__course__organization=user_organization.id)
            
            if not query.exists():
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'This lecture does not exists', 'system_error_message': ''})

            obj = query.first()

            if obj.is_active == False:
                return Response({'status': 200, 'system_status': 200, 'data': '', 'message': 'This Lecture is already deactivated', 'system_error_message': ''})
            
            obj.is_active=False
            obj.save()
            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT,  'data': '', 'message': 'Successfully Deleted', 'system_status_message': ''})

        except Exception as e:
            return exception(e)



    

class PreLecturesDataView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def get(self, request, *args, **kwargs):
        try:
            result_data = {'courses_session_instructors': None, 'mode_of_instruction': None}

            user_organization = request.data.get('organization_profile')
            organization_id = user_organization.id

            course_session_instructor_obj = CourseSessionInstructors.objects.filter(course_session__course__organization=organization_id, is_active=True)
            if course_session_instructor_obj.exists():
                session_instructor_serializer = CourseSessionInstructorsViewsetSerializers(course_session_instructor_obj, many=True)
                result_data['courses_session_instructors'] = session_instructor_serializer.data

            mode_obj = ModeOfInstructions.objects.filter(is_active=True) 
            if mode_obj.exists():
                mode_serializer = ModeOfInstructionsViewsetSerializers(mode_obj, many=True)
                result_data['mode_of_instruction'] = mode_serializer.data

            return Response({'status': 200, 'system_status': 200, 'data': result_data, 'message': 'Success', 'system_status_message': ''})


        except Exception as e:
            return exception(e)