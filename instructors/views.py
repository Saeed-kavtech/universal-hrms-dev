from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import viewsets
from .serializers import *
from helpers.status_messages import *
from .models import *
from helpers.custom_permissions import IsAuthenticated, DoesOrgExists


# Create your views here.

# mode of instructions router
class ModeOfInstructionsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ModeOfInstructions.objects.filter(is_active=True)
    serializer_class = ModeOfInstructionsViewsetSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if not ModeOfInstructions.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'This mode of instruction does not exists', 'system_status_message': ''})

            obj = ModeOfInstructions.objects.get(id=pk)
            if obj.is_active == False:
                msg = "This Attachment Type is already deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
            obj.is_active = False
            obj.save()
            serializer = ModeOfInstructionsViewsetSerializers(obj)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Deactivated Successfully', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)


# course session type router
class CourseSessionTypesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = CourseSessionTypes.objects.filter(is_active=True)
    serializer_class = CourseSessionTypesViewsetSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if not CourseSessionTypes.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'This mode of instruction does not exists', 'system_status_message': ''})

            obj = CourseSessionTypes.objects.get(id=pk)
            if obj.is_active == False:
                msg = "This Attachment Type is already deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
            obj.is_active = False
            obj.save()
            serializer = CourseSessionTypesViewsetSerializers(obj)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Deactivated Successfully', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)



class InstructorViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def list(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            obj = Instructors.objects.filter(organization=user_organization.id, is_active=True).order_by('name')
            serializer = InstructorsViewsetSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def retrieve(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            uuid = self.kwargs['uuid']
            slug = self.kwargs['slug']

            query = Instructors.objects.filter(uuid=uuid, slug_name=slug, organization=user_organization.id)
            if not query.exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'No instructor exists at this id or at this slug', 'system_error_message': ''})
            
            if query.filter(is_active=False).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Instructor is deactivated', 'system_error_message': ''})
            
            obj = query.first()
            serializer = InstructorsViewsetSerializers(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)   


    def create(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            request.data['organization'] = user_organization.id

            serializer = InstructorsViewsetSerializers(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)

        except Exception as e:
            return exception(e)


    def patch(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            uuid = self.kwargs['uuid']
            slug = self.kwargs['slug']

            query = Instructors.objects.filter(uuid=uuid, slug_name=slug, organization=user_organization.id)
            if not query.exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'No instructor exists at this id or at this slug', 'system_error_message': ''})
            
            obj = query.first()
            serializer = InstructorsViewsetSerializers(obj, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()
            
            return successfullyUpdated(serializer.data)

        except Exception as e:
            return exception(e)


    def delete(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            uuid = self.kwargs['uuid']
            slug = self.kwargs['slug']

            query = Instructors.objects.filter(uuid=uuid, slug_name=slug, organization=user_organization.id)
            if not query.exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'No instructor exists at this id or at this slug', 'system_error_message': ''})
            if query.filter(is_active=False):
                return Response({'status': 200, 'system_status': 200, 'data': '', 'message': 'Instructor is already deactivated', 'system_error_message': ''})

            obj = query.first()
            obj.is_active = False
            obj.save()
            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT,  'data': '', 'message': 'Successfully Deleted', 'system_status_message': ''})

        except Exception as e:
            return exception(e)



class PreCompleteInstructorDataView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def get(self, request, *args, **kwargs):
        try:
            result_data = {'instructors': None, 'course_sessions': None, 'course_session_instructors': None, 'lectures': None}
            
            user_organization = request.data.get('organization_profile')

            instructor_obj = Instructors.objects.filter(organization=user_organization.id, is_active=True)
            if instructor_obj.exists():
                instructor_serializer = InstructorsViewsetSerializers(instructor_obj, many=True)
                result_data['instructors'] = instructor_serializer.data

            course_sessions_obj = CourseSessions.objects.filter(course__organization=user_organization.id, course__is_active=True, is_active=True)
            if course_sessions_obj.exists():
                course_sessions_serializer = CourseSessionsViewsetSerializers(course_sessions_obj, many=True)
                result_data['course_sessions'] = course_sessions_serializer.data

            course_session_instructors_obj = CourseSessionInstructors.objects.filter(course_session__course__organization=user_organization.id, course_session__is_active=True, is_active=True)
            if course_session_instructors_obj.exists():
                course_session_instructors_serializer = SessionInstructorsSerializers(course_session_instructors_obj, many=True)
                result_data['course_session_instructors'] = course_session_instructors_serializer.data

            lectures_obj = Lectures.objects.filter(course_session_instructor__course_session__course__organization=user_organization.id, course_session_instructor__is_active=True, is_active=True)
            if lectures_obj.exists():
                lectures_serializer = LecturesViewsetSerializers(lectures_obj, many=True)
                result_data['lectures'] = lectures_serializer.data

            return Response({'status': 200, 'system_status': 200, 'data': result_data, 'message': 'Success', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)
