from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .serializers import SubjectTypesViewsetSerializers
from helpers.status_messages import exception
from .models import SubjectTypes


class SubjectTypesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = SubjectTypes.objects.filter(is_active=True)
    serializer_class = SubjectTypesViewsetSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if not SubjectTypes.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This Subject type does not exists', 'system_status_message': ''})

            obj = SubjectTypes.objects.get(id=pk)
            if obj.is_active == False:
                msg = "This Subject Type is already deactivated"
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': msg, 'system_status_message': ''})
            obj.is_active = False
            obj.save()
            serializer = SubjectTypesViewsetSerializers(obj)
            return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': serializer.data, 'message': 'Deactivated Successfully', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)