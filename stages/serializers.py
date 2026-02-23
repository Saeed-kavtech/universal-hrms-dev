from .models import * 
from rest_framework import serializers


class StagesSerializers(serializers.ModelSerializer):
	email_template_title=serializers.SerializerMethodField()
	procedure_title=serializers.SerializerMethodField()
	class Meta:
		model = Stages
		fields = [
			'id', 'title', 'procedure','procedure_title','organization', 'level', 'description', 'is_email', 'notify_to_admin',
			'is_interview', 'is_evaluation', 'is_auto_sent_email', 'email_template','email_template_title', 'is_active'
		]

	def get_email_template_title(self, obj):
		try:
			return obj.email_template.title
		except Exception as e:
			return None
		
	def get_procedure_title(self, obj):
		try:
			return obj.procedure.title
		except Exception as e:
			return None




class StageTypeTemplatesSerializers(serializers.ModelSerializer):
	stage_type_title = serializers.SerializerMethodField()
	class Meta:
		model = StageTypeTemplates  
		fields = ['id', 'title', 'stage_type', 'organization', 'stage_type_title', 'level', 
			'is_email', 'is_auto_sent_email', 'email_template', 'is_active', 'created_at'
		]

	def validate(self, data):
		instance = self.instance
		
		stage_type = data.get('stage_type')
		organization = data.get('organization')
		
		if instance is not None:
			if StageTypeTemplates.objects.exclude(id=instance.id).filter(stage_type=stage_type, organization=organization).exists():
				raise serializers.ValidationError("This stage value already exists.")
		if StageTypeTemplates.objects.filter(stage_type=stage_type, organization=organization).exists():
			raise serializers.ValidationError("This stage value already exists.")

		return data

	def get_stage_type_title(self, obj):
		try:
			return Stage_Types[obj.stage_type-1][1]
		except Exception as e:
			return None


class ListStageTypeTemplatesSerializers(serializers.ModelSerializer):
	stage_type_title = serializers.SerializerMethodField()
	class Meta:
		model = StageTypeTemplates  
		fields = ['id', 'title', 'stage_type', 'stage_type_title', 'organization', 'level', 
			'is_email', 'is_auto_sent_email', 'email_template', 'is_active', 'created_at'
		]

	def get_stage_type_title(self, obj):
		try:
			return Stage_Types[obj.stage_type-1][1]
		except Exception as e:
			return None


