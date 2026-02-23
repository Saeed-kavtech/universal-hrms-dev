from .models import * 
from rest_framework import serializers



class InterviewModeSerializers(serializers.ModelSerializer):
	class Meta:
		model = InterviewMode
		fields = ['id', 'title', 'organization', 'is_active']

class PreDataInterviewModeSerializers(serializers.ModelSerializer):
	class Meta:
		model = InterviewMode
		fields = ['id', 'title']


class ListCandidateInterviewsSerializers(serializers.ModelSerializer):
	interviewer_name = serializers.SerializerMethodField()
	time_slot_title = serializers.SerializerMethodField()
	mode_title = serializers.SerializerMethodField()
	created_at = serializers.SerializerMethodField()
	start_date_time = serializers.SerializerMethodField()
	complete_date_time = serializers.SerializerMethodField()
	reschedule_date = serializers.SerializerMethodField()

	class Meta:
		model = CandidateInterviews
		fields = [
			'id', 'interviewer', 'stage', 'interviewer_name', 'interview_date', 'interview_time_slot', 'time_slot_title',
			'interview_mode', 'mode_title', 'status', 'start_date_time', 'complete_date_time', 'is_cancel',
			'reason_for_cancel', 'is_reschedule', 'reschedule_date', 'is_active', 'created_at'
		]

	def get_reschedule_date(self, obj):
		try:
			return obj.reschedule_date.strftime('%Y-%m-%d %H:%M:%S')
		except Exception as e:
			print(str(e))
			return None

	def get_start_date_time(self, obj):
		try:
			return obj.start_date_time.strftime('%Y-%m-%d %H:%M:%S')
		except Exception as e:
			print(str(e))
			return None

	def get_complete_date_time(self, obj):
		try:
			return obj.complete_date_time.strftime('%Y-%m-%d %H:%M:%S')
		except Exception as e:
			print(str(e))
			return None


	def get_created_at(self, obj):
		try:
			return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
		except Exception as e:
			print(str(e))
			return None


	def get_interviewer_name(self, obj):
		if obj.interviewer is not None:
			return obj.interviewer.first_name+" "+obj.interviewer.last_name
		else:
			return None

	def get_time_slot_title(self, obj):
		if obj.interview_time_slot is not None:
			return obj.interview_time_slot.title
		else:
			return None

	def get_mode_title(self, obj):
		if obj.interview_mode is not None:
			return obj.interview_mode.title
		else:
			return None

