from .models import * 
from candidate_emails.models import * 
from rest_framework import serializers

class TemplateVariablesSerializers(serializers.ModelSerializer):
	class Meta:
		model = TemplateVariables
		fields = [
			'id', 'title', 'code', 'organization', 'short_code', 'description', 
			'is_email', 'is_certificate', 'is_interview', 'is_active'
		]

class EmailTemplatesSerializers(serializers.ModelSerializer):
	class Meta:
		model = EmailTemplates
		fields = [
			'id', 'uuid', 'title', 'organization', 'user', 'subject_line', 'body', 
			'footer', 'has_attachments', 'is_active'
		]

class PreDataEmailTemplatesSerializers(serializers.ModelSerializer):
	class Meta:
		model = EmailTemplates
		fields = ['id', 'title']


class GetCandidateEmailsSerializers(serializers.ModelSerializer):
	stage_title = serializers.SerializerMethodField()
	stage_type_title = serializers.SerializerMethodField()
	email_template_title = serializers.SerializerMethodField()
	candidate_job_uuid = serializers.SerializerMethodField()
	created_at = serializers.SerializerMethodField()
	has_attachments = serializers.SerializerMethodField()

	class Meta:
		model = CandidateEmails
		fields = ['id', 'uuid', 'candidate', 'candidate_job', 'candidate_job_uuid', 'stage', 'stage_title',
			'stage_type', 'stage_type_title', 'email_template', 'email_template_title', 'has_attachments', 'status', 'is_active', 'created_at'
			]

	def get_stage_title(self, obj):
		if obj.stage is not None:
			return obj.stage.title
		elif obj.stage_type is not None:
			return obj.stage_type.title
		return None

	def get_stage_type_title(self, obj):
		if obj.stage_type is not None:
			return obj.stage_type.title
		return None

	def get_created_at(self, obj):
		try:
			return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')	
		except:
			return None
	
	
	def get_candidate_job_uuid(self, obj):
		if obj.candidate_job is not None:
			return obj.candidate_job.uuid
		return None

	def get_email_template_title(self, obj):
		if obj.email_template is not None:
			return obj.email_template.title
		return None

	def get_has_attachments(self, obj):
		if obj.email_template:
			return obj.email_template.has_attachments
		return None


class CandidateEmailAttachmentsSerializers(serializers.ModelSerializer):
	class Meta:
		model = CandidateEmailAttachments  
		fields = ['candidate_email', 'attachment']


class CUCandidateEmailBodySerializers(serializers.ModelSerializer):
	class Meta:
		model = CandidateEmailBody  
		fields = ['id', 'candidate_email', 'subject', 'body', 'footer']

class GetCandidateEmailBodySerializers(serializers.ModelSerializer):
	class Meta:
		model = CandidateEmailBody  
		fields = ['id', 'candidate_email', 'subject', 'body', 'footer']


class EmailRecipientsSerializer(serializers.ModelSerializer):
	employee_name=serializers.SerializerMethodField()
	class Meta:
		model = EmailRecipients
		fields = ['id', 'title', 'level', 'employee','employee_name', 'created_by', 'is_active', 'created_at', 'updated_at']
	
	def get_employee_name(self,obj):
		try:
			return obj.employee.name

		except Exception as e:
			return None


			
