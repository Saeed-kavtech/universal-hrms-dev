from rest_framework import serializers
from .models import *


class ProjectsViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = [
            'id',
            'uuid',
            'name',
            'code',
            'organization',
            'is_active'
        ]


class PreProjectDataViewSerializers(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = [
            'id',
            'name'
        ]
