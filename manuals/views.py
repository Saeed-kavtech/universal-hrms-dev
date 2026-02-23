from rest_framework import viewsets
from helpers.decode_token import decodeToken
from helpers.custom_permissions import IsAuthenticated, IsAdminOnly,IsEmployeeOnly
from helpers.status_messages import ( 
    exception, errorMessage, serializerError, successMessageWithData,
    success, successMessage, successfullyCreated, 
)
from .models import ManualTypes, Manuals
from .serializers import (
    ManualTypesSerializers, ManualsSerializers, UpdateManualsSerializers, ManualPreDataSerializers
)


class ManualTypesViewsets(viewsets.ModelViewSet):
    queryset = ManualTypes.objects.all()
    serializer_class = ManualTypesSerializers
    permission_classes = [IsAuthenticated]
    
    # def get_permissions(self):
    #     # Apply IsAuthenticated permission for all actions
    #     permission_classes = [IsAuthenticated]

    #     # Apply IsAdminOnly permission for create and destroy actions
    #     if self.action in ['list','create', 'destroy']:
    #         permission_classes.append(IsAdminOnly)

    #     # Apply IsEmployeeOnly permission for the list action
    #     elif self.action == 'list':
    #         permission_classes.append(IsEmployeeOnly)

    #     return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            # print("Test")
            queryset = self.queryset.filter(organization=organization_id, is_active=True)
            serializer = self.get_serializer(queryset, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            request.data['created_by'] = request.user.id
            request.data['organization'] = organization_id
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return exception(e)      

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            organization_id = decodeToken(request, self.request)['organization_id']
            queryset = self.queryset.filter(organization=organization_id, is_active=True)
            query = queryset.filter(id=pk)
            if not query.exists():
                return errorMessage('No manual exists at this id')
            if not query.filter(is_active=True):
                return errorMessage('Manual is deactivated at this id')
            
            obj = query.get()
            if Manuals.objects.filter(manual_type=obj.id, is_active=True).exists():
                return errorMessage('Data exists against this manual type')
            
            obj.is_active = False
            obj.save()
            return successMessage('Sucessfully deactivated')
        except Exception as e:
            return exception(e) 
    

class ManualsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOnly|IsEmployeeOnly]
    queryset = Manuals.objects.all()
    serializer_class = ManualsSerializers
    
    def get_queryset(self):
        try:
            
            organization_id = decodeToken(self, self.request)['organization_id']
            return self.queryset.filter(manual_type__organization=organization_id)
        except Exception as e:
            return None

    def list(self, request, *args, **kwargs):
        try:
           
            query = self.get_queryset().filter(is_active=True)
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            
            pk = self.kwargs['pk']
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('Does not exists')
            elif not query.filter(is_active=True).exists():
                return errorMessage('Deactivated at this id')

            obj = query.get()
            serializer = self.serializer_class(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, request)['organization_id']
            if request.data:
                request.data._mutable = True
            required_fields = ['manual_type', 'title', 'document']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [manual_type, title, document]')

            request.data['created_by'] = request.user.id
            request.data['is_active'] = True
            manual_type_id = request.data['manual_type']
            manual_type = ManualTypes.objects.filter(
                id=manual_type_id, 
                organization=organization_id,
                is_active=True
            )
            if not manual_type.exists():
                return errorMessage('Manual Type does not exists')
            
            title = request.data['title']
            query = Manuals.objects.filter(
                manual_type=manual_type_id,
                title__iexact = title,
                is_active=True
            )
            if query.exists():
                return errorMessage('title is not unique')
            
            serializer = self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            # print(serializer)
            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)          
        

    def patch(self, request, *args, **kwargs):
        try:
            
            pk = self.kwargs['pk']
            if request.data:
                request.data._mutable = True
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('No Manual exists at this id')
            obj = query.get()

            if 'title' in request.data:
                title = request.data['title']
                query = Manuals.objects.filter(
                    manual_type=obj.manual_type,
                    title__iexact = title,
                    is_active=True
                )
                if query.exists():
                    return errorMessage('title is not unique')

            serializer = UpdateManualsSerializers(obj, data = request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
                     
            return successMessageWithData('Success', serializer.data)
        except Exception as e:
            return exception(e)
        
    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('No manual exists at this id')
            if not query.filter(is_active=True):
                return errorMessage('Manual is deactivated at this id')
            
            obj = query.get()
            obj.is_active = False
            obj.save()
            return successMessage('Sucessfully deactivated')
        except Exception as e:
            return exception(e)


class ManualPreDataViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOnly]
    queryset = ManualTypes.objects.all()
    serializer_class = ManualPreDataSerializers

    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            query = self.queryset.filter(organization=organization_id, is_active=True)
            serializer = self.serializer_class(query, many=True)
            return serializer.data
        except Exception as e:
            return exception(e)