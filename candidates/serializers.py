import regex
from rest_framework import serializers
from .models import *

from assessments.models import CandidateAssessmentTest
from assessments.serializers import CandidateAssessmentTestMarksSerializers




class CandidatesViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = Candidates
        fields = ['candidate_name', 'email', 'cnic_no', 'mobile_no', 'linkedin_profile','is_already_applied','reference_name','reference_connection']

class CreateCandidatesViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = Candidates
        fields = ['id', 'candidate_name','is_already_applied','organization', 'email', 'cnic_no', 'mobile_no', 'linkedin_profile','reference_name','reference_connection']

    def validate(self, data):
        cnic_no = data.get('cnic_no')
        mobile_no = data.get('mobile_no')
        linkedin_profile_url = data.get('linkedin_profile')
        # upload_resume = data.get('upload_resume')
        
        # validation for CNIC Number
        # cnic_pattern = "^[0-9]{5}-[0-9]{7}-[0-9]$"
        # is_cnic_format_valid = regex.match(cnic_pattern, cnic_no)
        # if not is_cnic_format_valid:
        #     raise serializers.ValidationError("Number of characters enter must be 15 and in the following format: *****-*******-*")
       
        # validation for Mobile number
        # mobile_no_format = "^(\+923[0-4]{1}|03[0-4]{1})[0-9]{8}"
        # is_mobile_no_format_valid = regex.match(mobile_no_format, mobile_no)  
        # if len(mobile_no) not in [11, 13]:
        #     raise serializers.ValidationError("Number of digits are incorrect")
        # elif not (is_mobile_no_format_valid):
        #     raise serializers.ValidationError("Mobile Number format is not valid. Please check if number starts with +92 or 03")
            
        # validation for linkedin profile
        # request = requests.get(linkedin_profile_url)
    
        #validation for resume format
        # resume_format = ".*\.(jpg|doc|pdf)$"
        # is_resume_format_valid = regex.match(resume_format, upload_resume) 
        # print(is_resume_format_valid)
        # if not is_resume_format_valid:
        #     raise serializers.ValidationError("Resume format is incorrect")

        return data


class UpdateCandidatesViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = Candidates
        fields = ['id', 'candidate_name','is_already_applied','organization', 'email', 'cnic_no', 'mobile_no', 'linkedin_profile','reference_name','reference_connection']

    def validate(self, data):
        cnic_no = data.get('cnic_no') or None
        mobile_no = data.get('mobile_no') or None
        linkedin_profile_url = data.get('linkedin_profile') or None
        # upload_resume = data.get('upload_resume') or None
        
        # validation for CNIC Number
        # if cnic_no is not None:
        #     cnic_pattern = "^[0-9]{5}-[0-9]{7}-[0-9]$"
        #     is_cnic_format_valid = regex.match(cnic_pattern, cnic_no)
        #     if not is_cnic_format_valid:
        #         raise serializers.ValidationError("Number of characters enter must be 15 and in the following format: *****-*******-*")
       
        # validation for Mobile number
        # if mobile_no is not None:
        #     mobile_no_format = "^(\+923[0-4]{1}|03[0-4]{1})[0-9]{8}"
        #     is_mobile_no_format_valid = regex.match(mobile_no_format, mobile_no)  
        #     if len(mobile_no) not in [11, 13]:
        #         raise serializers.ValidationError("Number of digits are incorrect")
        #     elif not (is_mobile_no_format_valid):
        #         raise serializers.ValidationError("Mobile Number format is not valid. Please check if number starts with +92 or 03")

        return data


class CreateUpdateCandidateJobsSerializers(serializers.ModelSerializer):
    class Meta:
        model = CandidateJobs
        fields = ['candidate', 'job_post', 'stage', 'resume', 'time_interval']

