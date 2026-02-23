from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .serializers import *
from helpers.status_messages import *
from .models import *
from organizations.models import Organization
from helpers.get_org import userOrganizationChecks
from helpers.custom_permissions import IsAdminOnly
from helpers.employee_helper import preEmployeeDataChecks
from helpers.decode_token import decodeToken


# Create your views here.
class BanksViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    queryset = Banks.objects.filter(is_active=True)
    serializer_class = BanksViewsetSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if not Banks.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'This Bank does not exists', 'system_status_message': ''})

            obj = Banks.objects.get(id=pk)
            if obj.is_active == False:
                msg = "This Bank is already deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
            obj.is_active = False
            obj.save()
            serializer = BanksViewsetSerializers(obj)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Deactivated Successfully', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)
        
class OrganizationBankDetailViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOnly]
    serializer_class = OrganizationBankDetailViewsetSerializers
    queryset = OrganizationBankDetail.objects.filter(is_active=True)

    def list(self, request, *args, **kwargs):
        try :
            organization_id = decodeToken(request, self.request)['organization_id']
            request.data['organization'] = organization_id
            bank_accounts = self.queryset.filter(organization=organization_id,)
            serializer = OrganizationBankDetailViewsetSerializers(bank_accounts, many=True)  # Use many=True to serialize all results
            return successMessageWithData("sucsess", serializer.data)
        except Exception as e:
            return exception(e)
    def create(self, request, *args, **kwargs):
     try:
        organization_id = decodeToken(request, self.request)['organization_id']
        request.data['organization'] = organization_id

        # Assuming you want to create a new bank account
        serializer = OrganizationBankDetailViewsetSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return successMessageWithData("Success", serializer.data)
        else:
            return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'Invalid data', 'system_status_message': ''})

     except Exception as e:
        return exception(e)

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if not OrganizationBankDetail.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'This Bank does not exist', 'system_status_message': ''})

            obj = OrganizationBankDetail.objects.get(id=pk)
            
            if obj.is_active is False:
                msg = "This Bank is already deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})

            obj.is_active = False
            obj.save()
            
            serializer = OrganizationBankDetailViewsetSerializers(obj)
            
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Deactivated Successfully', 'system_status_message': ''})
            
        except Exception as e:
            # Consider using a more specific exception class, e.g., ObjectDoesNotExist
            return exception(e)

class EmployeeBankDetailsViewset(viewsets.ModelViewSet):
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

            obj = EmployeeBankDetails.objects.filter(employee__uuid=emp_uuid, employee__organization=org_id, is_active = True).order_by('bank__name')
            serializer = EmployeeBankDetailsViewsetSerializers(obj, many=True)
            return success(serializer.data)

        except Exception as e:
            return exception(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            org_id = None
            bank_id = self.kwargs['bank_id']
            emp_uuid = self.kwargs['emp_uuid']  

            # This function whether organization is_active or not
            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            # if user is admin
            if data_check['status'] == 400:
                return Response(data_check)
            elif data_check['status'] == 202:
                org_id = data_check['org_id']
            
            
            # if active emergency contact exists to that employee at this specific id
            query = EmployeeBankDetails.objects.filter(id=bank_id, employee__uuid=emp_uuid, employee__organization__id = org_id)
            if not query.exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This employee does not have any bank at this id', 'system_error_message': ''})

            if not query.filter(is_active=True).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': "Employee's bank is deactivated at this id", 'system_error_message': ''})
        
            obj = EmployeeBankDetails.objects.get(id=bank_id, employee__uuid=emp_uuid, employee__is_active=True,  employee__organization__id = org_id, is_active=True)
            
            serializer = EmployeeBankDetailsViewsetSerializers(obj, many=False) 
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
            
            
            serializer = EmployeeBankDetailsViewsetSerializers(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)


    def patch(self, request, *args, **kwargs):
        try:
            bank_id = self.kwargs['bank_id']
            emp_uuid = self.kwargs['emp_uuid']
            
            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            if data_check['status'] == 400:
                return Response(data_check)
            elif data_check['status'] == 202:
                emp_org_id = data_check['org_id']
            
            emp = Employees.objects.get(uuid=emp_uuid)    
            request.data['employee'] = emp.id
       
            # if no employee id exists
            if not EmployeeBankDetails.objects.filter(employee__uuid=emp_uuid, id=bank_id, employee__organization__id = emp_org_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': 'No bank exists at this id', 'message': '', 'system_status_message': ''})
            
            obj = EmployeeBankDetails.objects.get(employee__uuid = emp_uuid, id=bank_id, employee__organization__id = emp_org_id)
            serializer = EmployeeBankDetailsViewsetSerializers(obj, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()
            
            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)

    def delete(self, request, *args, **kwargs):
        try:
            emp_uuid = self.kwargs['emp_uuid']
            bank_id = self.kwargs['bank_id']
            
            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            if data_check['status'] == 400:
                return Response(data_check)
            elif data_check['status'] == 202:
                emp_org_id = data_check['org_id']
           
            emp = Employees.objects.get(uuid=emp_uuid)    
            request.data['employee'] = emp.id

            # if active emergency contact exists to that employee at this specific id
            if not EmployeeBankDetails.objects.filter(id = bank_id, employee__uuid=emp_uuid,  employee__organization__id = emp_org_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This employee does not have any bank at this id', 'system_error_message': ''})

            obj = EmployeeBankDetails.objects.get(id=bank_id, employee__uuid=emp_uuid, employee__organization__id = emp_org_id)
            if obj.is_active == False:
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This bank id is already deactivated', 'system_status_message': ''})

            obj.is_active = False
            obj.save()
            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT, 'data': '', 'message': 'Successfully Deleted', 'system_status_message': ''})
        except Exception as ppppp:
                return exception(ppppp)




