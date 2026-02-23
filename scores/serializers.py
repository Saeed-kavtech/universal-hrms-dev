from .models import * 
from rest_framework import serializers



class ComplexityLevelsSerializers(serializers.ModelSerializer):
	class Meta:
		model = ComplexityLevels
		fields = '__all__'

class ScoreTypesSerializers(serializers.ModelSerializer):
	class Meta:
		model = ScoreTypes
		fields = '__all__'

class ScoresSerializers(serializers.ModelSerializer):
	complexity_level_title = serializers.SerializerMethodField()
	score_type_title = serializers.SerializerMethodField()

	class Meta:
		model = Scores
		fields = [
			'id', 'organization', 'complexity_level', 'complexity_level_title', 'score', 'complexity_score', 'score_type', 
			'score_type_title', 'is_active'
		]

	def get_complexity_level_title(self, obj):
		if obj.complexity_level is not None:
			complexity_level = ComplexityLevels.objects.filter(level=obj.complexity_level, is_active=True)
			if complexity_level.exists():
				complexity_level = complexity_level.last()
				return complexity_level.title
		return None

	def get_score_type_title(self, obj):
		if obj.score_type is not None:
			return obj.score_type.title
		return None
