from rest_framework import serializers
from .models import SkillTypes, KavskillsEnrollmentForm

class SkillTypesSerializers(serializers.ModelSerializer):
    class Meta:
        model = SkillTypes
        fields = [
            'id',
            'title',
            'cost',
            'course_details',
            'organization',
            'is_active',
        ]

class SkillTypesPreDataSerializers(serializers.ModelSerializer):
    class Meta:
        model = SkillTypes
        fields = [
            'id',
            'title',
            'cost',
        ]

class KavskillsEnrollmentFormSerializers(serializers.ModelSerializer):
    skill_type_title = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    class Meta:
        model = KavskillsEnrollmentForm
        fields = [
            'id',
            'skill_type',
            'skill_type_title',
            'cost',
            'email',
            'full_name',
            'contact_number',
            'educational_qualifications',
            'university_name',
            'cnic_no',
            'major',
            'kav_skills_resume',
            'cover_letter',
            'joining_reason',
            'objectives',
            'financial_aid',
            'financial_aid_reason',
            'additional_information',
            'created_at',
            'remark',
            'lnd_remark',
            'category',
            'conversion_status',
            'is_active',
        ]

    def get_skill_type_title(self, obj):
        try:
            return obj.skill_type.title
        except Exception as e:
            print(str(e))
            return None
    
    def get_cost(self, obj):
        try:
            return obj.skill_type.cost
        except Exception as e:
            print(str(e))
            return None

        