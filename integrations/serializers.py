from rest_framework import serializers
from .models import MailsCredentials

class MailsCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailsCredentials
        fields = '__all__'  # Include all fields from the model