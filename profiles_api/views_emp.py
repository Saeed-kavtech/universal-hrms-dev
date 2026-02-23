from rest_framework import viewsets
from helpers.status_messages import (
    exception, errorMessage, serializerError, successMessage, successMessageWithData
)
from helpers.decode_token import decodeToken
from helpers.custom_permissions import IsAuthenticated, IsEmployeeOnly
from employees.models import Employees
from .serializers_users import EmployeesProfilePictureUpdateSerializers
from .serializers import HrmsUserChangePasswordSerializer, SendPasswordResetEmailSerializer, HrmsUserPasswordResetSerializer


class HrmsUserProfileUpdatesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated] # , IsEmployeeOnly

    def create(self, request, *args, **kwargs):
        try:
            # token_data = decodeToken(self, self.request)
            # organization_id = token_data['organization_id']
            # employee_id = token_data['employee_id']

            # required_fields = ['old_password', 'password', 'password2']
            # if not all(field in request.data for field in required_fields):
            #     return errorMessage('make sure you have added all the required fields: [old_password, password, password2]')
       
            # serializer = EmployeesLoginSerializers(data=request.data)
            # if serializer.is_valid():
            #     return serializerError(serializer.errors)
            
            # old_password = serializer.data.get('old_password')
            # emp = Employees.objects.get(employee_id=employee_id, organization=organization_id)

            # user = authenticate(email=emp.official_email, password=old_password)

            serializer = HrmsUserChangePasswordSerializer(data=request.data, context={'hrms_user':request.user})
            if serializer.is_valid():
                return successMessage('Password changed successfully')
            else:
                return serializerError(serializer.errors)

        except Exception as e:
            return exception(e)
        

    def profile_update(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            employee_id = token_data['employee_id']

            if not employee_id:
                return errorMessage('User is not an employee')
            
            if 'profile_image' not in request.data:
                return errorMessage('You have not added the profile_image')
                        
            request.data._mutable = True

            emp = Employees.objects.get(id=employee_id)
            serializer = EmployeesProfilePictureUpdateSerializers(emp, data = request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()
            return successMessageWithData('Profile Image is successfully updated', serializer.data)
        except Exception as e:
            return exception(e)   
        
class ResetPassword(viewsets.ModelViewSet):
    def post_send_password_email(self, request, *args, **kwargs):
        try:         
            serializer = SendPasswordResetEmailSerializer(data = request.data)
            if serializer.is_valid():
                return successMessage('Password Reset link send. Please check your email')
            else:
                errors = serializer.errors.copy()
                if 'non_field_errors' in errors:
                    non_field_errors = errors.pop('non_field_errors')
                    error_message = non_field_errors[0]
                else:
                    first_field_errors = next(iter(errors.values()))
                    error_message = first_field_errors[0]

                return errorMessage(error_message)        
        except Exception as e:
            return exception(e)   
        
    def post_reset_password(self, request, *args, **kwargs):
        try:
            uid = self.kwargs['uid']
            token = self.kwargs['token']
            serializer = HrmsUserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
            if serializer.is_valid():
                return successMessage('password is reset successfully')
            else:
                errors = serializer.errors.copy()
                if 'non_field_errors' in errors:
                    non_field_errors = errors.pop('non_field_errors')
                    error_message = non_field_errors[0]
                else:
                    first_field_errors = next(iter(errors.values()))
                    error_message = first_field_errors[0]

                return errorMessage(error_message) 
        except Exception as e:
            return exception(e)