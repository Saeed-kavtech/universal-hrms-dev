from .models import *
from departments.models import Departments
from rest_framework import serializers
from candidates.models import CandidateJobs
from jd.models import JdSpecifications
from jd.serializers import JdSpecificationsSerializers

class JobTypesSerializers(serializers.ModelSerializer):
    class Meta:
        model = JobTypes
        fields = ['id', 'title', 'level' ,'is_active']


class CreateUpdateJobsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = [ 'department', 'staff_classification', 'position' ,'job_code', 'title', 'reports_to']




class JobPostsSerializers(serializers.ModelSerializer):
    class Meta:
        model = JobPosts
        exclude = ['updated_at']
        # fields = [
        # 	'jd_selection', 'project', 'job_type' ,'job_post_code', 'purpose', 'jp_reports_to', 
        # 	'no_of_individuals', 'post_date', 'expiry_date'
        # ]


class JobsSerializers(serializers.ModelSerializer):
	job_posts = JobPostsSerializers(many=True)
	class Meta:
		model = Jobs
		fields = [
        'uuid', 'department', 'staff_classification' ,'position', 'created_by', 'job_code', 'title', 
        'reports_to', 'status', 'is_active', 'created_at', 'job_posts'
        ]

class JobListPostSerializers(serializers.ModelSerializer):
    job_uuid = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    job_post_id = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    department_title = serializers.SerializerMethodField()
    staff_classification = serializers.SerializerMethodField()
    staff_classification_title = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    job_code = serializers.SerializerMethodField()
    reports_to = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    job_is_active = serializers.SerializerMethodField()
    total_applicants = serializers.SerializerMethodField()
    class Meta:
        model = JobPosts
        fields = [
            'job_uuid', 'title', 'job_post_id', 'department', 'department_title', 'staff_classification', 
            'staff_classification_title', 'position','position_title', 'created_by',
            'job_code', 'reports_to', 'created_at', 'uuid', 'total_applicants',
            'jd_selection', 'project', 'job_type' ,'job_post_code', 'purpose', 'jp_reports_to',
            'no_of_individuals', 'post_date', 'expiry_date', 'job_is_active', 'is_active'
        ]

    def get_job_uuid(self, obj):
        return obj.job.uuid

    def get_title(self, obj):
        return obj.job.title

    def get_job_post_id(self, obj):
        return obj.id

    def get_total_applicants(self, obj):
        applicants = CandidateJobs.objects.filter(job_post=obj.id)
        if applicants.exists():
            return applicants.count()
        return None


    def get_department(self, obj):
        if obj.job.department is not None:
            return obj.job.department.id 
        else:
            return None


    def get_department_title(self, obj):
        try:
            return obj.job.department.title
        except Exception as e:
            print(str(e))
            return None

        
    def get_staff_classification(self, obj):
        if obj.job.staff_classification is not None:
            return obj.job.staff_classification.id
        else:
            return None


    def get_staff_classification_title(self, obj):
        try:
            return obj.job.staff_classification.title
        except Exception as e:
            print(str(e))
            return None
            
        

    def get_position(self, obj):
        if obj.job.position is not None:
            return obj.job.position.id
        else:
            return None

    def get_position_title(self, obj):
        try:
            return obj.job.position.title
        except Exception as e:
            print(str(e))
            return None

    def get_created_by(self, obj):
        if obj.job.created_by is not None:
            return obj.job.created_by.id
        else:
            return None

    def get_job_code(self, obj):
        return obj.job.job_code

    def get_reports_to(self, obj):
        return obj.job.reports_to

    def get_job_is_active(self, obj):
        return obj.job.is_active

    def get_created_at(self, obj):
        return obj.job.created_at

class CreateUpdateJobPostsSerializers(serializers.ModelSerializer):
    class Meta:
        model = JobPosts
        fields = [
        	'jd_selection', 'project', 'job_type' ,'job_post_code', 'purpose', 'jp_reports_to', 
        	'no_of_individuals', 'post_date', 'expiry_date'
        ]


class JobsForKavtechWebsiteSerializers(serializers.ModelSerializer):
    job_uuid = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    job_post_id = serializers.SerializerMethodField()
    job_code = serializers.SerializerMethodField()
    jd_description = serializers.SerializerMethodField()
    jd_title = serializers.SerializerMethodField()
    jd_specification_data = serializers.SerializerMethodField()
    class Meta:
        model = JobPosts
        fields = [
            'job_uuid', 
            'title', 
            'job_post_id',
            'uuid', 
            'job_code',
            'jd_selection', 
            'jd_title',
            'jd_description', 
            'jd_specification_data',
            'job_type' ,
            'no_of_individuals',
            'is_active',
        ]

  
    def get_title(self, obj):
        return obj.job.title

    def get_job_post_id(self, obj):
        return obj.id
    
    def get_job_uuid(self, obj):
        try:
            return obj.job.uuid
        except Exception as e:
            print(str(e))
            return None


    def get_job_code(self, obj):
        try:    
            return obj.job.job_code
        except Exception as e:
            print(str(e))
            return None

    def get_job_is_active(self, obj):
        try:
            return obj.job.is_active
        except Exception as e:
            print(str(e))
            return None

    def get_jd_title(self, obj):
        try:
            return obj.jd_selection.title
            
        except Exception as e:
            print(str(e))
            return None

    def get_jd_description(self, obj):
        try:
            return obj.jd_selection.main_responsibilities
        except Exception as e:
            print(str(e))
            return None
        
    def get_jd_specification_data(self, obj):
        try:
            query = JdSpecifications.objects.filter(jd=obj.jd_selection.id, is_active=True)
            serializer = JdSpecificationsSerializers(query, many=True)
            return serializer.data
        except Exception as e:
            print(str(e))
            return None


        

