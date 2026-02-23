from rest_framework import serializers
from .models import HrmsUsers
from organizations.models import Organization,SubadminOrganization
from employees.models import Employees


class HrmsUserRegisterationSerializers(serializers.ModelSerializer):
    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = HrmsUsers
        fields = ['id','email', 'first_name', 'last_name',
                  'profile_image', 'password', 'password2','is_subadmin']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if first_name == None:
            raise serializers.ValidationError("First name cannot be blank")
        if last_name == None:
            raise serializers.ValidationError("Last name cannot be blank")
        if password != password2:
            raise serializers.ValidationError(
                "Password and Confirm Password doesn't match")
        return data

    def create(self, validated_data):
        return HrmsUsers.objects.create_user(**validated_data)


class HrmsUsersSerializers(serializers.ModelSerializer):
    class Meta:
        model = HrmsUsers
        fields = ['id','email', 'first_name', 'last_name',
                  'is_active', 'status', 'profile_image','is_subadmin']


class HrmsUsersUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = HrmsUsers
        fields = ['first_name', 'last_name', 'profile_image']


class SubadminOrganizationSerializers(serializers.ModelSerializer):
    class Meta:
        model = SubadminOrganization
        fields = '__all__'


class AssignedOrganizationListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['user_id', 'name', 'tagline', 'vision', 'mission', 'logo']


class HrmsUserEmployeesRegisterationSerializers(serializers.ModelSerializer):
    password2 = serializers.CharField()

    class Meta:
        model = HrmsUsers
        fields = ['email', 'first_name', 'last_name', 'password', 'password2','is_subadmin']
        

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        if first_name == None:
            raise serializers.ValidationError("first name cannot be blank")
        if last_name == None:
            raise serializers.ValidationError("last name cannot be blank")
   
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password doesn't match")
        return data

    def create(self, validated_data):
        return HrmsUsers.objects.create_employees(**validated_data)


class EmployeesLoginSerializers(serializers.ModelSerializer):
    old_password = serializers.CharField(
        max_length=255, 
        style={'input-type':'password'}, 
        write_only=True
    )
    class Meta:
        model = HrmsUsers
        fields = ['old_password']


class EmployeesProfilePictureUpdateSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = Employees
        fields = ['profile_image']
        