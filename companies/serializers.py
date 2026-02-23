from rest_framework import serializers
from .models import *

class CompaniesViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = Companies
        fields = [
            'id',
            'name',
            'company_type',
            'established_date',
            'vision',
            'mission',
            'is_active'
        ]

class EmployeeWorkExperienceViewsetSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    choosen_company_name = serializers.SerializerMethodField()
    class Meta:
        model = EmployeeWorkExperience
        fields = [
            'id',
            'employee',
            'employee_name',
            'company',
            'choosen_company_name',
            'company_name',
            'designation',
            'joining_date',
            'leaving_date',
            'leaving_reason',
            'is_currently_employed',
            'experience_letter',
            'is_active'
        ]

    def get_choosen_company_name(self, obj):
        if obj.company is not None:
            return obj.company.name
        else:
            return None

    def get_employee_name(self, obj):
        if obj.employee is not None:
            return obj.employee.name
        return None