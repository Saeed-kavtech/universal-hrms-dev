from rest_framework import serializers
from .models import *

class DegreeTypesViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = DegreeTypes
        fields = [
            'id',
            'title',
            'duration',
            'is_active'
        ]

class InstitutesViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = Institutes
        fields = [
            'id',
            'name',
            'short_form',
            'is_active'
        ]


class EmployeeEducationsViewsetSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    degree_type_title = serializers.SerializerMethodField()
    selected_institute_name = serializers.SerializerMethodField()
    class Meta:
        model = EmployeeEducations
        fields = [
            'id',
            'employee',
            'employee_name',
            'institutes',
            'selected_institute_name',
            'institute_name',
            'degree_type',
            'degree_type_title',
            'degree_title',
            'duration',
            'year_of_completion',
            'degree_certificate',
            'is_active'
        ]

    def get_employee_name(self, obj):
        try:
            if obj.employee is not None:
                return obj.employee.name
            return None
        except Exception as e:
            print(str(e))
            return None

    def get_degree_type_title(self, obj):
        try:
            if obj.degree_type is not None:
                return obj.degree_type.title
            return None
        except Exception as e:
            print(str(e))
            return None

    def get_selected_institute_name(self, obj):
        try:
            if obj.institutes is not None:
                return obj.institutes.name
            return None
        except Exception as e:
            print(str(e))
            return None