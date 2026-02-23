from rest_framework import serializers
from .models import *

class ModeOfInstructionsViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = ModeOfInstructions
        fields = [
            'id',
            'mode',
            'level',
            'is_active'
        ]


class CourseSessionTypesViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = CourseSessionTypes
        fields = [
            'id',
            'title',
            'level',
            'is_active'
        ]


class InstructorsViewsetSerializers(serializers.ModelSerializer):
    organization_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Instructors
        fields = [
            'id',
            'uuid',
            'name',
            'slug_name',
            'organization',
            'organization_title',
            'title',
            'is_active'
        ]

    def get_organization_title(self, obj):
        try:
            if obj.organization is not None:
                return obj.organization.name
            return None
        except Exception as e:
            print(str(e))
            return None



class CourseSessionInstructorsViewsetSerializers(serializers.ModelSerializer):
    course_session_title = serializers.SerializerMethodField()
    instructor_name = serializers.SerializerMethodField()
    course_id = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()

    class Meta:
        model = CourseSessionInstructors
        fields = [
            'id',
            'course_session',
            'course_session_title',
            'course_id',
            'course_title',
            'instructor',
            'instructor_name',
            'is_active',
        ]

    def get_course_session_title(self, obj):
        try:
            if obj.course_session is not None:
                return obj.course_session.session_type
            return None
        except Exception as e:
            print(str(e))
            return None


    def get_instructor_name(self, obj):
        try:
            if obj.instructor is not None:
                return obj.instructor.name
            return None
        except Exception as e:
            print(str(e))
            return None


    def get_course_id(self, obj):
        try:
            return obj.course_session.course.id
        except Exception as e:
            print(str(e))
            return None


    def get_course_title(self, obj):
        try:
            return obj.course_session.course.title
        except Exception as e:
            print(str(e))
            return None



