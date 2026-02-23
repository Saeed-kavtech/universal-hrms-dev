from django.forms import ValidationError
from rest_framework import serializers
from .models import Organization, OrganizationApikeys, OrganizationLocation, OrganizationModuleAccess, StaffClassification, ProcedureTypes, ThirdPartyTokens

class OrganizationSerializers(serializers.ModelSerializer):
    
    # user_id = serializers.ReadOnlyField(source='user.id')
    logo = serializers.ImageField(required=False)
    class Meta:
        model = Organization
        fields = ['user', 'created_by', 'name', 'tagline', 'vision', 'mission', 'logo', 'established_date', 'organization_type']
        # fields = '__all__'
    # def validate(self, data):
    #     if data['is_active'] is None or data['is_active']=='':
    #         data['is_active'] = True
    #     return data

        
    
class OrganizationLocationSerializers(serializers.ModelSerializer):
    class Meta:
        model = OrganizationLocation
        fields =  '__all__'

    def validate(self, data):
        longitute = data['longitute'] 
        latitute= data['latitute'] 
        if longitute is not None:
            if longitute < -180.00 or longitute > 180.00:
                raise ValidationError('Longitute Value should be in these ranges: -180 till 180')
        if latitute is not None:
            if latitute < -90.00 or latitute > 90.00:
                raise ValidationError('Latitute must be in these ranges: -90 till 90')
        
        return data

class OrganizationAndLocationSerializers(serializers.ModelSerializer):
    locations = OrganizationLocationSerializers(many=True) 
    logo = serializers.ImageField(required=False)

    def create(self, validated_data):       
        validated_data.pop("city_name")
        return validated_data


    class Meta:
        model = Organization
        fields = '__all__' 


class StaffClassificationSerializers(serializers.ModelSerializer):
    class Meta:
        model = StaffClassification
        fields = '__all__'

class StaffClassificationOrgSerializers(serializers.ModelSerializer):
    class Meta:
        model = StaffClassification
        fields = ['id', 'title']

class UpdateOrganizationSerializers(serializers.ModelSerializer):
    
    # user_id = serializers.ReadOnlyField(source='user.id')
    logo = serializers.ImageField(required=False)
    class Meta:
        model = Organization
        fields = ['created_by', 'name', 'tagline', 'vision', 'mission', 'logo', 'established_date', 'organization_type', 'is_active']


class ProcedureTypesSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProcedureTypes
        fields = ['id', 'title', 'organization', 'is_active']


class OrganizationApikeysSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationApikeys
        fields = '__all__'


class ThirdPartyTokensSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThirdPartyTokens
        fields = '__all__'


class OrganizationModuleAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationModuleAccess
        fields = [
            'id',
            'organization',
            'title',
            'level',
            'is_allowed',
            'is_default',
            'created_by',
            'is_active',
            'created_at',
            'updated_at'
        ]