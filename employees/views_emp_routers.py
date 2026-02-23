from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework import viewsets

from helpers.decode_token import decodeToken
from .serializers import *
from helpers.status_messages import *
from .models import *
from organizations.models import Organization


class ContactRelationsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ContactRelations.objects.filter(is_active=True)
    serializer_class = ContactRelationsViewsetSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if not ContactRelations.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'This Employee type does not exists', 'system_status_message': ''})

            obj = ContactRelations.objects.get(id=pk)
            if obj.is_active == False:
                msg = "This Employee Type is already deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
            obj.is_active = False
            obj.save()
            serializer = ContactRelationsViewsetSerializers(obj)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Deactivated Successfully', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)



class EmployeeTypesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EmployeeTypes.objects.filter(is_active=True)
    serializer_class = EmployeeTypesViewsetSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if not EmployeeTypes.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'This Employee type does not exists', 'system_status_message': ''})

            obj = EmployeeTypes.objects.get(id=pk)
            if obj.is_active == False:
                msg = "This Employee Type is already deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
            obj.is_active = False
            obj.save()
            serializer = EmployeeTypesViewsetSerializers(obj)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Deactivated Successfully', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)



class AttachmentTypesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = AttachmentTypes.objects.filter(is_active=True)
    serializer_class = AttachmentTypesViewsetSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if not AttachmentTypes.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'This Attachment type does not exists', 'system_status_message': ''})

            obj = AttachmentTypes.objects.get(id=pk)
            if obj.is_active == False:
                msg = "This Attachment Type is already deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
            obj.is_active = False
            obj.save()
            serializer = AttachmentTypesViewsetSerializers(obj)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Deactivated Successfully', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)

