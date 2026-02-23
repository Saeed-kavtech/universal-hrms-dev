from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from helpers.status_messages import success, serializerError, errorMessage, exception, nonexistent, successfullyCreated, successfullyUpdated, successfullyDeleted
from departments.models import GroupHeads, Departments
from .serializers import GroupHeadsSerializers, UpdateGroupHeadsSerializers, DepartmentsSerializers
from positions.models import Positions
from helpers.custom_permissions import TokenDataPermissions



class GroupHeadsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, TokenDataPermissions]
    queryset = GroupHeads.objects.all()

    def get_queryset(self):
        organization_id = self.request.data.get('current_organization')
        return self.queryset.filter(organization=organization_id)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset().filter(is_active=True).order_by('title')
            serializer = GroupHeadsSerializers(queryset, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            grouphead_id = self.kwargs['pk']
            
            grouphead_query = self.get_queryset().filter(id=grouphead_id)
            if not grouphead_query.exists():
                return nonexistent(var = 'Grouphead')
            if grouphead_query.filter(is_active=False):
                return errorMessage("Grouphead does not exists")
            
            obj = grouphead_query.get()
            serializer = GroupHeadsSerializers(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request):
        try:
            organization_id = request.data.get('current_organization')
            user_id = request.user.id
            request.data['created_by'] = user_id
            request.data['organization'] = organization_id
            serializer = GroupHeadsSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return successfullyCreated(serializer.data)
            else:
                return serializerError(serializer.errors)
        except Exception as e:
            return exception(e)

    def patch(self, request, *args, **kwargs):
        try:
            grouphead_id = self.kwargs['pk']
    
            grouphead_query = self.get_queryset().filter(id=grouphead_id)
            if not grouphead_query.exists():
                return nonexistent(var = 'Grouphead')
            
            obj = grouphead_query.get()
            
            serializer = UpdateGroupHeadsSerializers(obj, data=request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)

    def delete(self, request, *args, **kwargs):
        try:
            grouphead_id = self.kwargs['pk']
            grouphead_query = self.get_queryset().filter(id=grouphead_id)

            if not grouphead_query.exists():
                return nonexistent(var = 'Organization')
            
            obj = grouphead_query.get()
            if Departments.objects.filter(grouphead=grouphead_id, is_active=True).exists():
                return errorMessage("Have active departments.")
            if Positions.objects.filter(grouphead=grouphead_id, is_active=True).exists():
                return errorMessage("Positions exists against this grouphead")
            
            if obj.is_active == False:
                return errorMessage('Grouphead is already deactivated')
            obj.is_active = False
            obj.save()
            serializer = GroupHeadsSerializers(obj)
            return successfullyDeleted(serializer.data)    
        except Exception as e:
            return exception(e)


# organization Department Logic
class DepartmentsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, TokenDataPermissions]
    queryset = Departments.objects.all()

    def get_queryset(self):
        organization_id = self.request.data.get('current_organization')
        return self.queryset.filter(grouphead__organization=organization_id)


    def list(self, request, *args, **kwargs):
        try:
            query = self.get_queryset().filter(is_active=True).order_by('-id')
            serializer = DepartmentsSerializers(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def pre_data(self,organization_id):
        try:
            queryset = Departments.objects.filter(grouphead__organization=organization_id,is_active=True).order_by('-id')
            query=queryset.values("id","title")
            return query
        except Exception as e:
            return exception(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            department_id = self.kwargs['pk']
            query = self.get_queryset().filter(id=department_id)
            if not query.exists():
                return nonexistent(var = 'Department')
            obj = query.get()
            if obj.is_active == False:
                return errorMessage("Change the status of the department to active first")
                
            serializer = DepartmentsSerializers(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            organization_id = self.request.data.get('current_organization')

            grouphead_id = request.data.get('grouphead', None)
            if grouphead_id == None:
                return errorMessage("Grouphead is a required field")
            
            grouphead_query = GroupHeads.objects.filter(id=grouphead_id, organization=organization_id)
            if not grouphead_query.exists():
                return errorMessage("Grouphead does not exists")
            elif grouphead_query.filter(is_active=False).exists():
                return errorMessage("Grouphead is deactivated at this id")

            user_id = request.user.id
            request.data['created_by'] = user_id
            serializer = DepartmentsSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return successfullyCreated(serializer.data)
            else:
                return serializerError(serializer.errors)
        except Exception as e:
            return exception(e)

    def patch(self, request, *args, **kwargs):
        try:
            department_id = self.kwargs['pk']
            query = self.get_queryset().filter(id=department_id)

            if not query.exists():
                return nonexistent(var = 'Department')
            
            obj = query.get()

            if 'grouphead' in request.data:
                organization_id = request.data.get('current_organization')
                grouphead_id = request.data['grouphead']

                grouphead_query = GroupHeads.objects.filter(id=grouphead_id, organization = organization_id)
                if not grouphead_query.exists():
                    return errorMessage('grouphead does not exists')
                elif not grouphead_query.filter(is_active=True):
                    return errorMessage('Grouphead is deactivated. Activate the grouphead first')

            serializer = DepartmentsSerializers(obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return successfullyUpdated(serializer.data)
            else:
                return serializerError(serializer.errors)  
        except Exception as e:
            return exception(e)

    def delete(self, request, *args, **kwargs):
        try:
            department_id = self.kwargs['pk']
            query = self.get_queryset().filter(id=department_id)

            if not query.exists():
                return nonexistent(var = 'Department')

            obj = query.get()
            if obj.is_active == False:
                return errorMessage("This Department is already deactivated") 
            obj.is_active = False
            obj.save()
            serializer = DepartmentsSerializers(obj, many=False)
            return successfullyDeleted(serializer.data) 
        except Exception as e:
            return exception(e)
