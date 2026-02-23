from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .serializers import *
from helpers.status_messages import *
from .models import *
from helpers.custom_permissions import IsAdminOnly
from organizations.models import Organization
from helpers.get_org import userOrganizationChecks
import json
from rest_framework import generics
from helpers.employee_helper import preEmployeeDataChecks

class DependentViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Dependent.objects.filter(is_active=True)
    serializer_class = DependentViewsetSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if not Dependent.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': "This employee's dependent does not exists", 'system_status_message': ''})

            obj = Dependent.objects.get(id=pk)
            if obj.is_active == False:
                msg = "This Employee's dependent is already deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
            obj.is_active = False
            obj.save()
            serializer = DependentViewsetSerializers(obj)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Deactivated Successfully', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)


class EmployeeDependentViewset(viewsets.ModelViewSet):
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
            

            obj = EmployeeDependent.objects.filter(employee__uuid = emp_uuid, employee__organization__id=org_id, employee__is_active = True, is_active = True)
            serializer = EmployeeDependentViewsetSerializers(obj, many=True)
            return success(serializer.data)

        except Exception as e:
            return exception(e)


    def retrieve(self, request, *args, **kwargs):
        try:
            dependent_id = self.kwargs['dependent_id']
            emp_uuid = self.kwargs['emp_uuid']
            org_id = None

            # This function whether organization is_active or not
            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            # if user is admin
            if data_check['status'] == 400:
                return Response(data_check)
            elif data_check['status'] == 202:
                org_id = data_check['org_id']
            

            # if active emergency dependent exists to that employee at this specific id
            obj = EmployeeDependent.objects.filter(id=dependent_id, employee__uuid=emp_uuid, employee__organization__id = org_id)
            if not obj.exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This employee does not have any dependent at this id', 'system_error_message': ''})
            
            if not obj.filter(is_active=True).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This employee dependent is deactivated at this id', 'system_error_message': ''})

            obj = EmployeeDependent.objects.get(id = dependent_id, employee__uuid=emp_uuid, employee__organization__id = org_id, is_active=True)
            serializer = EmployeeDependentViewsetSerializers(obj, many=False)
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
            
            serializer = EmployeeDependentViewsetSerializers(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)
        
        except Exception as e:
            return exception(e)

    
    def patch(self, request, *args, **kwargs):
        try:
            emp_uuid = self.kwargs['emp_uuid']
            dependent_id = self.kwargs['dependent_id']

            
            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            if data_check['status'] == 400:
                return Response(data_check)
            elif data_check['status'] == 202:
                emp_org_id = data_check['org_id']
            
            emp = Employees.objects.get(uuid=emp_uuid)    
            request.data['employee'] = emp.id
            
            # if no employee id exists
            if not EmployeeDependent.objects.filter(employee=emp.id, employee__organization = emp_org_id, id=dependent_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'No Dependent exists at this id', 'system_status_message': ''})
            

            obj = EmployeeDependent.objects.get(employee = emp.id, employee__organization = emp_org_id, id=dependent_id)
            serializer = EmployeeDependentViewsetSerializers(obj, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()
            
            return successfullyUpdated(serializer.data)
        
        except Exception as e:
            return exception(e)


    def delete(self, request, *args, **kwargs):
        try:
            dependent_id = self.kwargs['dependent_id']

            emp_uuid = self.kwargs['emp_uuid']
        
            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            if data_check['status'] == 400:
                return Response(data_check)
            elif data_check['status'] == 202:
                emp_org_id = data_check['org_id']
           
            emp = Employees.objects.get(uuid=emp_uuid)    
            request.data['employee'] = emp.id

            # if active emergency dependent exists to that employee at this specific id
            if not EmployeeDependent.objects.filter(id = dependent_id, employee__uuid=emp_uuid, employee__is_active=True,  employee__organization__id = emp_org_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This employee does not have any Dependent at this id', 'system_error_message': ''})

            obj = EmployeeDependent.objects.get(id=dependent_id, employee__uuid=emp_uuid, employee__organization__id = emp_org_id)
            if obj.is_active == False:
                return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': '', 'message': "Employee's Dependent is already deactivated", 'system_status_message': ''})

            obj.is_active = False
            obj.save()
            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT, 'data': '', 'message': 'Successfully Deleted', 'system_status_message': ''})
        except Exception as e:
                return exception(e)



class PreEmployeeDependentView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        try:
            dependent_obj = Dependent.objects.filter(is_active=True)
            dependent_serializer = DependentViewsetSerializers(dependent_obj, many=True)
            data = {'dependent': dependent_serializer.data}

            return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': data, 'message': 'Success', 'system_status_message': ''})

        except Exception as e:
            return exception(e)