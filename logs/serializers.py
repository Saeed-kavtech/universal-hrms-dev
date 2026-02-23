from django.forms import ValidationError
from rest_framework import serializers
from .models import *

class UserLoginLogsSerializers(serializers.ModelSerializer):
	class Meta:
		model = UserLoginLogs
		fields = ['user', 'organization', 'is_active']