from rest_framework import serializers
from .models import *

from rest_framework import serializers
from .models import *



class ProficiencyLevelsViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProficiencyLevels
        fields = [
            'id',
            'title',
            'level',
            'is_active'
        ]


class SkillCategoriesViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = SkillCategories
        fields = [
            'id',
            'title',
            'is_active'
        ]


class SkillsViewsetSerializers(serializers.ModelSerializer):
    category_title = serializers.SerializerMethodField()
    class Meta:
        model = Skills
        fields = [
            'id',
            'category',
            'category_title',
            'title',
            'is_active'
        ]

    def get_category_title(self, obj):
        try:
            if obj.category is not None:
                return obj.category.title
            return None
        except Exception as e:
            print(str(e))
            return None



class EmployeeSkillsViewsetSerializers(serializers.ModelSerializer):
    skill_title = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    category_title = serializers.SerializerMethodField()
    employee_name =  serializers.SerializerMethodField()
    proficiency_level_title =  serializers.SerializerMethodField()
       
    class Meta:
        model = EmployeeSkills
        fields = [
            'id',
            'employee',
            'employee_name',
            'category',
            'category_title',
            'skill',
            'skill_title',
            'proficiency_level',
            'proficiency_level_title',
            'comment',
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

    def get_category(self, obj):
        try:
            if obj.skill is not None:
                return obj.skill.category.id
            return None
        except Exception as e:
            print(str(e))
            return None  

    def get_category_title(self, obj):
        try:
            if obj.skill is not None:
                return obj.skill.category.title
            return None
        except Exception as e:
            print(str(e))
            return None
    
    def get_skill_title(self, obj):
        try:
            if obj.skill is not None:
                return obj.skill.title
            return None
        except Exception as e:
            print(str(e))
            return None

    def get_proficiency_level_title(self, obj):
        try:
            if obj.proficiency_level is not None:
                return obj.proficiency_level.title
            return None
        except Exception as e:
            print(str(e))
            return None