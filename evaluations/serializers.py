from .models import * 
from rest_framework import serializers


class RoleProcedureAccessSerializers(serializers.ModelSerializer):
	class Meta:
		model = RoleProcedureAccess
		fields = ['id', 'role', 'procedure', 'is_allow', 'is_active']

class UpdateRoleProcedureAccessSerializers(serializers.ModelSerializer):
	class Meta:
		model = RoleProcedureAccess
		fields = ['id', 'is_allow', 'is_active']

class EvaluationsSerializers(serializers.ModelSerializer):
	procedure_title=serializers.SerializerMethodField()
	class Meta:
		model = Evaluations
		fields = ['id', 'uuid', 'title', 'organization', 'user', 'procedure','procedure_title','description', 'is_active']

	def get_procedure_title(self,obj):
		try:
			return obj.procedure.title

		except Exception as e:
			return None

class EvaluationProcedureQuestionsSerializers(serializers.ModelSerializer):
	class Meta:
		model = EvaluationProcedureQuestions
		fields = ['id', 'evaluation', 'procedure', 'question', 'complexity_level', 'score', 'is_active']

class CreateCandidateEvaluationsSerializers(serializers.ModelSerializer):
	class Meta:
		model = CandidateEvaluations  
		fields = [
			'id', 'candidate', 'candidate_job', 'stage', 'evaluation', 'evaluated_by'
		]

class UpdateCandidateEvaluationsSerializers(serializers.ModelSerializer):
	class Meta:
		model = CandidateEvaluations  
		fields = ['evaluation', 'evaluated_by']

class GetCandidateEvaluationsSerializers(serializers.ModelSerializer):
	evaluation_title = serializers.SerializerMethodField()
	evaluated_by_name = serializers.SerializerMethodField()
	created_at = serializers.SerializerMethodField()
	percentage = serializers.SerializerMethodField()
	evaluation_remarks_title = serializers.SerializerMethodField()
	class Meta:
		model = CandidateEvaluations
		fields = [
			'id', 'candidate', 'candidate_job', 'stage', 'evaluation', 'evaluation_title', 'evaluated_by', 'evaluated_by_name',
			'comment', 'is_start', 'start_date_time', 'is_completed', 'total_marks', 'total_marks_obtained', 'percentage', 'recommendation', 'is_rechecked', 'is_mark_done', 'is_cancel',
			'cancel_by', 'cancel_date_time', 'reason_for_cancel', 'evaluation_remarks', 'evaluation_remarks_title', 'is_active', 'created_at'
		]

	def get_created_at(self, obj):
		try:
			return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
		except:
			return None

	def get_evaluation_remarks_title(self, obj):
		try:
			if obj.evaluation_remarks is not None:
				return EVALUATION_REMARKS[obj.evaluation_remarks-1][1]

			return None
		except Exception as e:
			return None
			
	def get_percentage(self, obj):
		try:
			if obj.total_marks > 0:
				return round((obj.total_marks_obtained/obj.total_marks)*100, 2)
		except Exception as e:
			return 0

	def get_evaluation_title(self, obj):
		if obj.evaluation is not None:
			return obj.evaluation.title
		else:
			return None

	def get_evaluated_by_name(self, obj):
		if obj.evaluated_by is not None:
			return obj.evaluated_by.first_name+" "+obj.evaluated_by.last_name
		return None

class SubmitCandidateEvaluationsSerializers(serializers.ModelSerializer):
	class Meta:
		model = CandidateEvaluations
		fields = ['comment', 'recommendation', 'evaluation_remarks']

class CancelCandidateEvaluationsSerializers(serializers.ModelSerializer):
	class Meta:
		model = CandidateEvaluations
		fields = ['reason_for_cancel', 'is_active', 'is_completed', 'is_cancel', 'cancel_date_time', 'cancel_by']

class CreateCandidateEvaluationQuestionRemarksSerializers(serializers.ModelSerializer):
	class Meta:
		model = CandidateEvaluationQuestionRemarks  
		fields = ['candidate_evaluation', 'evaluation_procedure_question', 'is_active']

class SubmitCandidateEvaluationQuestionRemarksSerializers(serializers.ModelSerializer):
	class Meta:
		model = CandidateEvaluationQuestionRemarks  
		fields = ['comment', 'score', 'complexity_level']

class ListCandidateEvaluationQuestionRemarksSerializers(serializers.ModelSerializer):
	question = serializers.SerializerMethodField()
	created_at = serializers.SerializerMethodField()
	class Meta:
		model = CandidateEvaluationQuestionRemarks  
		fields = ['id', 'question', 'candidate_evaluation', 'evaluation_procedure_question', 'score', 'comment', 'is_active', 'created_at']

	
	def get_created_at(self, obj):
		return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
	

	def get_question(self, obj):
		return obj.evaluation_procedure_question.question
		
	


class PreDataEvaluationsSerializers(serializers.ModelSerializer):
	class Meta:
		model = Evaluations 
		fields = ['id', 'title']


class CandidateJobActionLogs(serializers.ModelSerializer):   
    class Meta:
        model = CandidateJobActionLogs
        fields = ['id', 'candidate_job','candidate_evaluation', 'title', 'action_by', 'is_active', 'created_at', 'updated_at']
