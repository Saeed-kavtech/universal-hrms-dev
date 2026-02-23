from rest_framework import viewsets
from helpers.custom_permissions import IsAuthenticated
from helpers.status_messages import exception, success, serializerError, errorMessage, successMessage
from helpers.decode_token import decodeToken
from .models import JiraTokens
from .serializers import JiraTokensViewsetSerializers


# Create your views here.
class JiraTokensViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):   
        try:
            organization_id = decodeToken(self, request)['organization_id']
            obj = JiraTokens.objects.filter(is_active=True) # organization=organization_id, 
            serializer = JiraTokensViewsetSerializers(obj, many=True)
            return success(serializer.data)
            # return errorMessage('Jira does not work on dev instance')
        except Exception as e:
            return exception(e)  

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            request.data['organization'] = organization_id
            # print("test",request.data)
            serializer = JiraTokensViewsetSerializers(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)          
            
            tokens = JiraTokens.objects.filter(is_active=True) # organization=organization_id
            for token in tokens:
                token.is_active=False
                token.save()

            serializer.save()
            return success(serializer.data)    
            # return errorMessage('Jira does not work on dev instance')
        except Exception as e:
            return exception(e)
    
    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            tokens = JiraTokens.objects.filter(id=pk) 
            if not tokens.exists():
                return errorMessage('No token exists at this id')
            elif not tokens.filter(is_active=True):
                return errorMessage('Token is deactivated at this id')

            token = tokens.get()
            token.is_active = False
            token.save()
        
            return successMessage('Token is deactivated successfully')
            # return errorMessage('Jira does not work on dev instance')
        except Exception as e:
            return exception(e)   
         