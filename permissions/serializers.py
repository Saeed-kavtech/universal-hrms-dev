from rest_framework import serializers
from .models import AppPermissions
from django.contrib.contenttypes.models import ContentType

class AppPermissionsViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = AppPermissions
        fields = [
                'id',
                'role',
                'content_type',
                'can_view',
                'can_update',
                'can_add',
                'can_delete',
                'is_active',          
            ]


class ContentTypeSerializers(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = '__all__'

