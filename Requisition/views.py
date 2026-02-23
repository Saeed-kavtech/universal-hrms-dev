from django.shortcuts import render
from .models import *
from django.db.models import Q
from .Serializers import *
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets
from helpers.decode_token import decodeToken
from helpers.status_messages import (
    exception, errorMessage, serializerError, successMessageWithData, 
    success, successMessage, successfullyCreated, successfullyUpdated
)

class ReplacementForViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ReplacementFor.objects.filter(is_active=True)
    serializer_class = ReplacementForSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if not EmployeeTypes.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'This Employee type does not exists', 'system_status_message': ''})

            obj = EmployeeTypes.objects.get(id=pk)
            if obj.is_active == False:
                msg = "This Employee Type is already deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
            obj.is_active = False
            obj.save()
            serializer = ReplacementForSerializers(obj)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Deactivated Successfully', 'system_status_message': ''})
        except Exception as e:
            return exception(e)   
        
class EmployeeRequisitionViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwrags):
     try:
        organization_id = decodeToken(request, self.request)['organization_id']
        employee_id = decodeToken(request, self.request)['employee_id']
        user_id = request.user.id
        request.data['created_by'] = user_id
        request.data['employee'] = employee_id
        request.data['organization'] = organization_id
        supervisor = request.data.get('supervisor')
        if supervisor == None:
            request.data['supervisor'] = employee_id
        serializer = EmployeeRequisitionSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return successMessageWithData('Request added successfully', serializer.data)
        else:
            return serializerError(serializer.errors) 
     except Exception as e:
            return exception(e)
    def employee_view(self, request, *args, **kwargs):
     try:
        organization_id = decodeToken(request, self.request)['organization_id']
        employee_id = decodeToken(request, self.request)['employee_id']
        user_id = request.user.id
        
        # Query employee requisitionss
        query = EmployeeRequisition.objects.filter(
            Q(is_active=True) &
            (Q(created_by=user_id) | Q(supervisor=employee_id)) &
            Q(organization=organization_id)
        )
        
        # Serialize the queryset
        serializer = EmployeeRequisitionSerializers(query, many=True)
        
        # Check if serialization is valid and return data
        
        return successMessageWithData('Data fetched successfully', serializer.data)
    
     except Exception as e:
        return exception(e)
    
    def remove(self, request, *args, **kwargs):
      try:
        pk = self.kwargs['pk']
        claim_data = EmployeeRequisition.objects.get(id=pk, is_active=True)
        if claim_data.status <= 1:
                claim_data.is_active = False
                claim_data.save()
                return successMessage('Successfully deleted')
        else:
            return errorMessage('You cannot delete at this moment')
      except Exception as e:
            return exception(e)
        
    def sendtohr(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            #  employee_id = decodeToken(request, self.request)['employee_id']
            emp_data = EmployeeRequisition.objects.get(id=pk, is_active=True)
            emp_data.status = 2
            emp_data.save()
            return successMessage('success')
            #  return successMessage('success')
        except Exception as e:
                return exception(e)
     
 
class HRRequisitionViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def hr_view(self, request, *args, **kwargs):
     try:
        organization_id = decodeToken(request, self.request)['organization_id']
        # employee_id = decodeToken(request, self.request)['employee_id']
        # user_id = request.user.id
        
        # Query employee requisitionss
        query = EmployeeRequisition.objects.filter(is_active=True, organization=organization_id, status__gt=1)
        
        # Serialize the queryset
        serializer = EmployeeRequisitionSerializers(query, many=True)
        
        # Check if serialization is valid and return data
        
        return successMessageWithData('Data fetched successfully', serializer.data)
    
     except Exception as e:
        return exception(e)
        
    def hr_status_update(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            status = request.data.get('status')
            #  employee_id = decodeToken(request, self.request)['employee_id']
            emp_data = EmployeeRequisition.objects.get(id=pk, is_active=True)
            emp_data.status = status
            emp_data.save()
            return successMessage('success')
            #  return successMessage('success')
        except Exception as e:
                return exception(e)
            
    def update(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            job = request.data.get('job')
            job_query = Jobs.objects.get(id = job)
            #  employee_id = decodeToken(request, self.request)['employee_id']
            emp_data = EmployeeRequisition.objects.get(id=pk, is_active=True)
            emp_data.job = job_query
            emp_data.save()
            return successMessage('success')
            #  return successMessage('success')
        except Exception as e:
                return exception(e)
     
 
    
        
# Create your views here.
