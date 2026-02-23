from rest_framework import serializers
from .models import GroupHeads, Departments


class GroupHeadsSerializers(serializers.ModelSerializer):
    class Meta:
        model = GroupHeads
        fields = [
            'id', 
            'organization',
            'title',
            'grouphead_type', 
            'description',
            'created_by', 
            'is_active', 
        ] 

class UpdateGroupHeadsSerializers(serializers.ModelSerializer):
    class Meta:
        model = GroupHeads
        fields = [
            'id',
            'title',
            'grouphead_type', 
            'description',
            'created_by', 
            'is_active', 
        ] 

class DepartmentsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = [
            'id',
            'grouphead',
            'title',
            'description',
            'status',
            'created_by',
            'is_active'
        ]


class GroupHeadsOrgSerializer(serializers.ModelSerializer):
	class Meta:
		model = GroupHeads
		fields = [
                    'id', 
                    'title', 
                    'grouphead_type'
                ]


class DepartmentsOrgSerializer(serializers.ModelSerializer):
	class Meta:
		model = Departments
		fields = [
                    'id', 
                    'grouphead', 
                    'title'
                ]
                