class ListCandidateJobsSerializers(serializers.ModelSerializer):
    job_title = serializers.SerializerMethodField()
    candidate_name = serializers.SerializerMethodField()
    cnic_no = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    candidate_uuid = serializers.SerializerMethodField()
    stage_is_interview = serializers.SerializerMethodField()
    stage_is_evaluation = serializers.SerializerMethodField()
    stage_is_email = serializers.SerializerMethodField()
    candidate_job_assessments = serializers.SerializerMethodField()
    time_interval_title = serializers.SerializerMethodField()
    total_pages_qualified = serializers.SerializerMethodField()
    total_pages_disqualified = serializers.SerializerMethodField()
    is_already_applied=serializers.SerializerMethodField()
    stage_title=serializers.SerializerMethodField()
    class Meta:
        model = CandidateJobs
        fields = [
        'id', 'uuid', 'candidate_uuid', 'candidate','is_already_applied', 'job_post', 'time_interval', 'time_interval_title', 'resume', 'stage','stage_title', 'evaluation_score', 'status', 
        'is_active', 'job_title', 'candidate_name', 'cnic_no', 'email', 'stage_is_interview', 'stage_is_evaluation',
        'stage_is_email', 'is_qualified', 'disqualified_time', 'candidate_job_assessments', 
        'total_pages_qualified', 'total_pages_disqualified'
        ]

    def get_candidate_job_assessments(self, obj):
        result = {"non_tech_test": None, "tech_test": None}
        try:
            candidate_assessment_tests = CandidateAssessmentTest.objects.filter(candidate=obj.candidate.id)

            # self.context.get('candidate_assessment_test_data')
            if candidate_assessment_tests.exists(): 
                non_tech_test = candidate_assessment_tests.filter(assessment_test__assessment_type__is_technical=False)
                if non_tech_test.exists():
                    # non_tech_test = non_tech_test.last()
                    if non_tech_test.filter(total_marks__isnull=False):
                        ntt_ser = CandidateAssessmentTestMarksSerializers(non_tech_test, many=True)
                        result['non_tech_test'] = ntt_ser.data

                tech_test = candidate_assessment_tests.filter(assessment_test__assessment_type__is_technical=True, assessment_test__position__id=obj.job_post.job.position.id )
                if tech_test.exists():
                    # tech_test = tech_test.last()
                    if tech_test.filter(total_marks__isnull=False):
                        tech_serializer = CandidateAssessmentTestMarksSerializers(tech_test, many=True)
                        result['tech_test'] = tech_serializer.data

            return result

        except Exception as e:
            return result

    def get_total_pages_qualified(self, obj):
        try:
            return self.context.get('total_pages_qualified')
        except Exception as e:
            print(str(e))
            return None
        
    def get_total_pages_disqualified(self, obj):
        try:
            return self.context.get('total_pages_disqualified')
        except Exception as e:
            print(str(e))
            return None

    def get_time_interval_title(self, obj):
        try:
            if obj.time_interval is not None:
                return f"{obj.time_interval.title} ({obj.time_interval.start_time.strftime('%H:%S')}-{obj.time_interval.end_time.strftime('%H:%S')})"
            return None
        except Exception as e:
            return None

    def get_job_title(self, obj):
        return obj.job_post.job.title

    def get_candidate_name(self, obj):
        return obj.candidate.candidate_name
    
    def get_is_already_applied(self, obj):
        return obj.candidate.is_already_applied

    def get_candidate_uuid(self, obj):
        return obj.candidate.uuid

    def get_cnic_no(self, obj):
        return obj.candidate.cnic_no

    def get_email(self, obj):
        return obj.candidate.email

    def get_stage_is_interview(self, obj):
        if obj.stage is not None:
            if obj.stage.is_interview is not None:
                return obj.stage.is_interview
        return None
    
    def get_stage_title(self, obj):
        if obj.stage is not None:
                return obj.stage.title
        return None

    def get_stage_is_evaluation(self, obj):
        if obj.stage is not None:
            if obj.stage.is_evaluation is not None:
                return obj.stage.is_evaluation
        return None

    def get_stage_is_email(self, obj):
        if obj.stage is not None:
            if obj.stage.is_email is not None:
                return obj.stage.is_email
        return None


class ListCandidateJobsDataSerializers(serializers.ModelSerializer):
    job_title = serializers.SerializerMethodField()
    stage_is_evaluation = serializers.SerializerMethodField()
    staff_classification=serializers.SerializerMethodField()
    position=serializers.SerializerMethodField()
    department=serializers.SerializerMethodField()
    staff_classification_title=serializers.SerializerMethodField()
    position_title=serializers.SerializerMethodField()
    department_title=serializers.SerializerMethodField()
    stage_title=serializers.SerializerMethodField()
    candidate_data=serializers.SerializerMethodField()
    class Meta:
        model = CandidateJobs
        fields = [
        'id', 'uuid', 'candidate', 'job_post', 'time_interval', 'resume', 'stage','stage_title', 'evaluation_score', 'status', 
        'is_active', 'job_title', 'stage_is_evaluation', 'is_qualified', 'disqualified_time','staff_classification','staff_classification_title'
        ,'position','position_title','department','department_title',"candidate_data",
        ]
    def get_job_title(self, obj):
        return obj.job_post.job.title

    def get_stage_title(self, obj):
        if obj.stage is not None:
                return obj.stage.title
        return None

    def get_stage_is_evaluation(self, obj):
        if obj.stage is not None:
            if obj.stage.is_evaluation is not None:
                return obj.stage.is_evaluation
        return None

    def get_staff_classification(self, obj):
        if obj.job_post is not None and obj.job_post.job is not None and obj.job_post.job.staff_classification is not None:
          return obj.job_post.job.staff_classification.id
        
        return None
    
    
    def get_position(self, obj):
        if obj.job_post is not None and obj.job_post.job is not None and obj.job_post.job.position is not None:
          return obj.job_post.job.position.id
        
        return None
    
    def get_department(self, obj):
        if obj.job_post is not None and obj.job_post.job is not None and obj.job_post.job.department is not None:
          return obj.job_post.job.department.id
        
        return None

    
    def get_staff_classification_title(self, obj):
        if obj.job_post is not None and obj.job_post.job is not None and obj.job_post.job.staff_classification is not None:
          return obj.job_post.job.staff_classification.title
        return None
    
    def get_position_title(self, obj):
        if obj.job_post is not None and obj.job_post.job is not None and obj.job_post.job.position is not None:
          return obj.job_post.job.position.title
        return None
    
    def get_department_title(self, obj):
        if obj.job_post is not None and obj.job_post.job is not None and obj.job_post.job.department is not None:
          return obj.job_post.job.department.title
        return None
    
    def get_candidate_data(self,obj):
        try:
            
            query=Candidates.objects.get(id=obj.candidate.id,is_active=True)

            serializer=CandidatesViewsetSerializers(query,many=False)

            return serializer.data

        except Exception as e:
            return None

 

