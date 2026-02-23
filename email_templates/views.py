from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from helpers.renderers import Renderer
from rest_framework.response import Response
from .models import *
from organizations.models import Organization
from rest_framework import viewsets
from .serializers import *

from helpers.status_messages import *
from helpers.custom_permissions import *

from logs.views import UserLoginLogsViewset

class TemplateVariablesViewset(viewsets.ModelViewSet):
    queryset = TemplateVariables.objects.filter(is_active=True)
    serializer_class = TemplateVariablesSerializers
    permission_classes = [IsAuthenticated]

    def list(self, request):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            obj = TemplateVariables.objects.filter(is_active=True, organization=user_organization.id)
            serializer = TemplateVariablesSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            request.data['organization'] = user_organization.id
            is_exist = self.checkVariableCode(request.data.get('code'), user_organization.id, None)
            if is_exist:
                return Response({'status':400, 'message':'Code is already exists', 'system_status_message':'', 'system_status':400})
            serializer = TemplateVariablesSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return successfullyCreated(serializer.data)
            else:
                return serializerError(serializer.errors)
        except Exception as e:
            return exception(e)

    def partial_update(self, request, pk):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            if TemplateVariables.objects.filter(pk=pk, organization=user_organization.id).exists():
                
                if 'code' in request.data:
                    is_exist = self.checkVariableCode(request.data.get('code'), user_organization.id, pk)
                    if is_exist:
                        return Response({'status':400, 'message':'Code is already exists', 'system_status_message':'', 'system_status':400})

                obj = TemplateVariables.objects.get(pk=pk)
                serializer = TemplateVariablesSerializers(obj, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return successfullyUpdated(serializer.data)
                else:
                    return serializerError(serializer.errors)
            else:
                return nonexistent(var='Template variable')
        except Exception as e:
            return exception(e)

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if TemplateVariables.objects.filter(id=pk).exists():
                obj = TemplateVariables.objects.get(id=pk)
                if obj.is_active == False:
                    msg = "Template Variables is already deactivated"
                    return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
                obj.is_active = False
                obj.save()
                serializer = TemplateVariablesSerializers(obj)
                return success(serializer.data)
            else:
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This Template variable does not exists', 'system_status_message': ''})
        except Exception as e:
            return exception(e)

    def checkVariableCode(self, code, organization_id, variable_id):
        try:
            if variable_id is not None:
                variable = TemplateVariables.objects.filter(code=code, organization=organization_id).exclude(pk=variable_id)
            else:
                variable = TemplateVariables.objects.filter(code=code, organization=organization_id)
            if variable.exists():
                return True
            else:
                return None
        except Exception as e:
            return False


class EmailTemplatesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            obj = EmailTemplates.objects.filter(organization=user_organization)
            serializer = EmailTemplatesSerializers(obj, many=True)
            return success(serializer.data)

        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            request.data['organization'] = user_organization.id 
            request.data['user'] = request.user.id

            serializer = EmailTemplatesSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return successfullyCreated(serializer.data)
            else:
                return serializerError(serializer.errors)

        except Exception as e:
            return exception(e)

    def get(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            uuid = self.kwargs['uuid']
            if EmailTemplates.objects.filter(uuid=uuid, organization=user_organization).exists():
                obj = EmailTemplates.objects.get(uuid=uuid)
                serializer = EmailTemplatesSerializers(obj, many=False)
                return success(serializer.data)
            else:
                return errorMessage("This does not belong to this organization or inactive.")
        except Exception as e:
            return exception(e)

    def partial_update(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            uuid = self.kwargs['uuid']
            if EmailTemplates.objects.filter(uuid=uuid, organization=user_organization).exists():
                obj = EmailTemplates.objects.get(uuid=uuid)
                serializer = EmailTemplatesSerializers(obj, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return successfullyUpdated(serializer.data)
                else:
                    return serializerError(serializer.errors)
        except Exception as e:
            return exception(e)

    def destroy(self, request, *args, **kwargs):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            uuid = self.kwargs['uuid']
            if EmailTemplates.objects.filter(uuid=uuid, organization=user_organization).exists():
                obj = EmailTemplates.objects.get(uuid=uuid)
                obj.is_active=False
                obj.save()
                serializer = EmailTemplatesSerializers(obj, many=False)
                return success(serializer.data)
        except Exception as e:
            return exception(e)


class PreDataEmailTemplatesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def pre_data(self, organization_id):
        try:
            data = EmailTemplates.objects.filter(is_active=True, organization=organization_id)
            serializer = PreDataEmailTemplatesSerializers(data, many=True)
            return serializer.data
        except Exception as e:
            return []
        
class EmailRecipientsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsAdminOnly]
    queryset = EmailRecipients.objects.all() 
    serializer_class = EmailRecipientsSerializer
    

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            # print(request.data)
           
            # print(organization_id)
            required_fields = ['level', 'title','employee']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all the required fields','level,title,employee')
            
            employee=request.data['employee']
            level = request.data['level']
            title = request.data['title']

            employee_query=Employees.objects.filter(id=employee,organization=organization_id,is_active=True)
            if not employee_query.exists():
                errorMessage("Employee dose not exists")

            # print(employee_query.values())

            query=EmailRecipients.objects.filter(employee__organization=organization_id,is_active=True)
            if query.exists():
                if query.filter(level=level).exists():
                    return errorMessage("Same level already assing to another title")
                
                if query.filter(title=title).exists():
                    return errorMessage("Same title already assing to another level")
            
           
            request.data['created_by'] = request.user.id
            
            serializer=self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)
            
        except Exception as e:
            return exception(e)
        
 