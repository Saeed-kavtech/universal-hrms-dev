from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics
from helpers.custom_permissions import IsAuthenticated, DoesOrgExists
from rest_framework import viewsets
from .serializers import *
from helpers.status_messages import *
from .models import *
from courses.models import Courses
from courses.serializers import CoursesViewsetSerializers
from applicants.models import CourseSessionTrainees
import datetime


class SessionInstructorsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def list(self, request, *args, **kwargs):
        try:      
            user_organization = request.data.get('organization_profile')
            is_session_exists = CourseSessions.objects.filter(course__organization = user_organization.id, is_active=True).order_by('id')
            serializer = SessionInstructorsSerializers(is_session_exists, many=True)

            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Success', 'system_status_message': ''})
        except Exception as e:
            return exception(e)
    

    def retrieve(self, request, *args, **kwargs):
        try:   
            #check whether organization exists or not         
            user_organization = request.data.get('organization_profile')

            course_session_id = self.kwargs['course_session_id'] 
            
            is_session_exists = CourseSessions.objects.filter(id = course_session_id, course__organization = user_organization.id)
            if not is_session_exists.exists():
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'Course session does not exists', 'system_error_message': ''})
            elif not is_session_exists.filter(is_active=True).exists():
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'Course session is not active', 'system_error_message': ''})

            session_obj = is_session_exists.first()
            

            session_instructor_serializer = SessionInstructorsSerializers(session_obj)
           
            return Response({'status': 200, 'system_status': 200, 'data': session_instructor_serializer.data, 'message': 'Success', 'system_status_message': ''})

        except Exception as e:
            return exception(e)   


    def create(self, request, *args, **kwargs):
        try:   
            #check whether organization exists or not         
            user_organization = request.data.get('organization_profile')
            organization_id = user_organization.id
   
            # assigning course id via request.data
            if not 'course' in request.data:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'The course is a required field', 'system_error_message': ''})
            
            # TODO in a function
            # date checks
            if 'start_date' in request.data:
                current_date=datetime.date.today()
                start_date = datetime.datetime.strptime(request.data['start_date'], '%Y-%m-%d').date()
                if not start_date >= current_date:
                    return errorMessage('start_date should be greater than or equal to the current date')

                if 'end_date' in request.data:
                    end_date = datetime.datetime.strptime(request.data['end_date'], '%Y-%m-%d').date()
                    if not end_date >= start_date:
                        return errorMessage('End date should be greater than equal to the current date')
                    
                    duration = end_date - start_date
                    request.data['duration'] = str(duration.days) + ' days'


            request.data['session_status'] = 'Not initiated'
            course_id = request.data['course']

            # checks whether active course exists or not
            query = Courses.objects.filter(id=course_id, organization=organization_id)
            if not query.exists():
                return Response({'status': 400, 'system_status':400, 'data': '', 'message': 'This course does not exists', 'system_error_message': '' })
            if not query.filter(is_active=True).exists():
                return Response({'status': 400, 'system_status':400, 'data': '', 'message': 'The Course is deactivated. Activate the course first', 'system_error_message': '' })
       
            # This would store the course session data
            course_session_serializer = CourseSessionsViewsetSerializers(data=request.data)
            if not course_session_serializer.is_valid():
                return serializerError(course_session_serializer.errors)
            course_session = course_session_serializer.save()
            
            course_session_id = course_session.id
            message = None
            errors = ""
            
            if 'instructor' in request.data:
                session_data = self.createUpdateSessionInstructor(request, organization_id, course_session_id)
                session_serializer = SessionInstructorsSerializers(course_session)
                session_data['data'] = session_serializer.data
                return Response(session_data)
            else:
                message = "Course session data processed Successfully. However, Instructor data is not passed"

            if message==None:
                message = 'Success'
            session_instructor = SessionInstructorsSerializers(course_session)
            return Response({'status': 200, 'system_status': 201, 'data': session_instructor.data, 'message': message, 'system_status_message': errors})

        except Exception as e:
            return exception(e)
        

    def patch(self, request, *args, **kwargs):
        try:  
            #check whether organization exists or not         
            user_organization = request.data.get('organization_profile')
            organization_id = user_organization.id
            
            # this would store the result
            result_data = {'session_instructor': None, 'lecture_data': None}

            # checks whether course session exists or not
            course_session_id = self.kwargs['course_session_id'] 
            is_session_exists = CourseSessions.objects.filter(id = course_session_id, course__organization=organization_id)
            if not is_session_exists.exists():
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'Course session does not exists', 'system_error_message': ''})
            
            session_obj = is_session_exists.first()

            # if course is inactive then course session cannot get update
            course_id = session_obj.course.id
            if not Courses.objects.filter(id=course_id, organization=organization_id, is_active=True).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Activate the course first', 'system_status_message': ''})


            # Lecture data gets updated if total lectures are passed in the request:    
            if 'total_lectures' in request.data:
                total_lectures = request.data['total_lectures']
                updated_lectures = self.update_lectures(total_lectures, session_obj, user_organization)
                if updated_lectures['status'] == 400:
                    return errorMessage(updated_lectures['message'])
                
                result_data['lecture_data'] = updated_lectures   

            # updating the course session
            course_session_serializer = CourseSessionsViewsetSerializers(session_obj, data=request.data, partial=True)
            if course_session_serializer.is_valid():
                course_session_serializer.save()
            else:
                return serializerError(course_session_serializer.errors)
            # After updating the course session. Now course session instructor would get updated
            
           
            # these variable would store appropriate messages
            message = None
            errors = None
            course_session_id = session_obj.id
            # If instructor is passed 
            if 'instructor' in request.data:
                session_data = self.createUpdateSessionInstructor(request, organization_id, course_session_id)
                session_serializer = SessionInstructorsSerializers(session_obj)
                session_data['data'] = session_serializer.data
                return Response(session_data)

            else:
                # if only is_active is passed in request.data
                if 'is_active' in request.data:
                    course_session_instructor = CourseSessionInstructors.objects.filter(course_session=course_session_id, course_session__course__organization=organization_id)
                    if course_session_instructor.exists():
                        if request.data['is_active'] == "False":
                            for obj in course_session_instructor.filter(is_active=True):
                                obj.is_active=False
                                obj.save()
                            message = "Course session and Course sessions instructors updated successfully"
                        
                        else:
                            # if only one course session instructor exists(). It will get activated
                            if not course_session_instructor.filter(is_active=True).exists():
                                if course_session_instructor.count() == 1:
                                    csi_last = course_session_instructor.last()
                                    csi_last.is_active=True
                                    csi_last.save()
                                    message = "Course session and Course sessions instructors updated successfully"

                    else:
                        message = "Course session updated successfully. No course session instructor  exists"

                    

            if message == None:
                message='Successfully updated'
            
            session_serializer = SessionInstructorsSerializers(session_obj)
            result_data['session_instructor'] = session_serializer.data

            return Response({'status': 200, 'system_status': 200, 'data': result_data, 'message': message, 'system_status_message': errors})

        except Exception as e:
            return exception(e)
 

    def delete(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            organization_id = user_organization.id

            course_session_id = self.kwargs['course_session_id'] 
            
            is_session_exists = CourseSessions.objects.filter(id = course_session_id, course__organization=organization_id)
            if not is_session_exists.exists():
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'Course session does not exists', 'system_error_message': ''})

            session_obj = is_session_exists.first()

            if CourseSessionTrainees.objects.filter(course_session = course_session_id, course_session__course__organization=organization_id, is_active=True).exists():
                return Response({'status': 400, 'system_status': 403, 'data': '', 'message': 'Deactivate the course session trainee first', 'system_status_message': ''})
        
            # Whether active course session instructor exists or not
            data = CourseSessionInstructors.objects.filter(course_session=course_session_id, course_session__course__organization=organization_id)
            message = ''
            if data.exists():
                session_obj.is_active = False
                session_obj.save()
                for obj in data:
                    obj.is_active = False
                    obj.save()
                message = "Course session and all the corresponding course session instructor is deactivated successfully"
                
            else:
                if session_obj.is_active==False:
                    message = 'Course session is already deactivated. No session instructor exists right now!'
                elif session_obj.is_active==True:
                    session_obj.is_active=False
                    session_obj.save()
                    message = 'Course session is deactivated successfully. No session instructor exists right now!'

            return Response({'status': 200, 'system_status': 200, 'data': '', 'message': message, 'system_status_message': ''})            
        except Exception as e:
            return exception(e)


    def courseSessionInstructorFieldsArray(self, course_session_instructor_data):
        try:
            course_session_instructor_data_dict = {
                'course_session': '',
                'instructor': '',
            }

            for key in course_session_instructor_data_dict:
                if course_session_instructor_data.get(key):
                    if course_session_instructor_data.get(key) != '':
                        course_session_instructor_data_dict[key] = course_session_instructor_data.get(key, None)

            return course_session_instructor_data_dict
        except Exception as e:
            return str(e)
 


    def courseSessionChecks(self, request, course_session_id):
        try:
            #check whether organization exists or not         
            user_organization = request.data.get('organization_profile')
            organization_id = user_organization.id
            
            is_session_exists = CourseSessions.objects.filter(id = course_session_id, course__organization=organization_id)
            if not is_session_exists.exists():
                return {'status':400, 'system_status':400, 'data': '', 'message': 'Course session does not exists', 'system_error_message': ''}
            
            return {'status': 200}
        except Exception as e:
            return str(e)

    # updates lectures if lectures are passed in request.data
    def update_lectures(self, total_lectures, session_obj, user_organization):
        try:
            course_session_id = session_obj.id
            lecture_query = Lectures.objects.filter(course_session_instructor__course_session=course_session_id, course_session_instructor__course_session__course__organization=user_organization.id)
        
            response = {'status': 200, 'data': '', 'message': ''}
            if lecture_query.exists():
                lectures_list = []
                previous_total_lectures = None
                if lecture_query.exists():
                    lecture_data = lecture_query.first()
                    csi_id = lecture_data.course_session_instructor
                    previous_total_lectures = int(lecture_data.course_session_instructor.course_session.total_lectures)
                else:
                    csi = CourseSessionInstructors.objects.filter(course_session=course_session_id, is_active=True)
                    if not csi.exists():
                        response['status'] = 400
                        response['message'] = 'Please assign instructor to this session first'
                        return response
                    csi_id = csi.id

                current_total_lectures = int(total_lectures)

                if previous_total_lectures is None:
                    previous_total_lectures = 0
                    
                    
                if current_total_lectures > previous_total_lectures:
                    # session status would change to In progress if it was completed
                    if session_obj.session_status == 'Completed':
                        session_obj.session_status = 'InProgress'
                        session_obj.save()


                    for i in range(previous_total_lectures + 1, current_total_lectures + 1):
                        if lecture_query.filter(lecture_no=i).exists():
                            lecture_obj = lecture_query.filter(lecture_no=i).first()
                            lecture_obj.is_active=True
                            lecture_obj.save()
                            lectures_list.append(LecturesViewsetSerializers(lecture_obj, many=False).data)
                            continue
                        

                        lectures = Lectures.objects.create(
                            course_session_instructor = csi_id,
                            lecture_no = i,
                            title = 'title {}'.format(i),
                            description = 'description {}'.format(i),
                            status = 2, # Not Scheduled
                            start_time = None,
                            date = None
                        )
                        lectures.save()
                        lecture_serializer = LecturesViewsetSerializers(lectures, many=False)
                        lectures_list.append(lecture_serializer.data)

                elif current_total_lectures < previous_total_lectures:
                    # if instructor has taken more lecture
                    if lecture_query.filter(lecture_no = current_total_lectures+1, status=4):
                        response['message'] = 'Total lecture cannot be equal to the value provided, as the instructor has completed more lectures than the value provided'
                        response['status'] = 400
                        return response
                    elif lecture_query.filter(lecture_no = current_total_lectures, status=4):
                        session_obj.session_status = 'Completed'
                        session_obj.save()

                    for i in range(current_total_lectures + 1, previous_total_lectures + 1):
                        lecture_obj = lecture_query.filter(lecture_no=i)
                        lecture_obj = lecture_obj.first()
                        lecture_obj.is_active=False
                        lecture_obj.save()
                        lectures_list.append(LecturesViewsetSerializers(lecture_obj, many=False).data)

                response['data'] = lectures_list
                return response
            
            return response
        except Exception as e:
            response['status'] = 400
            response['message'] = str(e)
            return response



    """
        This functions checks if an active instructor exists or not. If instructor is passed and the instructor already exists
        it will update the instructor by activating it. If instuctor does not exists. It will create a new instructor and deactivate
        all the other instructors 
    """
    def createUpdateSessionInstructor(self, request, organization_id, course_session_id):
        try:
            message = None
            errors = ""
            # If instructor is passed while updating. This checks whether at that particular id, instructor exists or not
            if 'instructor' in request.data:
                instructor_id = request.data['instructor']
                instructor_obj = Instructors.objects.filter(id=instructor_id, organization=organization_id)
                if not instructor_obj.exists():
                    message = "Course session data processed Successfully. However, No instructor exists at this id"
                elif instructor_obj.filter(is_active=False):
                    message = "Course session data processed Successfully. However, Instructor is deactivated"
                
                if message is not None:
                    return {'status': 200, 'response': 400, 'system_status': 201, 'data': '', 'message': message, 'system_status_message': errors}
            

            course_session_instructor = CourseSessionInstructors.objects.filter(course_session=course_session_id, course_session__course__organization=organization_id)
            session_instructor = course_session_instructor.filter(instructor=instructor_id)
            
            # deactivate all the course session instructor
            if course_session_instructor.filter(is_active=True).exists():
                for obj in course_session_instructor.filter(is_active=True):
                    obj.is_active = False
                    obj.save()
                    
            # update session instructor
            if session_instructor.exists():
                message = "Course session data is processed successfully and course session instructor status is changed to active"
                obj = session_instructor.first()
                obj.is_active=True
                obj.save()
                return {'status': 200, 'response': 400, 'system_status': 201, 'data': '', 'message': message, 'system_status_message': errors}
            # instructor is created 
            else: 
                if message is None:
                    course_session_instructor_data = request.data
                    course_session_instructor_data_array = self.courseSessionInstructorFieldsArray(course_session_instructor_data)
                    course_session_instructor_data_array['course_session'] = course_session_id
                    serializer_course_session_instructor = CourseSessionInstructorsViewsetSerializers(data = course_session_instructor_data_array)
                    if serializer_course_session_instructor.is_valid():
                        serializer_course_session_instructor.save()
                        CourseSessionInstructorsViewsetSerializers(data = serializer_course_session_instructor.data)
                        message = "Successfully Created"
                    else:
                        errors = serializer_course_session_instructor.errors
                        message = "Course session data processed Successfully. However, something went wrong while creating course session instructor"
                    return {'status': 200, 'response': 400, 'system_status': 201, 'data': '', 'message': message, 'system_status_message': errors}

            return {'status': 200, 'system_status': 200, 'response': 200, 'data': '', 'message': message, 'system_status_message': errors}

        except Exception as e:
            return str(e)

        
class PreSessionInstructorsDataView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def get(self, request, *args, **kwargs):
        try:
            result_data = {'instructors': None, 'courses': None, 'session_types': None}
            
            user_organization = request.data.get('organization_profile')

            instructor_obj = Instructors.objects.filter(organization=user_organization.id, is_active=True)
            if instructor_obj.exists():
                instructor_serializer = InstructorsViewsetSerializers(instructor_obj, many=True)
                result_data['instructors'] = instructor_serializer.data

            course_obj = Courses.objects.filter(organization=user_organization.id, is_active=True)
            if course_obj.exists():
                course_serializer = CoursesViewsetSerializers(course_obj, many=True)
                result_data['courses'] = course_serializer.data

            session_types_obj = CourseSessionTypes.objects.all()
            session_types_serializer = CourseSessionTypesViewsetSerializers(session_types_obj, many=True)
            result_data['session_types'] = session_types_serializer.data

            return Response({'status': 200, 'system_status': 200, 'data': result_data, 'message': 'Success', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)



    