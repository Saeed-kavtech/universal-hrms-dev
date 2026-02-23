from .models import *
from departments.models import Departments
from rest_framework import serializers

class AssessmentTypesSerializers(serializers.ModelSerializer):
    class Meta:
        model = AssessmentTypes
        fields = ['id', 'title', 'is_technical', 'level' ,'is_active']

class AssessmentTestsSerializers(serializers.ModelSerializer):
    position_title = serializers.SerializerMethodField()
    assessment_type_title = serializers.SerializerMethodField()
    organization_title = serializers.SerializerMethodField()
    class Meta:
        model = AssessmentTests
        fields = ['id', 'title', 'organization', 'organization_title', 'position', 'position_title', 'assessment_type', 'assessment_type_title', 'duration', 'is_active', 'created_at', 'updated_at']

    def get_organization_title(self, obj):
        try:
            if obj.organization is not None:
                return obj.organization.name
            return None
        except Exception as e:
            return None

    def get_position_title(self, obj):
        try:
            if obj.position is not None:
                return obj.position.title
            return None
        except Exception as e:
            return None

    def get_assessment_type_title(self, obj):
        try:
            if obj.assessment_type is not None:
                return obj.assessment_type.title
            return None
        except Exception as e:
            return None


class CUAssessmentTestsSerializers(serializers.ModelSerializer):
    class Meta:
        model = AssessmentTests
        fields = ['assessment_type', 'organization', 'position', 'is_active']

class InActiveAssessmentTestFilesSerializers(serializers.ModelSerializer):
    class Metha:
        model = AssessmentTestFiles
        fields = ['organization', 'is_active']

class CUAssessmentTestFilesSerializers(serializers.ModelSerializer):
    class Meta:
        model = AssessmentTestFiles
        fields = ['assessment_test', 'uploaded_by', 'assessment_file']

class CreateQuestionsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = ['question', 'assessment_test_file', 'answer_option', 'answer', 'total_options', 'complexity_level', 'time']

class CreateQuestionOptionsSerializers(serializers.ModelSerializer):
    class Meta:
        model = QuestionOptions
        fields = ['question', 'option', 'value']

class CreateCandidateAssessmentTestSerializers(serializers.ModelSerializer):
    class Meta:
        model = CandidateAssessmentTest
        fields = ['candidate', 'assessment_test', 'is_email_sent', 'duration', 'candidate_job']

class CandidateAssessmentTestSerializers(serializers.ModelSerializer):
    class Meta:
        model = CandidateAssessmentTest
        fields = ['candidate', 'assessment_test', 'is_email_sent', 'duration', 'candidate_job']

class CandidateAssessmentTestMarksSerializers(serializers.ModelSerializer):
    assessment_test_title = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()
    class Meta:
        model = CandidateAssessmentTest
        fields = ['assessment_test_title', 'total_marks', 'total_marks_obtained', 'percentage', 'result', 'is_passed', 'is_completed']

    def get_assessment_test_title(self, obj):
        if obj.assessment_test is not None:
            return obj.assessment_test.title
        return None

    def get_percentage(self, obj):
        if obj.total_marks is None:
            return None
        if obj.total_marks_obtained is None:
                return None
        
        if obj.total_marks>0: 
            return round((obj.total_marks_obtained/obj.total_marks)*100,2)
        return None

class ListCandidateAssessmentTestSerializers(serializers.ModelSerializer):
    job_title = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    assessment_title = serializers.SerializerMethodField()
    assessment_type = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()
    class Meta:
        model = CandidateAssessmentTest
        fields = [
            'uuid', 'candidate', 'candidate_job', 'assessment_test', 
            'assessment_test_file', 'is_email_sent', 'duration', 'start_date_time', 'complete_date_time',
            'is_completed', 'result', 'is_passed', 'is_active', 'created_at', 
            'job_title', 'total_marks', 'total_marks_obtained', 'percentage',
            'position_title', 'assessment_title', 'assessment_type'
        ]

    def get_job_title(self, obj):
        if obj.candidate_job is not None:
            if obj.candidate_job.job_post is not None:
                return obj.candidate_job.job_post.job.title
        return None

    def get_position_title(self, obj):
        if obj.assessment_test.position is not None:
            return obj.assessment_test.position.title
        return None

    def get_assessment_title(self, obj):
        return obj.assessment_test.title

    def get_assessment_type(self, obj):
        if obj.assessment_test is not None:
            return obj.assessment_test.assessment_type.title
        return None

    def get_percentage(self, obj):
        if obj.total_marks is not None:
            if obj.total_marks>0:
                return round((obj.total_marks_obtained/obj.total_marks)*100,2)
        return None


class CreateCandidateAssessmentQuestionsSerializers(serializers.ModelSerializer):
    class Meta:
        model = CandidateAssessmentQuestions
        fields = ['candidate_assessment_test', 'question', 'time']

class AnswerCandidateAssessmentQuestionsSerializers(serializers.ModelSerializer):
    class Meta:
        model = CandidateAssessmentQuestions
        fields = ['answer', 'answer_option']

class ShowQuestionOptionsSerializers(serializers.ModelSerializer):
    class Meta:
        model = QuestionOptions 
        fields = ['option', 'value']

class ShowQuestionSerializers(serializers.ModelSerializer):
    question_options = ShowQuestionOptionsSerializers(many=True) 
    class Meta:
        model = Questions
        fields = ['id', 'question', 'complexity_level', 'clevel', 'time', 'question_options']

class AdminViewQuestionSerializers(serializers.ModelSerializer):
    question_options = ShowQuestionOptionsSerializers(many=True) 
    class Meta:
        model = Questions
        fields = ['question', 'complexity_level', 'clevel', 'time', 'answer', 'answer_option', 'question_options']



