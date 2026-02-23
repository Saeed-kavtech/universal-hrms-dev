from rest_framework import serializers
from .models import Positions


class PositionsSerializers(serializers.ModelSerializer):
    grouphead_title = serializers.SerializerMethodField()
    department_title = serializers.SerializerMethodField()
    staff_classification_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Positions
        fields = [
            'id',
            'grouphead',
            'grouphead_title',
            'department',
            'department_title',
            'staff_classification',
            'staff_classification_title',
            'title',
            'code',
            'code_number',
            'qualification',
            'years_of_experience',
            'min_salary',
            'max_salary',
            'is_active'
        ]

    def get_grouphead_title(self, obj):
        try:
            return obj.grouphead.title
        except Exception as e:
            print(str(e))
            return None


    def get_department_title(self, obj):
        try:
            return obj.department.title
        except Exception as e:
            print(str(e))
            return None


    def get_staff_classification_title(self, obj):
        try:
            return obj.staff_classification.title
        except Exception as e:
            print(str(e))
            return None
        

class PositionsOrgSerializers(serializers.ModelSerializer):
    class Meta:
        model = Positions
        fields = ['id', 'grouphead', 'department', 'staff_classification', 'title']