class CourseSessionsViewsetSerializers(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    course_session_type_title = serializers.SerializerMethodField()
    # course_session_instructors = CourseSessionInstructorsViewsetSerializers(many=True)

    class Meta:
        model = CourseSessions
        fields = [
            'id',
            'session_type',
            'course',
            'course_title',
            'course_session_type',
            'course_session_type_title',
            # 'course_session_instructors',
            'session_status',
            'start_date',
            'end_date',
            'duration',
            'total_lectures',
            'no_of_students',
            'is_active',
        ]


    def get_course_title(self, obj):
        try:
            if obj.course is not None:
                return obj.course.title
            return None
        except Exception as e:
            print(str(e))
            return None


    def get_course_session_type_title(self, obj):
        try:
            if obj.course_session_type is not None:
                return obj.course_session_type.title
            return None
        except Exception as e:
            print(str(e))
            return None




class SessionInstructorsSerializers(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    course_session_type_title = serializers.SerializerMethodField()
    cs_instructor = serializers.SerializerMethodField() 

    class Meta:
        model = CourseSessions
        fields = [
            'id',
            'session_type',
            'course',
            'course_title',
            'course_session_type',
            'course_session_type_title',
            'session_status',
            'cs_instructor',
            'start_date',
            'end_date',
            'duration',
            'total_lectures',
            'no_of_students',
            'is_active',
        ]

   
    def get_cs_instructor(self, obj):
        try:
            csi = obj.cs_instructor.filter(is_active=True)
            serializer = CourseSessionInstructorsViewsetSerializers(csi, many=True)
            return serializer.data
        except Exception as e:
            print(str(e))
            return None


    def get_course_title(self, obj):
        try:
            return obj.course.title
        except Exception as e:
            print(str(e))
            return None


    def get_course_session_type_title(self, obj):
        try:
            if not obj.course_session_type == None:
                return obj.course_session_type.title
            return None
        except Exception as e:
            print(str(e))
            return None


# for homepage API
class SessionInstructorsHomepageSerializers(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    course_session_type_title = serializers.SerializerMethodField()
    cs_instructor = serializers.SerializerMethodField() 
    lectures = serializers.SerializerMethodField()
    class Meta:
        model = CourseSessions
        fields = [
            'id',
            'session_type',
            'course',
            'course_title',
            'course_session_type',
            'course_session_type_title',
            'session_status',
            'cs_instructor',
            'start_date',
            'end_date',
            'duration',
            'lectures',
            'total_lectures',
            'no_of_students',
            'is_active',
        ]

    def get_lectures(self, obj):
        try:
            lecture = Lectures.objects.filter(course_session_instructor__course_session=obj.id, is_active=True)
            serializer = LecturesViewsetSerializers(lecture, many=True)
            return serializer.data
        except Exception as e:
            print(str(e))
            return None
   
    def get_cs_instructor(self, obj):
        try:
            csi = obj.cs_instructor.filter(is_active=True)
            serializer = CourseSessionInstructorsViewsetSerializers(csi, many=True)
            return serializer.data
        except Exception as e:
            print(str(e))
            return None


    def get_course_title(self, obj):
        try:
            return obj.course.title
        except Exception as e:
            print(str(e))
            return None


    def get_course_session_type_title(self, obj):
        try:
            if not obj.course_session_type == None:
                return obj.course_session_type.title
            return None
        except Exception as e:
            print(str(e))
            return None



class CreateLecturesViewsetSerializers(serializers.ModelSerializer):  
    lecture_status_title = serializers.SerializerMethodField()
    class Meta:
        model = Lectures
        fields = [
            'id',
            'course_session_instructor',
            'lecture_no',
            'title',
            'description',
            'status',
            'lecture_status_title'
        ]

    def get_lecture_status_title(self, obj):
        try:
            return status_choices[obj.status-1][1]
        except Exception as e:
            print(str(e))
            return None
    



class LecturesViewsetSerializers(serializers.ModelSerializer):
    course_id = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    instructor_id = serializers.SerializerMethodField()
    instructor_name = serializers.SerializerMethodField()
    mode_of_instruction_title = serializers.SerializerMethodField()
    status_title = serializers.SerializerMethodField()

    class Meta:
        model = Lectures
        fields = [
            'id',
            'course_session_instructor',
            'instructor_id',
            'instructor_name',
            'course_id',
            'course_title',
            'lecture_no',
            'start_time',
            'duration',
            'title',
            'description',
            'is_taken',
            'mode_of_instruction',
            'mode_of_instruction_title',
            'status',
            'status_title',
            'date',
            'is_active',
        ]

        read_only_fields = [
            'lecture_no'
        ]

    
    def get_course_id(self, obj):
        try:
            return obj.course_session_instructor.course_session.course.id
        except Exception as e:
            print(str(e))
            return None


    def get_course_title(self, obj):
        try:
            return obj.course_session_instructor.course_session.course.title
        except Exception as e:
            print(str(e))
            return None


    def get_instructor_id(self, obj):
        try:
            return obj.course_session_instructor.instructor.id
        except Exception as e:
            print(str(e))
            return None

    
    def get_instructor_name(self, obj):
        try:
            return obj.course_session_instructor.instructor.name
        except Exception as e:
            print(str(e))
            return None


    def get_mode_of_instruction_title(self, obj):
        try:
            if obj.mode_of_instruction is not None:
                return obj.mode_of_instruction.mode
            return None
        except Exception as e:
            print(str(e))
            return None



    def get_status_title(self, obj):
        try:
            return status_choices[obj.status-1][1]
        except Exception as e:
            print(str(e))
            return None
        



class CourseSessionsApplicantViewsetSerializers(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    course_session_type_title = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()

    class Meta:
        model = CourseSessions
        fields = [
            'id',
            'session_type',
            'course',
            'course_title',
            'course_session_type',
            'course_session_type_title',
            'session_status',
            'start_date',
            'end_date',
            'duration',
            'total_lectures',
            'no_of_students',
            'is_registered',
            'is_active',
        ]

    
    def get_is_registered(self, obj):
        try:
            registered_course_sessions = self.context.get('registered_course_sessions')
            if registered_course_sessions.filter(course_session=obj.id).exists():
                return True
            
            return False
        except Exception as e:
            print(str(e))
            return None


    def get_course_title(self, obj):
        try:
            if obj.course is not None:
                return obj.course.title
            return None
        except Exception as e:
            print(str(e))
            return None


    def get_course_session_type_title(self, obj):
        try:
            if obj.course_session_type is not None:
                return obj.course_session_type.title
            return None
        except Exception as e:
            print(str(e))
            return None
