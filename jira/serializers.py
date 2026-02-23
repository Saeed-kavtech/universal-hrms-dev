from rest_framework import serializers
from .models import JiraTokens


class JiraTokensViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = JiraTokens
        fields = [
            'id',
            'organization',
            'access_token',
            'expires_in',
            'refresh_token',
            'scope',
            'token_type',
            'is_active'
        ]