class ListCandidateByPositionSerializers(serializers.ModelSerializer):
    job_title = serializers.SerializerMethodField()
    candidate_name = serializers.SerializerMethodField()
    cnic_no = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    candidate_uuid = serializers.SerializerMethodField()
    stage_is_interview = serializers.SerializerMethodField()
    stage_is_evaluation = serializers.SerializerMethodField()
    stage_is_email = serializers.SerializerMethodField()
    candidate_job_assessments = serializers.SerializerMethodField()
    time_interval_title = serializers.SerializerMethodField()
    total_job_count = serializers.SerializerMethodField()
    class Meta:
        model = CandidateJobs
        fields = [
        'id', 'uuid', 'candidate_uuid', 'candidate', 'job_post', 'time_interval', 'time_interval_title', 'resume', 'stage', 'evaluation_score', 'status', 
        'is_active', 'job_title', 'candidate_name', 'cnic_no', 'email', 'stage_is_interview', 'stage_is_evaluation',
        'stage_is_email', 'is_qualified', 'disqualified_time', 'candidate_job_assessments', 'total_job_count'
        ]

    def get_total_job_count(self, obj):
        return obj.total_job_count

    def get_candidate_job_assessments(self, obj):
        result = {"non_tech_test": None, "tech_test": None}
        try:
            candidate_assessment_tests = CandidateAssessmentTest.objects.filter( candidate=obj.candidate.id)

            if candidate_assessment_tests.exists(): 
                non_tech_test = candidate_assessment_tests.filter(assessment_test__assessment_type__is_technical=False)
                if non_tech_test.exists():
                    # non_tech_test = non_tech_test.last()
                    ntt_ser = CandidateAssessmentTestMarksSerializers(non_tech_test, many=True)
                    result['non_tech_test'] = ntt_ser.data

                tech_test = candidate_assessment_tests.filter(assessment_test__assessment_type__is_technical=True, assessment_test__position__id=obj.job_post.job.position.id )
                if tech_test.exists():
                    # tech_test = tech_test.last()
                    tech_serializer = CandidateAssessmentTestMarksSerializers(tech_test, many=True)
                    result['tech_test'] = tech_serializer.data

            return result

        except Exception as e:
            return result

    def get_time_interval_title(self, obj):
        try:
            if obj.time_interval is not None:
                return f"{obj.time_interval.title} ({obj.time_interval.start_time.strftime('%H:%S')}-{obj.time_interval.end_time.strftime('%H:%S')})"
        except Exception as e:
            return None

    def get_job_title(self, obj):
        return obj.job_post.job.title

    def get_candidate_name(self, obj):
        return obj.candidate.candidate_name

    def get_candidate_uuid(self, obj):
        return obj.candidate.uuid

    def get_cnic_no(self, obj):
        return obj.candidate.cnic_no

    def get_email(self, obj):
        return obj.candidate.email

    def get_stage_is_interview(self, obj):
        if obj.stage is not None:
            if obj.stage.is_interview is not None:
                return obj.stage.is_interview
        return None

    def get_stage_is_evaluation(self, obj):
        if obj.stage is not None:
            if obj.stage.is_evaluation is not None:
                return obj.stage.is_evaluation
        return None

    def get_stage_is_email(self, obj):
        if obj.stage is not None:
            if obj.stage.is_email is not None:
                return obj.stage.is_email
        return None


class UpdateCandidateStatusSerializers(serializers.ModelSerializer):
    class Meta:
        model = CandidateJobs
        fields = ['is_qualified', 'disqualified_time']

class CreateCandidateStatusLogSerializers(serializers.ModelSerializer):
    class Meta:
        model = CandidateStatusLog  
        fields = ['candidate', 'candidate_job', 'action_by', 'action', 'action_reason']

class RecruitmentStagesSerializers(serializers.ModelSerializer):
    class Meta:
        model = RecruitmentStages
        fields = '__all__'


class UpdateCandidateStagesSerializers(serializers.ModelSerializer):
    class Meta:
        model = CandidateJobs
        fields = ['uuid', 'stage']