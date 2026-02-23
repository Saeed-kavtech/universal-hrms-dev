from rest_framework import serializers
from .models import *


class SubjectTypesViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = SubjectTypes
        fields = [
            'id',
            'title',
            'level',
            'is_active'
        ]


class SubjectsViewsetSerializers(serializers.ModelSerializer):
    type_title = serializers.SerializerMethodField()
    organization_title = serializers.SerializerMethodField()
    class Meta:
        model = Subjects
        fields = [
            'id',
            'uuid',
            'organization',
            'organization_title',
            'title',
            'slug_title',
            'organization',
            'type',
            'type_title',
            'description',
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


    def get_type_title(self, obj):
        try:
            if obj.type is not None:
                return obj.type.title
            return None
        except Exception as e:
            print(str(e))
            return None


class ProgramsViewsetSerializers(serializers.ModelSerializer):
    subject_title = serializers.SerializerMethodField()   
    subject_slug_title = serializers.SerializerMethodField()
    class Meta:
        model = Programs
        fields = [
            'id',
            'uuid',
            'title',
            'slug_title',
            'subject',
            'subject_title',
            'subject_slug_title',
            'description',
            'is_active',
        ]

    def get_subject_title(self, obj):
        try:
            if obj.subject is not None:
                return obj.subject.title
            return None
        except Exception as e:
            print(str(e))
            return None
    
    def get_subject_slug_title(self, obj):
        try:
            if obj.program is not None:
                if obj.program.subject is not None:
                    return obj.program.subject.slug_title
            return None
        except Exception as e:
            print(str(e))
            return None

class CoursesViewsetSerializers(serializers.ModelSerializer):
    program_title = serializers.SerializerMethodField()
    program_slug_title = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    subject_title = serializers.SerializerMethodField() 
    subject_slug_title = serializers.SerializerMethodField() 
    organization_title = serializers.SerializerMethodField()
    mode_of_course_title = serializers.SerializerMethodField()
    complexity_level_title = serializers.SerializerMethodField()

    class Meta:
        model = Courses
        fields = [
            'id',
            'uuid',
            'title',
            'slug_title',
            'code',
            'program',
            'program_title',
            'program_slug_title',
            'organization',
            'organization_title',
            'subject',
            'subject_title',
            'subject_slug_title',
            'program_level',
            'what_will_you_learn',
            'skills_you_gain',
            'credit_hours',
            'mode_of_course',
            'mode_of_course_title',
            'complexity_level',
            'complexity_level_title',
            'offered_by',
            'is_active',
        ]

    def get_subject(self, obj):
        try:
            if obj.program is not None:
                if obj.program.subject is not None:
                    return obj.program.subject.id
            return None
        except Exception as e:
            print(str(e))
            return None

    def get_subject_title(self, obj):
        try:
            if obj.program is not None:
                if obj.program.subject is not None:
                    return obj.program.subject.title
            return None
        except Exception as e:
            print(str(e))
            return None

    def get_subject_slug_title(self, obj):
        try:
            if obj.program is not None:
                if obj.program.subject is not None:
                    return obj.program.subject.slug_title
            return None
        except Exception as e:
            print(str(e))
            return None

    def get_program_title(self, obj):
        try:
            if obj.program is not None:
                return obj.program.title
            return None
        except Exception as e:
            print(str(e))
            return None

    def get_program_slug_title(self, obj):
        try:
            if obj.program is not None:
                return obj.program.slug_title
            return None
        except Exception as e:
            print(str(e))
            return None

    def get_organization_title(self, obj):
        try:
            if obj.organization is not None:
                return obj.organization.name
            return None
        except Exception as e:
            print(str(e))
            return None


    def get_mode_of_course_title(self, obj):
        try:
            if obj.mode_of_course in [1,2,3]:
                return mode_of_course_choices[obj.mode_of_course-1][1]
            return None
        except Exception as e:
            print(str(e))
            return None

    def get_complexity_level_title(self, obj):
        try:
            if obj.complexity_level in [1,2,3]:
                return complexity_level_choices[obj.complexity_level-1][1]
            return None
        except Exception as e:
            print(str(e))
            return None
 


class STCoursesViewsetSerializers(serializers.ModelSerializer):
  
    organization_title = serializers.SerializerMethodField()
    mode_of_course_title = serializers.SerializerMethodField()
    complexity_level_title = serializers.SerializerMethodField()

    class Meta:
        model = Courses
        fields = [
            'id',
            'uuid',
            'title',
            'code',
            'organization',
            'organization_title',
            'what_will_you_learn',
            'skills_you_gain',
            'credit_hours',
            'mode_of_course',
            'mode_of_course_title',
            'complexity_level',
            'complexity_level_title',
            'is_active',
        ]



    def get_organization_title(self, obj):
        try:
            if obj.organization is not None:
                return obj.organization.name
            return None
        except Exception as e:
            print(str(e))
            return None


    def get_mode_of_course_title(self, obj):
        try:
            if obj.mode_of_course in [1,2,3]:
                return mode_of_course_choices[obj.mode_of_course-1][1]
            return None
        except Exception as e:
            print(str(e))
            return None

    def get_complexity_level_title(self, obj):
        try:
            if obj.complexity_level in [1,2,3]:
                return complexity_level_choices[obj.complexity_level-1][1]
            return None
        except Exception as e:
            print(str(e))
            return None
 

class CoursePreRequisiteViewsetSerializers(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    course_slug_title = serializers.SerializerMethodField()
    class Meta:
        model = CoursePreRequisite
        fields = [
            'id',
            'course',
            'course_title',
            'course_slug_title',
            'pre_requisite',
            'detail',
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


    def get_course_slug_title(self, obj):
        try:
            if obj.course is not None:
                return obj.course.slug_title
            return None
        except Exception as e:
            print(str(e))
            return None

class CourseSkillsViewsetSerializers(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    course_slug_title = serializers.SerializerMethodField()
    class Meta:
        model = CourseSkills
        fields = [
            'id',
            'course',
            'course_title',
            'course_slug_title',
            'skill',
            'is_active'
        ]

    def get_course_title(self, obj):
        try:
            if obj.course is not None:
                return obj.course.title
            return None
        except Exception as e:
            print(str(e))
            return None


    def get_course_slug_title(self, obj):
        try:
            if obj.course is not None:
                return obj.course.slug_title
            return None
        except Exception as e:
            print(str(e))
            return None

class CourseModulesViewsetSerializers(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    course_slug_title = serializers.SerializerMethodField()
    class Meta:
        model = CourseModules
        fields = [
            'id',
            'course',
            'course_title',
            'course_slug_title',
            'title',
            'description',
            'what_we_learn',
            'total_hours',
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


    def get_course_slug_title(self, obj):
        try:
            if obj.course is not None:
                return obj.course.slug_title
            return None
        except Exception as e:
            print(str(e))
            return None

class STCourseModulesViewsetSerializers(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    class Meta:
        model = CourseModules
        fields = [
            'id',
            'course',
            'course_title',
            'title',
            'description',
            'what_we_learn',
            'total_hours',
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


    def get_course_slug_title(self, obj):
        try:
            if obj.course is not None:
                return obj.course.slug_title
            return None
        except Exception as e:
            print(str(e))
            return None


class ModuleTopicsViewsetSerializers(serializers.ModelSerializer):
    course_module_title = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    course_slug_title = serializers.SerializerMethodField()
    class Meta:
        model = ModuleTopics
        fields = [
            'id',
            'course',
            'course_title',
            'course_slug_title',
            'course_module',
            'course_module_title',
            'title',
            'credit_hours',
            'description',
            'is_active'   
        ]
    
    def get_course(self, obj):
        try:
            return obj.course_module.course.id
        except Exception as e:
            print(str(e))
            return None


    def get_course_title(self, obj):
        try:
            return obj.course_module.course.title
        except Exception as e:
            print(str(e))
            return None


    def get_course_slug_title(self, obj):
        try:
            return obj.course_module.course.slug_title
        except Exception as e:
            print(str(e))
            return None    


    def get_course_module_title(self, obj):
        try:
            return obj.course_module.title
        except Exception as e:
            print(str(e))
            return None

class STModuleTopicsViewsetSerializers(serializers.ModelSerializer):
    course_module_title = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    class Meta:
        model = ModuleTopics
        fields = [
            'id',
            'course',
            'course_title',
            'course_module',
            'course_module_title',
            'title',
            'credit_hours',
            'description',
            'is_active'   
        ]
    
    def get_course(self, obj):
        try:
            return obj.course_module.course.id
        except Exception as e:
            print(str(e))
            return None


    def get_course_title(self, obj):
        try:
            return obj.course_module.course.title
        except Exception as e:
            print(str(e))
            return None


    def get_course_slug_title(self, obj):
        try:
            return obj.course_module.course.slug_title
        except Exception as e:
            print(str(e))
            return None    


    def get_course_module_title(self, obj):
        try:
            return obj.course_module.title
        except Exception as e:
            print(str(e))
            return None


class ListCourseModulesViewsetSerializers(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    # course_slug_title = serializers.SerializerMethodField()
    module_topic_data=serializers.SerializerMethodField()
    class Meta:
        model = CourseModules
        fields = [
            'id',
            'course',
            'course_title',
            # 'course_slug_title',
            'title',
            'description',
            'what_we_learn',
            'total_hours',
            'module_topic_data',
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


    # def get_course_slug_title(self, obj):
    #     try:
    #         if obj.course is not None:
    #             return obj.course.slug_title
    #         return None
    #     except Exception as e:
    #         print(str(e))
    #         return None
        

    def get_module_topic_data(self,obj):
        try:

            query=ModuleTopics.objects.filter(course_module=obj.id,is_active=True)

            if not query.exists():
                return None
            
            data=STModuleTopicsViewsetSerializers(query,many=True).data
            
            return data

        except Exception as e:
            return None


class ListCoursesViewsetSerializers(serializers.ModelSerializer):
    
    organization_title = serializers.SerializerMethodField()
    mode_of_course_title = serializers.SerializerMethodField()
    complexity_level_title = serializers.SerializerMethodField()
    course_module_data=serializers.SerializerMethodField()
    course_group_title=serializers.SerializerMethodField()

    class Meta:
        model = Courses
        fields = [
            'id',
            'uuid',
            'title',
            # 'slug_title',
            'code',
            'course_group',
            'course_group_title',
            'organization',
            'organization_title',
            'what_will_you_learn',
            'skills_you_gain',
            'credit_hours',
            'mode_of_course',
            'mode_of_course_title',
            'complexity_level',
            'complexity_level_title',
            'is_active',
            "course_module_data",
        ]


    def get_organization_title(self, obj):
        try:
            if obj.organization is not None:
                return obj.organization.name
            return None
        except Exception as e:
            print(str(e))
            return None


    def get_mode_of_course_title(self, obj):
        try:
            if obj.mode_of_course in [1,2,3]:
                return mode_of_course_choices[obj.mode_of_course-1][1]
            return None
        except Exception as e:
            print(str(e))
            return None
        
    def get_course_group_title(self, obj):
        try:
            if obj.course_group in [1,2]:
                return group_courses_choices[obj.course_group-1][1]
            return None
        except Exception as e:
            print(str(e))
            return None

    def get_complexity_level_title(self, obj):
        try:
            if obj.complexity_level in [1,2,3]:
                return complexity_level_choices[obj.complexity_level-1][1]
            return None
        except Exception as e:
            print(str(e))
            return None
        

    def get_course_module_data(self,obj):
        try:

            query=CourseModules.objects.filter(course=obj.id,is_active=True)
            # print(query)
            if not query.exists():
                return None
            
            data=ListCourseModulesViewsetSerializers(query,many=True).data
            print(data)

            
            return data

        except Exception as e:

            return None
 
