from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .serializers import *
from helpers.status_messages import *
from .models import *
from organizations.models import Organization
from .views_emp_routers import *
from helpers.get_org import userOrganizationChecks
from helpers.custom_permissions import IsAdminOnly
import json
from rest_framework import generics
from helpers.employee_helper import preEmployeeDataChecks

class EmployeeEmergencyContactsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            emp_uuid = self.kwargs['emp_uuid']  
            org_id = None
            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            # if user is admin
            if data_check['status'] == 400:
                return Response(data_check)
            elif data_check['status'] == 202:
                org_id = data_check['org_id']
            

            obj = EmployeeEmergencyContacts.objects.filter(employee__uuid=emp_uuid, employee__organization__id=org_id, employee__is_active = True, is_active = True)
            serializer = EmployeeEmergencyContactsViewsetSerializers(obj, many=True)
            return success(serializer.data)

        except Exception as e:
            return exception(e)

    # get specific emergency contact of employee
    def retrieve(self, request, *args, **kwargs):
        try:
            contact_id = self.kwargs['contact_id']
            
            emp_uuid = self.kwargs['emp_uuid']  
            org_id = None

            # This function whether organization is_active or not
            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            # if user is admin
            if data_check['status'] == 400:
                return Response(data_check)
            elif data_check['status'] == 202:
                org_id = data_check['org_id']
            
            # if active emergency contact exists to that employee at this specific id
            query = EmployeeEmergencyContacts.objects.filter(id=contact_id, employee__uuid=emp_uuid, employee__is_active=True,  employee__organization__id = org_id)
            
            if not query.exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This employee does not have any emergency contact at this id', 'system_error_message': ''})
        
            if not query.filter(is_active=True).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Emergency contact is deactivated', 'system_error_message': ''})

            obj = EmployeeEmergencyContacts.objects.get(id=contact_id, employee__uuid=emp_uuid, employee__is_active=True,  employee__organization__id = org_id, is_active=True)
            serializer = EmployeeEmergencyContactsViewsetSerializers(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
    
    
    def create(self, request, *args, **kwargs):
        try:
            emp_uuid = self.kwargs['emp_uuid']       

            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            
            if data_check['status'] == 400:
                return Response(data_check)
                        
            emp = Employees.objects.get(uuid=emp_uuid)    
            request.data['employee'] = emp.id
            
            serializer = EmployeeEmergencyContactsViewsetSerializers(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)
        
        except Exception as e:
            return exception(e)

            
                
    def patch(self, request, *args, **kwargs):
        try:
            contact_id = self.kwargs['contact_id']
            emp_uuid = self.kwargs['emp_uuid']       
            

            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            if data_check['status'] == 400:
                return Response(data_check)
            elif data_check['status'] == 202:
                emp_org_id = data_check['org_id']
            
            emp = Employees.objects.get(uuid=emp_uuid)    
            request.data['employee'] = emp.id

            
            # if no employee contact id exists
            if not EmployeeEmergencyContacts.objects.filter(employee=emp.id, employee__organization = emp_org_id, id=contact_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'No Emergency contact exists at this id', 'system_status_message': ''})
            
            obj = EmployeeEmergencyContacts.objects.get(employee=emp.id, employee__organization = emp_org_id, id=contact_id)
            serializer = EmployeeEmergencyContactsViewsetSerializers(obj, data=request.data, partial=True)
            
            
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()
            
            return successfullyUpdated(serializer.data)
        
        except Exception as e:
            return exception(e)



    def delete(self, request, *args, **kwargs):
        try:
            contact_id = self.kwargs['contact_id']
            emp_uuid = self.kwargs['emp_uuid']       
        
            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            if data_check['status'] == 400:
                return Response(data_check)
            elif data_check['status'] == 202:
                emp_org_id = data_check['org_id']
           
            emp = Employees.objects.get(uuid=emp_uuid)    
            request.data['employee'] = emp.id


            # if active emergency contact exists to that employee at this specific id
            if not EmployeeEmergencyContacts.objects.filter(id=contact_id, employee__uuid=emp_uuid, employee__is_active=True,  employee__organization__id = emp_org_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This employee does not have any emergency contact at this id', 'system_error_message': ''})

            obj = EmployeeEmergencyContacts.objects.get(id=contact_id, employee__uuid=emp_uuid, employee__organization__id = emp_org_id)
            if obj.is_active == False:
                return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': '', 'message': 'This emergency contact is already deactivated', 'system_status_message': ''})

            obj.is_active = False
            obj.save()
            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT,  'data': '', 'message': 'Successfully Deleted', 'system_status_message': ''})

        except Exception as e:
            return exception(e)