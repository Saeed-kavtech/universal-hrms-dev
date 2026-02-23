from rest_framework import serializers
from .models import *

class CourseApplicantsViewsetSerializers(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    course_session_title = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    status_title = serializers.SerializerMethodField()
    decision_list = serializers.SerializerMethodField()

    class Meta:
        model = CourseApplicants
        fields = [
            'id',
            'course',
            'course_title',
            'course_session',
            'course_session_title',
            'employee',
            'employee_name',
            'decision_list',
            'is_submitted',
            'is_trainee',
            'status',
            'status_title',
            'date',
            'additional_comments',
            'is_active',
        ]

    def get_decision_list(self, obj):
        try:    
            decision_obj =  obj.decision_list.filter(is_active=True)
            serializer_decision = CourseApplicantsLogsViewsetSerializers(decision_obj, many=True)
            return serializer_decision.data
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


    def get_course_session_title(self, obj):
        try:
            if obj.course_session is not None:
                return obj.course_session.session_type
            return None
        except Exception as e:
            print(str(e))
            return None


    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None


    def get_status_title(self, obj):
        try:
            return STATUS_CHOICES[obj.status-1][1]
        except Exception as e:
            print(str(e))
            return None


    # def get_decision_status_title(self, obj):
    #     try:
    #         return DECISION_STATUS_CHOICES[obj.decision_status-1][1]
    #     except Exception as e:
    #         print(str(e))
    #         return None


class UpdateCourseApplicantsViewsetSerializers(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    course_session_title = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    status_title = serializers.SerializerMethodField()
    decision_list = serializers.SerializerMethodField()

    class Meta:
        model = CourseApplicants
        fields = [
            'id',
            'course',
            'course_title',
            'course_session',
            'course_session_title',
            'employee',
            'employee_name',
            'decision_list',
            'is_submitted',
            'is_trainee',
            'status',
            'status_title',
            'date',
            'additional_comments',
            'is_active',
        ]

        read_only_fields = [
                'employee', 
                'course', 
                'course_session'
            ]


    def get_decision_list(self, obj):
        try:    
            decision_obj =  obj.decision_list.filter(is_active=True)
            serializer_decision = CourseApplicantsLogsViewsetSerializers(decision_obj, many=True)
            return serializer_decision.data
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


    def get_course_session_title(self, obj):
        try:
            if obj.course_session is not None:
                return obj.course_session.session_type
            return None
        except Exception as e:
            print(str(e))
            return None


    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None


    def get_status_title(self, obj):
        try:
            return STATUS_CHOICES[obj.status-1][1]
        except Exception as e:
            print(str(e))
            return None



class CourseApplicantsLogsViewsetSerializers(serializers.ModelSerializer):
    decision_status_title = serializers.SerializerMethodField()
    class Meta:
        model = CourseApplicantsLogs
        fields = [
            'id',
            'course_applicant',
            'log_status', 
            'decision_status',
            'decision_status_title',
            'decision_by',
            'decision_reason'
        ]

    def get_decision_status_title(self, obj):
        try:
            return DECISION_STATUS_CHOICES[obj.decision_status-1][1]
        except Exception as e:
            print(str(e))
            return None

class CourseSessionTraineesViewsetSerializers(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    course_applicant_name = serializers.SerializerMethodField()
    trainee_status = serializers.SerializerMethodField()

    class Meta:
        model = CourseSessionTrainees
        fields = [
            'id',
            'course_applicant',
            'course_applicant_name',
            'course',
            'course_title',
            'course_session',
            'trainee_status',
            'is_active',
        ]

    def get_trainee_status(self, obj):
        try:
            trainee_status = obj.course_session.session_status
            if trainee_status == 'Not initiated':
                return 'TODO'
            return trainee_status
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

    def get_course_applicant_name(self, obj):
        try:
            if obj.course_applicant is not None:
                if obj.course_applicant.employee is not None:
                    return obj.course_applicant.employee.name
            return None
        except Exception as e:
            print(str(e))
            return None


class UpdateCourseSessionTraineesViewsetSerializers(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    course_applicant_name = serializers.SerializerMethodField()
    trainee_status = serializers.SerializerMethodField()
    class Meta:
        model = CourseSessionTrainees
        fields = [
            'id',
            'course_applicant',
            'course_applicant_name',
            'course',
            'course_title',
            'course_session',
            'trainee_status',
            'is_active',
        ]

        read_only_fields = [
            'course_applicant', 
            'course', 
            'course_session'
        ]

    def get_trainee_status(self, obj):
        try:
            return obj.course_session.session_status
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

    def get_course_applicant_name(self, obj):
        try:
            if obj.course_applicant is not None:
                if obj.course_applicant.employee is not None:
                    return obj.course_applicant.employee.name
            return None
        except Exception as e:
            print(str(e))
            return None


class CourseSessionTraineeAttendanceViewsetSerializers(serializers.ModelSerializer):
    lecture_number = serializers.SerializerMethodField()
    course_session_trainee_name = serializers.SerializerMethodField()
    attendance_status_title = serializers.SerializerMethodField()

    class Meta: 
        model = CourseSessionTraineeAttendance
        fields = [
            'id',
            'lecture',
            'lecture_number',
            'course_session_trainee',
            'course_session_trainee_name',
            'attendance_status',
            'attendance_status_title',
            'time',
            'date',
            'mode',
            'is_active'
        ]

    def get_lecture_number(self, obj):
        try:
            return obj.lecture.lecture_no
        except Exception as e:
            print(str(e))
            return None

    
    def get_course_session_trainee_name(self, obj):
        try:
            return obj.course_session_trainee.course_applicant.employee.name
        except Exception as e:
            print(str(e))
            return None


    def get_attendance_status_title(self, obj):
        try:
            if obj.attendance_status is not None:
                return ATTENDANCE_STATUS_CHOICES[obj.attendance_status-1][1]
            return None
        except Exception as e:
            print(str(e))
            return None


class CSTAttendanceViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = CourseSessionTraineeAttendance
        fields = [
            'id',
            'lecture',
            'course_session_trainee',
            'attendance_status',

        ]



