from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .serializers import PositionsSerializers
from django.db.models import Max
from organizations.models import StaffClassification
from organizations.serializers import StaffClassificationSerializers
from departments.models import Departments
from departments.serializers import DepartmentsSerializers
from .models import Positions
from helpers.status_messages import success, errorMessage, successfullyCreated, successfullyUpdated, serializerError, exception, nonexistent, successfullyDeleted
from helpers.custom_permissions import IsAuthenticated, DoesOrgExists
from jobs.models import Jobs
from jd.models import JdDescriptions

# Create your views here.
class PositionViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]
    
    def list(self, request, *args, **kwargs): 
        try:
            user_organization = request.data.get('organization_profile')
            
            obj = Positions.objects.filter(is_active=True, staff_classification__organization=user_organization).order_by('title')
            serializer = PositionsSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def retrieve(self, request, *args, **kwargs):
        try:       
            user_organization = request.data.get('organization_profile')
            pk = self.kwargs['pk']
            if Positions.objects.filter(id=pk, staff_classification__organization=user_organization.id).exists():  
                obj = Positions.objects.get(id=pk)
                serializer = PositionsSerializers(obj, many=False)
                return success(serializer.data)
            else:
                return nonexistent(var = 'Position')
        except Exception as e:
            return exception(e)


    def create(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')

            if not 'department' in request.data:
                return errorMessage('Department is a required field')

            if not 'staff_classification' in request.data:
                return errorMessage('Staff classification is a required field')
            
            department_id = request.data['department']
            staffclassification_id = request.data['staff_classification']

            checks = self.prePositionChecks(department_id, staffclassification_id, user_organization.id)
            if checks['status'] == 400:
                return Response(checks)
            
            request.data['grouphead'] = checks['data'] # This function returns the grouphead id

            # generating code:
            staff_classification_obj = StaffClassification.objects.get(id = staffclassification_id, organization=user_organization.id)
            code_str_part = staff_classification_obj.initial + '-' + str(staff_classification_obj.level) + '-'
            pos_query = Positions.objects.filter(staff_classification=staff_classification_obj.id, staff_classification__organization=user_organization.id)
            max_number = pos_query.aggregate(max_number=Max('code_number'))['max_number'] or 0
            max_number += 1
            request.data['code_number'] = max_number
            code = f"{code_str_part}{max_number:04d}"
            request.data['code'] = code

            if Positions.objects.filter(code=code, is_active=True, staff_classification__organization=user_organization.id).exists():
                return errorMessage('Code should be unique')

            serializer = PositionsSerializers(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return successfullyCreated(serializer.data)
            else:
                return serializerError(serializer.errors)
        except Exception as e:
            return exception(e)
        
    
    def patch(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            user_organization = request.data.get('organization_profile')
            if Positions.objects.filter(id=pk, staff_classification__organization=user_organization.id).exists():
                department_id = None
                staffclassification_id = None
                
                if 'department' in request.data:
                    department_id = request.data['department']
                
                if 'staff_classification' in request.data:
                    staffclassification_id = request.data['staff_classification']
                    
                checks = self.prePositionChecks(department_id, staffclassification_id, user_organization.id)
                if checks['status'] == 400:
                    return Response(checks)
                if department_id is not None:
                    request.data['grouphead'] = checks['data']
                
                obj = Positions.objects.get(id=pk)    
                serializer = PositionsSerializers(obj, data = request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return successfullyUpdated(serializer.data)
                else:
                    return serializerError(serializer.errors)
            else:
                
                return nonexistent(var = 'Position')
        except Exception as e:
            return exception(e)


    def delete(self, request, *args, **kwargs):        
        try:
            position_id = self.kwargs['pk']
            user_organization = request.data.get('organization_profile')

            if Positions.objects.filter(id=position_id, staff_classification__organization=user_organization.id).exists(): 
                obj = Positions.objects.get(id=position_id)
                if obj.is_active == False:
                    msg = "This Position is already deactivated"
                    return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message':msg, 'system_status_message': ''})

                if Jobs.objects.filter(position=position_id, is_active=True).exists():
                    return errorMessage("Job exists against this position. Kindly deactivate the job first")
                if JdDescriptions.objects.filter(position=position_id, is_active=True).exists():
                    return errorMessage("Job description exists against this position. Kindly! deactivate the jd first")

                obj.is_active = False
                obj.save()
                serializer = PositionsSerializers(obj, many=False)
                return successfullyDeleted(serializer.data)
            else:
                return Response({'status':400, 'system_status': status.HTTP_404_NOT_FOUND, 'data': '', 'message': "Position does not exist at this index", 'system_status_message': ''}) 
        except Exception as e:
            return exception(e)


    def pre_data(self, request, *args, **kwargs):
        try:  
            user_organization = request.data.get('organization_profile')
            
            department_obj = Departments.objects.filter(grouphead__organization=user_organization.id, is_active=True)
            department_serializer = DepartmentsSerializers(department_obj, many=True)

            staff_obj = StaffClassification.objects.filter(organization=user_organization.id, is_active=True)
            staff_serializer = StaffClassificationSerializers(staff_obj, many=True)

            data = {'staff_classification': staff_serializer.data, 'department': department_serializer.data}
            return success(data)
                
        except Exception as e:
            return exception(e)



    def prePositionChecks(self, department_id, staffclassification_id, organization_id):
        try:
            response = {'status': 400, 'data': '', 'message': ''}
            if staffclassification_id is not None: 
                staff_classification_query = StaffClassification.objects.filter(id = staffclassification_id, organization=organization_id)
                if not staff_classification_query.exists():
                    response['message'] = 'Staff classification does not exists'
                    return response
                if not staff_classification_query.filter(is_active=True).exists():
                    response['message'] = 'Staff classification is deactivated'
                    return response
                    
            
            if department_id is not None:
                department_query = Departments.objects.filter(id=department_id, grouphead__organization=organization_id)
                if not department_query.exists():
                    response['message'] = 'Department does not exists'
                    return response
                if not department_query.filter(is_active=True).exists():
                    response['message'] = 'Department is deactivated'
                    return response
                   
                obj = department_query.get()
                response['data'] = obj.grouphead.id

            response['status'] = 200
            return response
        except Exception as e:
            return {'status': 400, 'data': '', 'message': 'Exception Error', 'system_error_message': str(e)}    

    