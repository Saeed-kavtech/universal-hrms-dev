from .models import * 
from rest_framework import serializers


class TimeIntervalsSerializers(serializers.ModelSerializer):
	class Meta:
		model = TimeIntervals
		fields = ['id', 'title', 'organization', 'level', 'start_time', 'end_time', 'is_active']

class ChoicesTimeIntervalsSerializers(serializers.ModelSerializer):
	time_interval_title = serializers.SerializerMethodField()
	class Meta:
		model = TimeIntervals
		fields = ['id', 'time_interval_title']

	def get_time_interval_title(self, obj):
		try:
			if obj.start_time is not None and obj.end_time is not None:
				return f"{obj.title} ({obj.start_time.strftime('%H:%M')}-{obj.end_time.strftime('%H:%M')})"
			return obj.title
		except Exception as e:
			return None


class TimeSlotsSerializers(serializers.ModelSerializer):
	class Meta:
		model = TimeSlots
		fields = ['id', 'title', 'time_interval', 'from_time', 'to_time', 'is_active']

class PreDataTimeSlotsSerializers(serializers.ModelSerializer):
	class Meta:
		model = TimeSlots
		fields = ['id', 'title']