from rest_framework import serializers
from applicants.models import CourseSessionTrainees
from instructors.models import CourseSessions, CourseSessionInstructors

# This serializer is required for L&D Worksheet
class CourseSessionTraineesWorksheetSerializers(serializers.ModelSerializer):
    trainee_name = serializers.SerializerMethodField()
    employee_id = serializers.SerializerMethodField()
    class Meta:
        model = CourseSessionTrainees
        fields = [
            'trainee_name',
            'employee_id'
            
        ]


    def get_employee_id(self, obj):
        try:
            return obj.course_applicant.employee.emp_code
        except Exception as e:
            print(str(e))
            return None


    def get_trainee_name(self, obj):
        try:
            return obj.course_applicant.employee.name
        except Exception as e:
            print(str(e))
            return None
        

# This serializer is required for L&D Worksheet
class GetInstructorNameSerializers(serializers.ModelSerializer):
    instructor_name = serializers.SerializerMethodField()

    class Meta:
        model = CourseSessionInstructors
        fields = [
            'instructor_name'
        ]

    def get_instructor_name(self, obj):
        try:
            return obj.instructor.name
        except Exception as e:
            print(str(e))
            return None
        

# This serializer is required for L&D Worksheet
class LearningAndDevelopmentDashboardSerializers(serializers.ModelSerializer):
    training_name = serializers.SerializerMethodField()
    instructors = serializers.SerializerMethodField()
    trainee_name = serializers.SerializerMethodField()
    training_category = serializers.SerializerMethodField()
    course_session_type_title = serializers.SerializerMethodField()
    class Meta:
        model = CourseSessions
        fields = [
            'id',
            'training_name',
            'training_category',
            'course_session_type',
            'course_session_type_title',
            'duration',
            'start_date',
            'end_date',
            'session_status',
            'instructors',
            'trainee_name',
        ]


    def get_training_name(self, obj):
        try:
            return obj.course.title + ' (' + str(obj.start_date) + ' - ' + str(obj.end_date) + ')'
        except Exception as e:
            print(str(e))
            return None
        

    def get_trainee_name(self, obj):
        try:
            cs_obj = CourseSessionTrainees.objects.filter(course_session=obj.id, is_active=True)
            serializer = CourseSessionTraineesWorksheetSerializers(cs_obj, many=True)
            return serializer.data
        except Exception as e:
            print(str(e))
            return None
        

    def get_training_category(self, obj):
        try:
            return obj.course.program.subject.type.title
        except Exception as e:
            print(str(e))
            return None
    

    def get_course_session_type_title(self, obj):
        try:
            return obj.course_session_type.title
        except Exception as e:
            print(str(e))
            return None


    def get_instructors(self, obj):
        try:
            cs_obj = CourseSessionInstructors.objects.filter(course_session=obj.id, is_active=True)
            serializer = GetInstructorNameSerializers(cs_obj, many=True)
            return serializer.data
        except Exception as e:
            print(str(e))
            return None
        