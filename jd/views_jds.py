from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import *
from rest_framework import viewsets
from .serializers import *
from helpers.status_messages import *


class JdTypesViewset(viewsets.ModelViewSet):
    queryset = JdTypes.objects.filter(is_active=True).order_by('level')
    serializer_class = JdTypesSerializers


    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if JdTypes.objects.filter(id=pk).exists():
                obj = JdTypes.objects.get(id=pk)
                if obj.is_active == False:
                    msg = "Job Description Type is already deactivated"
                    return Response({'status':200, 'message':msg})
                obj.is_active = False
                obj.save()
                serializer = JdTypesSerializers(obj)
                return Response({'status':200, 'data': serializer.data, 'message': 'Deleted Successfully'})
            else:
                return Response({'status':404, 'message': 'This Job Description type does not exists'})
        except Exception as e:
            return exception(e)


class JdDimensionsViewset(viewsets.ModelViewSet):
    queryset = JdDimensions.objects.filter(is_active=True).order_by('jd_type', 'level')
    serializer_class = JdDimensionsSerializers
   
    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if JdDimensions.objects.filter(id=pk).exists():
                obj = JdDimensions.objects.get(id=pk)
                if obj.is_active == False:
                    msg = "Job Dimension is already deactivated"
                    return Response({'status':200, 'message':msg})
                obj.is_active = False
                obj.save()
                serializer = JdDimensionsSerializers(obj)
                return Response({'status':200, 'data': serializer.data, 'message': 'Deleted Successfully'})
            else:
                return Response({'status':404, 'message': 'This Job Dimension does not exists'})
        except Exception as e:
            return exception(e)
