from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .serializers import *
from helpers.status_messages import *
from .models import *
from helpers.custom_permissions import IsAdminOnly
from helpers.employee_helper import preEmployeeDataChecks


class CompaniesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOnly]
    queryset = Companies.objects.filter(is_active=True)
    serializer_class = CompaniesViewsetSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if not Companies.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'This Company does not exists', 'system_status_message': ''})

            obj = Companies.objects.get(id=pk)
            if obj.is_active == False:
                msg = "This Company is already deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
            obj.is_active = False
            obj.save()
            serializer = CompaniesViewsetSerializers(obj)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Deactivated Successfully', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)


class EmployeeWorkExperienceViewset(viewsets.ModelViewSet):
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

            obj = EmployeeWorkExperience.objects.filter(employee__uuid=emp_uuid, employee__organization=org_id, employee__is_active = True, is_active = True)
            serializer = EmployeeWorkExperienceViewsetSerializers(obj, many=True)
            return success(serializer.data)

        except Exception as e:
            return exception(e)


    def retrieve(self, request, *args, **kwargs):
        try:
            company_id = self.kwargs['company_id']
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
            obj = EmployeeWorkExperience.objects.filter(id=company_id, employee__uuid=emp_uuid, employee__organization = org_id)
            if not obj.exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This employee does not have any work experience at this id', 'system_error_message': ''})
            
            if not obj.filter(is_active=True).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This employee work experience is deactivated at this id', 'system_error_message': ''})

            obj = EmployeeWorkExperience.objects.get(id = company_id, employee__uuid=emp_uuid, employee__is_active=True,  employee__organization__id = org_id, is_active=True)
            serializer = EmployeeWorkExperienceViewsetSerializers(obj, many=False)
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

            if 'joining_date' in request.data:
                request.data._mutable = True
                request.data['employee'] = emp.id 
                request.data['is_active'] = True 
                request.data._mutable = False       
            
            
            serializer = EmployeeWorkExperienceViewsetSerializers(data = request.data)
         
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)
        
        except Exception as e:
            return exception(e)

    
    def patch(self, request, *args, **kwargs):
        try:
            emp_uuid = self.kwargs['emp_uuid']
            company_id = self.kwargs['company_id']

            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            if data_check['status'] == 400:
                return Response(data_check)
            elif data_check['status'] == 202:
                emp_org_id = data_check['org_id']
            
            emp = Employees.objects.get(uuid=emp_uuid)    

            request_data = request.data.get('data', {})
            if request_data:
                request_data._mutable = True
                request_data['employee'] = emp.id
                request_data._mutable = False
  
            # if no employee id exists
            if not EmployeeWorkExperience.objects.filter(employee=emp.id, id=company_id, employee__organization = emp_org_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'No work experience exists at this id', 'system_status_message': ''})
            
            

            obj = EmployeeWorkExperience.objects.get(employee = emp.id, id=company_id, employee__organization = emp_org_id)
            serializer = EmployeeWorkExperienceViewsetSerializers(obj, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()
            
            return successfullyUpdated(serializer.data)
        
        except Exception as e:
            return exception(e)


    def delete(self, request, *args, **kwargs):
        try:
            emp_uuid = self.kwargs['emp_uuid']
            company_id = self.kwargs['company_id']
            
            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            if data_check['status'] == 400:
                return Response(data_check)
            elif data_check['status'] == 202:
                emp_org_id = data_check['org_id']
           
            emp = Employees.objects.get(uuid=emp_uuid)    
            request.data['employee'] = emp.id


            # if active emergency contact exists to that employee at this specific id
            if not EmployeeWorkExperience.objects.filter(id = company_id, employee=emp.id,  employee__organization = emp_org_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This employee does not have any work experience at this id', 'system_error_message': ''})

            obj = EmployeeWorkExperience.objects.get(id=company_id, employee=emp.id, employee__organization = emp_org_id)
            if obj.is_active == False:
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This company is already deactivated', 'system_status_message': ''})

            obj.is_active = False
            obj.save()
            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT, 'data': '', 'message': 'Successfully Deleted', 'system_status_message': ''})
        except Exception as e:
                return exception(e)

  