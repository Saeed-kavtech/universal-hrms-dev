from django.forms import ValidationError
from rest_framework import serializers

from organizations.models import OrganizationModuleAccess
from .models import HrmsUsers
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import Util
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class HrmsUserLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)
    class Meta:
        model = HrmsUsers
        fields = ['email', 'password']

class HrmsUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HrmsUsers
        fields = ['id', 'email', 'first_name', 'last_name', 'is_privileged','is_admin', 'is_employee', 'profile_image','is_subadmin']


class HrmsUserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, 
        style={'input-type':'password'}, 
        write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, 
        style={'input-type':'password2'}, 
        write_only=True
    )
    class Meta:
        fields = ['password', 'password2']
    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('hrms_user')
        if len(password) < 8:
            raise serializers.ValidationError("Password length must be 8 characters")
        
        has_capital_letter = False
        has_small_letter = False

        for char in password:
            if char.isupper():
                has_capital_letter = True
            elif char.islower():
                has_small_letter = True

        if not has_capital_letter:
            raise serializers.ValidationError("Capital letters are missing")
        if not has_small_letter:
            raise serializers.ValidationError("Small letters are missing")


        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password doesn't match")
        user.set_password(password)
        user.save()
        return attrs 


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if HrmsUsers.objects.filter(email=email).exists():
            user = HrmsUsers.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = 'http://178.128.85.114/reset-password/'+uid+'/'+token+'/'
            #send email
            body = 'Click the Following link to  Reset your Password ' + link
            data = {
                'subject': 'Reset your Password',
                'body':  body,
                'to_email': user.email,
            }
            Util.send_email(data)
            return attrs
        else:
            raise ValidationError('You are not a registered User')


class HrmsUserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, 
        style={'input-type':'password'}, 
        write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, 
        style={'input-type':'password'}, 
        write_only=True
    )
    class Meta:
        fields = ['password', 'password2']
    
    def validate(self, attrs):
        try:     
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')
            if len(password) < 8:
                raise serializers.ValidationError("Password length must be 8 characters")
            
            has_capital_letter = False
            has_small_letter = False

            for char in password:
                if char.isupper():
                    has_capital_letter = True
                elif char.islower():
                    has_small_letter = True

            if not has_capital_letter:
                raise serializers.ValidationError("Capital letters are missing")
            if not has_small_letter:
                raise serializers.ValidationError("Small letters are missing")

            if password != password2:
                raise serializers.ValidationError("Password and Confirm Password doesn't match")
            id = smart_str(urlsafe_base64_decode(uid))
            user = HrmsUsers.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise ValidationError('Token is not Valid or Expired')
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError:
            PasswordResetTokenGenerator().check_token(user, token)
            raise ValidationError('Token is not valid or Expired')


class HrmsUserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    def validate(self, attrs):
        try:
            self.token = attrs['refresh']
            return attrs     
        except TokenError:
            raise Exception("Not valid token")

    def save(self, **kwargs):
        RefreshToken(self.token).blacklist()

class HrmsUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = HrmsUsers
        fields = ['first_name', 'last_name', 'profile_image']

        
class HrmsUserLoginSerializers(serializers.ModelSerializer):
    class Meta:
        model = HrmsUsers
        fields = '__all__'
    
   
        
class LoginOrganizationModuleAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationModuleAccess
        fields = [
            'id',
            'title',
            'level',
            'is_allowed',
            'is_default'
        ]
