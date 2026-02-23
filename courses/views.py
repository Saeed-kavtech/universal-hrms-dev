from django.shortcuts import render
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from helpers.custom_permissions import IsAuthenticated, DoesOrgExists
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from .serializers import *
from .models import *
from helpers.status_messages import *
from logs.views import UserLoginLogsViewset
from instructors.models import CourseSessions
from instructors.serializers import CourseSessionsViewsetSerializers
import json
from django.db import transaction
from training.models import Training
from helpers.decode_token import decodeToken

# Create your views here.
class CoursesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def list(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
            obj = Courses.objects.filter(organization = user_organization.id, program__is_active=True, program__subject__is_active=True, is_active = True).order_by('title')
            serializer = CoursesViewsetSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
           return exception(e)


    def retrieve(self, request, *args, **kwargs):
        try:
            slug = self.kwargs['slug']
            uuid = self.kwargs['uuid']

            course_data = self.preCourseDataChecks(request, slug, uuid)
            if course_data['status'] == 400:
                return Response(course_data)

            obj = course_data['data']

            serializer = CoursesViewsetSerializers(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def get_course_data(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
            obj = Courses.objects.filter(organization = user_organization.id,is_active = True).order_by('-id')
            serializer = ListCoursesViewsetSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
           return exception(e)



    def create(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
            request.data['organization'] = user_organization.id

            if 'program' in request.data:
                program_id = request.data['program']
            else:
                return Response({'status':400, 'system_status': 400, 'data': '', 'message': 'Program is a required field', 'system_error_message': ''})

            is_exists = Programs.objects.filter(id = program_id)
            if not is_exists.exists():
                return Response({'status':400, 'system_status': 400, 'data': '', 'message': 'No program exists at this id', 'system_error_message': ''})
            if is_exists.filter(subject__is_active=False):
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Activate the subject first', 'system_error_message': ''})
            if is_exists.filter(is_active=False):
                return Response({'status':400, 'system_status': 400, 'data': '', 'message': 'Activate the program first', 'system_error_message': ''})
            
            serializer = CoursesViewsetSerializers(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)
        
        except Exception as e:
            return exception(e)


    def patch(self, request, *args, **kwargs):
        try:
            slug = self.kwargs['slug']
            uuid = self.kwargs['uuid']

            course_data = self.preCourseDataChecks(request, slug, uuid)
            if course_data['status'] == 400:
                return Response(course_data)

            obj = course_data['data']

            if 'program' in request.data:
                program_id = request.data['program']
                if not Programs.objects.filter(id=program_id, is_active=True).exists():
                    return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Deactivate program cannot be assigned to courses. Kindly first activate the program', 'system_status_message': ''})


            serializer = CoursesViewsetSerializers(obj, data=request.data, partial=True)
                        
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()
            
            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)


    def delete(self, request, *args, **kwargs):
        try:
            slug = self.kwargs['slug']
            uuid = self.kwargs['uuid']

            course_data = self.preCourseDataChecks(request, slug, uuid)
            if course_data['status'] == 400:
                return Response(course_data)

            obj = course_data['data']
            
            if obj.is_active == False:
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Courses is already deactivated', 'system_status_message': ''})    

            course_id = obj.id
            if CourseSessions.objects.filter(course=course_id, is_active=True):
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'To deactivate the course, you need to deactivate the course session first', 'system_status_message': ''})


            obj.is_active = False
            obj.save()
            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT,  'data': '', 'message': 'Successfully Deleted', 'system_status_message': ''})

        except Exception as e:
            return exception(e)


    def get_session_courses(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            course_id = self.kwargs['course_id']

            # active course exists or not
            course_query = Courses.objects.filter(id=course_id, organization=user_organization.id)
            if not course_query.exists():
                return errorMessage("No course exists at this id")
            if not course_query.filter(is_active=True).exists():
                return errorMessage("No active course exists at this id")
            
            query = CourseSessions.objects.filter(course=course_id, course__organization=user_organization.id, course__is_active=True, is_active=True)
            serializer = CourseSessionsViewsetSerializers(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def preCourseDataChecks(self, request, slug, uuid):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return {'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''}
      
            query = Courses.objects.filter(uuid=uuid, slug_title=slug)
            
            if not query.exists():
                return {'status':400, 'system_status':400, 'data': '', 'message': 'uuid or slug title is incorrect or does not exists', 'system_error_message': ''}

            if request.method == 'GET':
                if query.filter(is_active=False):
                    return {'status':400, 'system_status':400, 'data': '', 'message': 'This course is inactive', 'system_error_message': ''}
            
            # if no organization exists against this course
            query = query.first()
            
            # if subject is inactive then he cannot access the course
            if query.program.subject.is_active == False:
                return {'status': 400, 'system_status': 400, 'message': 'The Subject is deactivated', 'data': '', 'system_error_message': ''}

            # if program is inactive. Then he cannot access the course
            if query.program.is_active == False:
                return {'status': 400, 'system_status': 400, 'data': '', 'message': 'The Program is deactivated', 'system_error_message': ''}
            
            # organization cannot be null
            if query.organization is None:
                return {'status': 400, 'system_status': 400, 'data': '', 'message': 'No organization is assigned to this course', 'system_error_message': ''}

            # if course organization id and logged in user id does not match
            if query.organization.id != user_organization.id:
                return {'status': 400, 'system_status':status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'User do not have previlage to access data of another organization', 'system_error_message': ''}

            return {'status': 200, 'data': query}
        except Exception as e:
            return {'status': 400, 'data': '', 'message': str(e)}
    
    
    @transaction.atomic
    def course_creation(self, request, *args, **kwargs):
        try:
          
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            request_data=request.data
           
            if isinstance(request_data, str):
                request_data = json.loads(request_data)
                req_course.append(request_data)
            else:
                req_course = request_data

            
            required_fields = ['title']
            if not all(field in request.data for field in required_fields):
                return errorMessage(
                    'make sure you have added all the required fields: '
                    '[title]'
                )

            req_course['organization'] = user_organization.id


            course_data = {key: value for key, value in req_course.items() if not isinstance(value, list)}
            
            serializer = STCoursesViewsetSerializers(data = course_data)
            if not serializer.is_valid():
                # return serializerError(serializer.errors)
                raise ValidationError(serializer.errors)
            course_id=serializer.save()

            # print(course_id.id)

            for module in req_course["course_module_data"]:

                module_data={
                        'title':module['title'],
                        'course':course_id.id,
                        'description':module['description'],
                        'what_we_learn':module['what_we_learn'],
                        'total_hours':module['total_hours'],
                        } 
                
                # print(module_data)
                
                serializer1 =STCourseModulesViewsetSerializers(data = module_data)
                if not serializer1.is_valid():
                    # return serializerError(serializer1.errors)
                    course_id.delete()
                    raise ValidationError(serializer1.errors)
                
            
                    # error.append(serializer1.errors)
                    # continue
                
                module_id=serializer1.save()
                # print(module_id.id)

                topics_data = module["module_topic_data"]
                

                for topic in topics_data:
                    topic_data={
                        'title':topic['title'],
                        'course_module':module_id.id,
                        'credit_hours':topic['credit_hours'],
                        'description':topic['description'],
                        } 
                    
                    # print(topic_data)
                   
                    serializer2 =STModuleTopicsViewsetSerializers(data = topic_data)
                    # print(serializer2)
                    if not serializer2.is_valid():
                        # print(serializer.errors)
                        course_id.delete()
                        module_id.delete()
                        raise ValidationError(serializer2.errors)
                        # return serializerError(serializer2.errors)
                        # transaction.rollback()
                        # error.append(serializer2.errors)
                        # continue
                    
                    serializer2.save()
                    # print(topic_id)
                


            # if error:
            #         return errorMessageWithData("some data is not save",error)




            return successMessage("Success")
        
        except Exception as e:
            return exception(e)
        

    def course_creation_update(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
            
            # request.data['organization'] = user_organization.id

            error=[]
            request_data=request.data
           
            if isinstance(request_data, str):
                request_data = json.loads(request_data)
                req_course.append(request_data)
            else:
                req_course = request_data

            # if pk != str(request.data.get('id',None)):
            #      return errorMessage(
            #         'Id is not matched'
            #     )

            query_course=Courses.objects.filter(id=pk,organization=user_organization.id,is_active=True)

            if not query_course.exists():
                return errorMessage("Course not exists at this id")
            

            course_instance=query_course.get()
            
            course_data = {key: value for key, value in req_course.items() if not isinstance(value, list)}

            serializer =STCoursesViewsetSerializers(course_instance,data = course_data,partial=True)
            if not serializer.is_valid():
                # return serializerError(serializer.errors)
                error.append(serializer.errors)
                # raise ValidationError(serializer.errors)
            serializer.save()

            # print(course_id.id)

            for module in req_course["course_module_data"]:


                module_id = module.get('id',None)
                
                module_instance = CourseModules.objects.get(id=module_id)
              
                
                serializer1 =STCourseModulesViewsetSerializers(module_instance,data=module,partial=True)
                if not serializer1.is_valid():
                  
                    # raise ValidationError(serializer1.errors)
                    error.append(serializer1.errors)
                    continue
                
                
                serializer1.save()
                # print(module_id.id)

                topics_data = module["module_topic_data"]
                

                for topic in topics_data:


                    topic_id = topic.get('id',None)
                   
                    topic_instance = ModuleTopics.objects.get(id=topic_id)
                    
                   
                    serializer2 =STModuleTopicsViewsetSerializers(topic_instance,data = topic,partial=True)
                    # print(serializer2)
                    if not serializer2.is_valid():
                        error.append(serializer2.errors)
                        continue

                    serializer2.save()
                    # print(topic_id)
                


            if error:
                    return errorMessageWithData("some data is not update",error)




            return successMessage("Success")
        
        except Exception as e:
            return exception(e)
        


    def course_creation_delete(self,request,*args, **kwargs):
        try:

            pk = self.kwargs['pk']
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            print(user_organization)
            query_course=Courses.objects.filter(id=pk,organization=user_organization.id,is_active=True)

            if not query_course.exists():
                return errorMessage("Course not exists at this id")

            obj_course=query_course.get()
            # print(type(obj_course))

            training_query=Training.objects.filter(course=obj_course,organization=user_organization,is_active=True)
            # print(training_query)
            if training_query.exists():
                return errorMessage("Can't delete course because its used in active training")
            
            module_query=CourseModules.objects.filter(course=obj_course,course__organization=user_organization,is_active=True)

            # print(module_query)
            obj_course.is_active = False
            obj_course.save()

            for module in module_query:
                module.is_active=False
                module.save()
                topic_query=ModuleTopics.objects.filter(course_module=module,is_active=True)

                if not topic_query.exists():
                    continue

                for topic in topic_query:
                    topic.is_active=False
                    topic.save()

            return successMessage("Success")
        except Exception as e:
            return exception (e)
        




class PreCourseDataView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return {'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''}
            
            obj = Programs.objects.filter(is_active=True, subject__is_active=True, subject__organization=user_organization.id)
            serializer = ProgramsViewsetSerializers(obj, many=True)

            return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': serializer.data, 'message': 'Success', 'system_error_message': ''})

        except Exception as e:
            return exception(e)


class PreCourseCompleteDataView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            result_data = {'course': None, 'course_pre_requsites': None, 'course_skills': None, 'course_modules': None, 'course_topics': None}
            course_uuid = self.kwargs['course_uuid']
            course_slug = self.kwargs['course_slug'] 
           
            course_obj = Courses.objects.filter(uuid=course_uuid, slug_title=course_slug, is_active=True)
            if course_obj.exists():
                course_obj = course_obj.first()
                courses_serializer = CoursesViewsetSerializers(course_obj)
                result_data['course'] = courses_serializer.data
            else:
                return result_data

            course_pre_requsites_obj = CoursePreRequisite.objects.filter(course__uuid=course_uuid, course__slug_title=course_slug, is_active=True)
            if course_pre_requsites_obj.exists():
                course_pre_requsites_serializer = CoursePreRequisiteViewsetSerializers(course_pre_requsites_obj, many=True)
                result_data['course_pre_requsites'] = course_pre_requsites_serializer.data

            course_skills_obj = CourseSkills.objects.filter(course__uuid=course_uuid, course__slug_title=course_slug, is_active=True)
            if course_skills_obj.exists():
                course_skills_serializer = CourseSkillsViewsetSerializers(course_skills_obj, many=True)
                result_data['course_skills'] = course_skills_serializer.data
           
            course_modules_obj = CourseModules.objects.filter(course__uuid=course_uuid, course__slug_title=course_slug, is_active=True)
            if course_modules_obj.exists():
                course_modules_serializer = CourseModulesViewsetSerializers(course_modules_obj, many=True)
                result_data['course_modules'] = course_modules_serializer.data

            course_topics_obj = ModuleTopics.objects.filter(course_module__course__uuid=course_uuid, course_module__course__slug_title=course_slug, is_active=True)
            if course_topics_obj.exists():
                course_modules_serializer = ModuleTopicsViewsetSerializers(course_topics_obj, many=True)
                result_data['course_topics'] = course_modules_serializer.data

            return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': result_data, 'message': 'Success', 'system_error_message': ''})

        except Exception as e:
            return exception(e)
        

# class  ModuleAssignmentsViewset(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated,DoesOrgExists]
#     queryset=ModuleAssignments.objects.all()
#     serializer_class=ModuleAssignmentsViewsetSerializer


#     def list(self, request, *args, **kwargs):
#         try:
#             user_organization = UserLoginLogsViewset().userOrganization(request.user)
#             if user_organization is None:
#                 return Response({'status':400, 'system_status': 400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
#             obj = self.queryset.filter(organization = user_organization.id, is_active = True).order_by('id')
#             serializer = self.serializer_class(obj, many=True)
#             return success(serializer.data)
#         except Exception as e:
#            return exception(e)

#     def create(self, request, *args, **kwargs):
#         try:
            
#             user_organization = UserLoginLogsViewset().userOrganization(request.user)
#             if user_organization is None:
#                 return {'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''}
      
            
            
#             if not request.data:
#                 return errorMessage("Request Data is empty")
            
            
#             required_fields = ['title', 'module_topic']
#             if not all(field in request.data for field in required_fields):
#                 return errorMessage(
#                     'make sure you have added all the required fields: '
#                     '[title, module_topic]'
#                 )
            
#             module_topic=request.data.get('module_topic')
            
#             query=ModuleTopics.objects.filter(id= module_topic,organization=user_organization.id,is_active=True)
            
#             if not query.exists():
#                 return errorMessage("Module Topic not exists at this id")
            
#             request.data['created_by']=request.user.id
#             request.data['organization']=user_organization.id

#             serializers=self.serializer_class(data=request.data)

#             if not serializers.is_valid():
#                 return serializerError(serializers.errors)
            
#             serializers.save()

#             return successfullyCreated(serializers.data)
            
#         except Exception as e:
#             return exception(e)

