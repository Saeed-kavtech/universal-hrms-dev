from .models import JdDescriptions, JdTypes, JdDimensions, JdSpecifications
from departments.models import Departments
from rest_framework import serializers


class JdTypesSerializers(serializers.ModelSerializer):
    class Meta:
        model = JdTypes
        fields = ['id', 'title', 'level' ,'is_active']

class JdSpecificationsSerializers(serializers.ModelSerializer):
    jd_dimension_title = serializers.SerializerMethodField()
    class Meta:
        model = JdSpecifications
        fields = ['jd', 'jd_dimension', 'jd_dimension_title', 'essential', 'desirable']
        # exclude = ['updated_at']

    def get_jd_dimension_title(self, obj):
        return obj.jd_dimension.title

class JdDimensionsSerializers(serializers.ModelSerializer):
    class Meta:
        model = JdDimensions
        fields = ['id', 'title', 'level', 'jd_type', 'is_active']

        ordering = ['level']

class JdDescriptionsSerializers(serializers.ModelSerializer):
    jd_specifications = JdSpecificationsSerializers(many=True)
    grouphead = serializers.SerializerMethodField()
    grouphead_title = serializers.SerializerMethodField()
    department_title = serializers.SerializerMethodField()
    staff_classification_title = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    class Meta:
        model = JdDescriptions
        fields = ['id', 'grouphead', 'grouphead_title', 'department', 'project', 'department_title', 'staff_classification', 'staff_classification_title', 'position', 'position_title', 'title', 'code', 'main_responsibilities', 'is_active', 'created_at', 'jd_specifications']

    def get_grouphead(self, obj):

    	return obj.department.grouphead.id

    def get_grouphead_title(self, obj):
        return obj.department.grouphead.title

    def get_department_title(self, obj):

        return obj.department.title

    def get_staff_classification_title(self, obj):
        return obj.staff_classification.title

    def get_position_title(self, obj):
        return obj.position.title


class CreateJdDescriptionsSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = JdDescriptions
        fields = ['department', 'staff_classification', 'position', 'project', 'title', 'code', 'main_responsibilities', 'is_active', 'created_at']