from .models import *
from rest_framework import serializers


class RoleTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleTypes
        fields = [
            'id',
            'title',
            'organization',
            'level',
            'is_active'
        ]



class RolesSerializers(serializers.ModelSerializer):
    role_type_title = serializers.SerializerMethodField()
    class Meta:
        model = Roles
        fields = [
            'id',  
			'uuid', 
			'role_type', 
			'role_type_title',
			'title', 
			'code', 
			'organization', 
			'user', 
			'description', 
			'is_active'
        ]

  

    def get_role_type_title(self, obj):
        try:
            return obj.role_type.title
        except Exception as e:
        	return None


class PreDataRolesSerializers(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = [
			'id', 
			'title'
		]