class GetCandidateInterviewsSerializers(serializers.ModelSerializer):
	interviewer_name = serializers.SerializerMethodField()
	time_slot_title = serializers.SerializerMethodField()
	mode_title = serializers.SerializerMethodField()
	stage_title = serializers.SerializerMethodField()
	is_evaluation = serializers.SerializerMethodField()
	created_at = serializers.SerializerMethodField()
	start_date_time = serializers.SerializerMethodField()
	complete_date_time = serializers.SerializerMethodField()
	reschedule_date = serializers.SerializerMethodField()
	candidate_name=serializers.SerializerMethodField()
	position_title=serializers.SerializerMethodField()
	evaluation_score=serializers.SerializerMethodField()
	candidate_job_uuid=serializers.SerializerMethodField()
	interview_medium_title=serializers.SerializerMethodField()
	class Meta:
		model = CandidateInterviews
		fields = [
			'id', 'interviewer', 'candidate_job_uuid','candidate_job','position_title', 'candidate','candidate_name', 'stage', 'stage_title', 'interviewer_name', 'interview_date', 'interview_time_slot', 'time_slot_title',
			'interview_mode', 'mode_title', 'status', 'start_date_time', 'complete_date_time', 'is_cancel','evaluation_score','is_completed',
			'reason_for_cancel', 'is_reschedule', 'is_evaluation', 'reschedule_date', 'is_active', 'created_at','interview_url','comments','interview_medium','interview_medium_title'
		]

	def get_reschedule_date(self, obj):
		try:
			return obj.reschedule_date.strftime('%Y-%m-%d %H:%M:%S')
		except Exception as e:
			print(str(e))
			return None

	def get_start_date_time(self, obj):
		try:
			return obj.start_date_time.strftime('%Y-%m-%d %H:%M:%S')
		except Exception as e:
			print(str(e))
			return None

	def get_complete_date_time(self, obj):
		try:
			return obj.complete_date_time.strftime('%Y-%m-%d %H:%M:%S')
		except Exception as e:
			print(str(e))
			return None


	def get_created_at(self, obj):
		try:
			return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
		except Exception as e:
			print(str(e))
			return None

	def get_stage_title(self, obj):
		if obj.stage is not None:
			return obj.stage.title
		return None

	def get_interviewer_name(self, obj):
		if obj.interviewer is not None:
			return obj.interviewer.first_name+" "+obj.interviewer.last_name
		else:
			return None

	def get_time_slot_title(self, obj):
		if obj.interview_time_slot is not None:
			return obj.interview_time_slot.title
		else:
			return None

	def get_mode_title(self, obj):
		if obj.interview_mode is not None:
			return obj.interview_mode.title
		else:
			return None

	def get_is_evaluation(self, obj):
		if obj.stage is not None:
			if obj.stage.is_evaluation==True:
				#Process the evalution score
				return True
		return None
	

	def get_candidate_name(self, obj):
		if obj.candidate is not None:
				#Process the evalution score
				return obj.candidate.candidate_name
		return None
	
	def get_position_title(self, obj):
		if obj.candidate_job is not None and obj.candidate_job.job_post is not None and obj.candidate_job.job_post.job is not None and obj.candidate_job.job_post.job.position is not None:
				#Process the evalution score
				return obj.candidate_job.job_post.job.position.title
		return None
	
	def get_candidate_job_uuid(self,obj):
		if obj.candidate_job is not None:
			return obj.candidate_job.uuid
		return None
	
	def get_evaluation_score(self,obj):
		if obj.candidate_job is not None:
			return obj.candidate_job.evaluation_score
		return None
	
	def get_interview_medium_title(self,obj):
		if obj.interview_medium is not None:
			return obj.interview_medium.title
		return None

class CandidateInterviewsSerializers(serializers.ModelSerializer):
	class Meta:
		model = CandidateInterviews 
		fields = [
			'id', 'candidate', 'candidate_job', 'stage', 'interviewer', 'interview_date', 
			'interview_time_slot', 'interview_mode', 'is_active', 'status','interview_url','comments','interview_medium'
		]

class UpdateCandidateInterviewsSerializers(serializers.ModelSerializer):
	class Meta:
		model = CandidateInterviews
		fields = ['interviewer', 'interview_date', 'interview_time_slot', 'interview_mode']

class StartCandidateInterviewsSerializers(serializers.ModelSerializer):
	class Meta:
		model = CandidateInterviews
		fields = ['start_date_time', 'status']

	# def validate(self, data):
	# 	start_date_time = data.get('start_date_time')
		
	# 	if start_date_time:
	# 		raise serializers.ValidationError("Start data time not be empty.")

	# 	return data

class CancelCandidateInterviewsSerializers(serializers.ModelSerializer):
	class Meta:
		model = CandidateInterviews
		fields = ['reason_for_cancel', 'is_cancel', 'is_active', 'status']

	def validate(self, data):
		reason_for_cancel = data.get('reason_for_cancel')
		is_cancel = data.get('is_cancel')
		is_active = data.get('is_active')
		if len(reason_for_cancel.strip())==0:
			raise serializers.ValidationError("Reason for cancel not be empty.")

		if is_cancel==False or is_cancel is None:
			raise serializers.ValidationError("Cancel must be set True.")
		if is_active==True or is_active is None:
			raise serializers.ValidationError("Candidate Interview must be set active false.")

		return data

class CompleteCandidateInterviewsSerializers(serializers.ModelSerializer):
	class Meta:
		model = CandidateInterviews
		fields = ['is_completed', 'complete_date_time', 'status']

	# def validate(self, data):
	# 	complete_date_time = data.get('complete_date_time')
	# 	is_completed = data.get('is_completed')
	# 	if len(complete_date_time.strip())==0:
	# 		raise serializers.ValidationError("Complete data time not be empty.")

	# 	if is_completed==True or is_completed is None:
	# 		raise serializers.ValidationError("Complete must be set True.")
		
	# 	return data
class InterviewMediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewMedium
        fields = '__all__'