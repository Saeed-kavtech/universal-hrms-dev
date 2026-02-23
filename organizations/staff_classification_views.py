from rest_framework import viewsets
from helpers.custom_permissions import IsAuthenticated, DoesOrgExists
from organizations.models import StaffClassification
from .serializers import StaffClassificationSerializers
from helpers.status_messages import *
from positions.models import Positions
from employees.models import Employees
import uuid

# staff classification viewset
class StaffClassificationViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def list(self, request, *args, **kwargs):   
        try:
            user_organization = request.data.get('organization_profile')
            obj = StaffClassification.objects.filter(is_active=True, organization=user_organization.id).order_by('level')
            serializer = StaffClassificationSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)  
        

    def pre_data(self,organization_id):
        try:
            queryset = StaffClassification.objects.filter(organization=organization_id,is_active=True).order_by('-id')
            query=queryset.values("id","title")
            return query
        except Exception as e:
            return exception(e)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            user_organization = request.data.get('organization_profile')
            if StaffClassification.objects.filter(id=pk, organization=user_organization.id).exists(): 
                obj = StaffClassification.objects.get(id=pk)
                serializer = StaffClassificationSerializers(obj, many=False)
                return success(serializer.data)
            else:
                return nonexistent(var = 'Staff Classification')
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            request.data['organization']  = user_organization.id
            initial = request.data['initial']
            initial = initial.strip()
            request.data['initial'] = initial

            if StaffClassification.objects.filter(initial=initial, organization=user_organization.id, is_active=True).exists():
                return errorMessage("The initial already exists")

            serializer = StaffClassificationSerializers(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return success(serializer.data)
            else:
                return serializerError(serializer.errors)
        except Exception as e:
            return exception(e)
        
    
    def patch(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            user_organization = request.data.get('organization_profile')
        
            if StaffClassification.objects.filter(id=pk, organization=user_organization.id).exists(): 
                obj = StaffClassification.objects.get(id=pk)

                if 'initial' in request.data:
                    initial = request.data['initial']
                    if StaffClassification.objects.exclude(id=pk).filter(initial=initial, organization=user_organization.id, is_active=True).exists():
                        return errorMessage("This initial already exists. Kindly change them")                    
                
                serializer = StaffClassificationSerializers(obj, data = request.data, partial=True)
                request.data['organization'] = user_organization.id
                if serializer.is_valid():
                    serializer.save()
                    return successfullyUpdated(serializer.data)
                else:
                    return serializerError(serializer.errors)
            else:
                return errorMessage('Staff Classification does not exist at this index')
        except Exception as e:
            return exception(e)

    def initial_adjustment(self, request, *args, **kwargs):
        try:
            
            initial_adjustment = StaffClassification.objects.filter()
            for obj in initial_adjustment:
                initial = str(uuid.uuid4())[:4]
                obj.initial = initial
                obj.save()

             
            return successMessage("Successfully updated")

        except Exception as e:
            return exception(e)           


    def delete(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            pk = self.kwargs['pk']
            if StaffClassification.objects.filter(id=pk, organization=user_organization.id).exists(): 
                obj = StaffClassification.objects.get(id=pk)
                if obj.is_active == False:
                    return errorMessage("Staff is already deactivated")
                
                position = Positions.objects.filter(is_active=True, staff_classification=pk, staff_classification__organization=user_organization.id)
                if position.exists():
                    return errorMessage("Active position exists against this staff classification")

                emp = Employees.objects.filter(staff_classification=pk, is_active=True)
                if emp.exists():
                    return errorMessage('Active Employees exists against this staff classification')
                    
                obj.is_active = False
                obj.save()   
                return successMessage('Successfully Deleted')     
    
            else:
                return errorMessage('Staff does not exist at this index')
        except Exception as e:
            return exception(e)
