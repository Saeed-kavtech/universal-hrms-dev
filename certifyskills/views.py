import datetime
from django.shortcuts import render
from rest_framework import viewsets
from helpers.status_messages import (
    exception,success,errorMessage, serializerError,successfullyUpdated,successMessage,errorMessageWithData,successfullyCreated, successMessageWithData
)
from helpers.decode_token import decodeToken
from helpers.custom_permissions import IsAuthenticated, IsEmployeeOnly,IsAdminOnly
from employees.models import Employees
from employees.serializers import EmployeePreDataSerializers
from employees.views_project_roles import EmployeeProjectsRolesViewset
from .models import *
import json
from django.db.models import Q
from .serializers import *
# Create your views here.

class LNDCertificationsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = LNDCertifications.objects.all() 
    serializer_class = LNDCertificationsSerializers


    def get_queryset(self):
        token_data = decodeToken(self, self.request)
        organization_id = token_data['organization_id']
        employee_id = token_data['employee_id']
        
        return self.queryset.filter(employee=employee_id, employee__organization=organization_id)
    
    def create(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            user_id = request.user.id
             
            # print(request.data)
            # if not request.data:
            #     return errorMessage("Request Data is empty")

            

            required_fields = ['title', 'duration','cost','course_url']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData(
                    'make sure you have added all the required fields',
                    'title, duration,cost,course_url'
                )

            
            employee_query=Employees.objects.filter(id=employee_id,organization=organization_id,is_active=True)

            if not employee_query.exists():
                return errorMessage("Employee not exists in current organization")
            
            team_lead=request.data.get('team_lead',None)
            if team_lead is not None:
                team_lead_query=Employees.objects.filter(id=team_lead,organization=organization_id,is_active=True)

                if not team_lead_query.exists():
                    return errorMessage("Team lead not exists in current organization")
                
            # if team_lead==employee_id:
            #     return errorMessage('Employee cannot set themselves as their own team lead')
                

            request.data['created_by'] = user_id
            request.data['employee']=employee_id

            serializer=self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)
                
        except Exception as e:
            return exception(e)
        

    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            # print("Test1")
            query = self.queryset.filter(employee=employee_id,employee__organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def patch(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            # user_id = request.user.id
            # print(pk)
            if not request.data:
                return errorMessage("Request Data is empty")

            employee_id=request.data.get('employees',None)


            if employee_id:
                employee_query=Employees.objects.filter(id=employee_id,organization=organization_id,is_active=True)

                if not employee_query.exists():
                    return errorMessage("Employee not exists in current organization")
                
            query = self.get_queryset().filter(id=pk)
            
            if not query.exists():
                return errorMessage('No certification request  exists')
            
            if not query.filter(certification_status=1):
                return errorMessage('For update request must be in pending state')
            
            obj = query.filter(certification_status=1).get()
            
            serializer=self.serializer_class(obj, data = request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()

            return successfullyUpdated(serializer.data)
            
        except Exception as e:
            return exception(e)
        


    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            
            query = self.get_queryset().filter(id=pk)
            if not query.exists():
                return errorMessage('Certification does not exists')
            if not query.filter(is_active=True).exists():
                return errorMessage('Certification is already deactivated at this id')
            obj = query.get()
            
            if obj.certification_status:
                if obj.certification_status != 1:
                    return errorMessage('Certification can only be deactivated when it is in pending state')
            
            obj.is_active=False
            obj.save()

            
            return successMessage('Certification is deactivated successfully')
        except Exception as e:
            return exception(e)
        

 
    def get_request_to_teamlead(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            query = self.queryset.filter(team_lead=employee_id,employee__organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def get_request_to_hr(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            query = self.queryset.filter(employee__organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def assign_team_lead(self, request, *args, **kwargs):
        try:
            # print("Test")
            pk = self.kwargs['pk']
            organization_id = decodeToken(request, self.request)['organization_id']

            user = request.user

            if not user.is_admin:
                return errorMessage('User is not an admin user')
            
            
            query = LNDCertifications.objects.filter(id=pk,employee__organization=organization_id,is_active=True)
            if request.data is not None:
                employee_id=request.data.get('team_lead',None)
                if employee_id:
                   employee_query=Employees.objects.filter(id=employee_id,organization=organization_id,is_active=True)

                   if not employee_query.exists():
                    return errorMessage("Employee not exists in current organization")
                
                if not query.exists():
                    return errorMessage('No certification request  exists')
                obj = query.get()
                serializer=self.serializer_class(obj, data = request.data, partial=True)
                if not serializer.is_valid():
                    return serializerError(serializer.errors)
                serializer.save()

            return successMessage('Success')
        except Exception as e:
            return exception(e)
    
    def approval_by_team_lead(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']

            user_id=request.user.id

            required_fields = ['certification_status', 'reason']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [certification_status,reason]')
            
            query = LNDCertifications.objects.filter(id=pk,team_lead=employee_id,employee__organization=organization_id,is_active=True)
            if not query.exists():
                return errorMessage('No certification request  exists')
            
            if query.filter(certification_status=5):
                return errorMessage('Certification is already approved by HR')
            
            if query.filter(certification_status=request.data['certification_status']).exists():
                # return errorMessage('Same status is already set against current certification')
                return successMessage('Status changed successfully')

            
            obj = query.get()
            
            reason = request.data.get('reason', None)
            status=request.data.get('certification_status',None)
            request.data['approved_by']=user_id
            
            if reason:
                # print(status)
                output = self.certification_reason(pk, reason,status,user_id)
                print(output)
                if output['status'] == 400:
                        # print("IF")
                        return errorMessage(output['message'])


            
            serializer=self.serializer_class(obj, data = request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()

            return successMessage('Status changed successfully')
    
        except Exception as e:
            return exception(e)
        

    def approval_by_hr(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            organization_id = decodeToken(request, self.request)['organization_id']
            user_id=request.user.id

            user = request.user

            if not user.is_admin:
                return errorMessage('User is not an admin user')

            required_fields = ['certification_status', 'reason']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all the required fields','certification_status,reason')
            
            query = LNDCertifications.objects.filter(id=pk,employee__organization=organization_id,is_active=True)
            if not query.exists():
                return errorMessage('No certification request  exists')
            
            
            
            if not query.filter(team_lead__isnull=True).exists():
                if not query.filter(Q(certification_status=2) | Q(certification_status=3)).exists():
                    return errorMessage('HR cannot take action until a decision is pending from the team lead')

            
            if query.filter(certification_status=request.data['certification_status']).exists():
                return successMessage('Status changed successfully')

            
            obj = query.get()
            
            reason = request.data.get('reason', None)
            status=request.data.get('certification_status',None)
            request.data['approved_by']=user_id
            
            if reason:
                # print(status)
                output = self.certification_reason(pk, reason,status,user_id)
                # print(output)
                if output['status'] == 400:
                        # print("IF")
                        return errorMessage(output['message'])


            
            serializer=self.serializer_class(obj, data = request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()

            return successMessage('Status changed successfully')
    
        except Exception as e:
            return exception(e)
        
    def certification_reason(self,id,reason,status,user_id):
        try:
            result = {
                'status': 400, 
                'message': '', 
                'system_error_message': '',   
            }
            
            data={
                "certification":id,
                "decision_reason":reason,
                "certification_status":status,
                "created_by":user_id,
            }
            

            serializer = LNDCertificationLogsSerializers(data=data)
            if not serializer.is_valid():
                print(serializer.errors)
                result['message'] = serializer.errors
                return result
            
            serializer.save()

            result['status'] = 200
            return result

        except Exception as e:
            return exception(e)



class SubmissionLNDCertificationsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = LNDCertifications.objects.all() 
    serializer_class = SubmissionLNDCertificationsSerializers

    
    def get_queryset(self):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            
            return self.queryset.filter(employee=employee_id, employee__organization=organization_id)
      
        except Exception as e:
            return exception(e)
    

    def certificate_submission(self,request,*args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            # user_id=request.user.id
            pk = self.kwargs['pk']
            
            required_fields = ['certificate']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added  the required field','certificate')
            

            query = LNDCertifications.objects.filter(id=pk,employee=employee_id,employee__organization=organization_id,is_active=True)
            if not query.exists():
                return errorMessage('No certification  exists against given id')
            
            elif not query.filter(certification_status=4).exists():
                return errorMessage('For submission certification must be approved by HR')
            
            elif  not query.filter(is_reimbursement=False).exists():
                return errorMessage('Reimbursement already approved')
            
            obj=query.get()

            request.data._mutable = True
            request.data['reimbursement_status']=1
            request.data['is_reimbursement']=False
            
        
            
            serializer=SubmissionLNDCertificationsSerializers(obj, data=request.data, partial=True)
            if not serializer.is_valid():
                # print(serializer.initial_data)
                if serializer.errors.get('certificate'):
                    return errorMessage(serializer.errors.get('certificate', [''])[0])
                elif serializer.errors.get('certification_receipt'):
                    return errorMessage(serializer.errors.get('certification_receipt', [''])[0])
                # print(serializer.errors)
                return serializerError(serializer.errors)
            
            # print(serializer.data)
            serializer.save()

            # return successMessage('Submitted successfully')
            return successMessageWithData('Submitted successfully',serializer.data)
        
        except Exception as e:
            return exception(e)
        

    def get_submission_to_employee(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            query = self.queryset.filter(employee=employee_id,certificate__isnull=False,employee__organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def get_specific_submission_to_employee(self, request, *args, **kwargs):
        try:
            pk=self.kwargs['pk']
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            query = self.queryset.filter(id=pk,employee=employee_id,certificate__isnull=False,employee__organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def get_submission_to_team_lead(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            query = self.queryset.filter(team_lead=employee_id,certificate__isnull=False,employee__organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def get_specific_submission_to_team_lead(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            pk=self.kwargs['pk']
            query = self.queryset.filter(id=pk,team_lead=employee_id,certificate__isnull=False,employee__organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def get_submission_to_hr(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            query = self.queryset.filter(certificate__isnull=False,employee__organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def get_specific_submission_to_hr(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            pk=self.kwargs['pk']
            query = self.queryset.filter(id=pk,certificate__isnull=False,employee__organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def reimbursement_approval_by_hr(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            pk = self.kwargs['pk']
            # user_id=request.user.id

            user = request.user

            if not user.is_admin:
                return errorMessage('User is not an admin user')
            
            query = LNDCertifications.objects.filter(id=pk,employee__organization=organization_id,is_active=True)
            if not query.exists():
                return errorMessage('No certification exists against given id')
            
            elif not query.filter(certification_status=4).exists():
                return errorMessage('For submission certificate must approved by HR')
            
            elif query.filter(reimbursement_status__gte=2,is_reimbursement=True):
                return errorMessage('Reimbursement is already approved by HR')
            
            obj=query.get()

            obj.reimbursement_status=2
            obj.is_reimbursement=True

            obj.save()
            return successMessage('Success')

        except Exception as e:
            return exception(e)

        
    


class CertificationPreDataViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            # scale_complexity=ScaleComplexityViewset().pre_data(organization_id)
            employees_projects=EmployeeProjectsRolesViewset().pre_data(employee_id,organization_id,None)
           
            # print(kpis_group_status)
            employees = Employees.objects.filter(organization=organization_id, is_active=True)

            employees_serializers = EmployeePreDataSerializers(employees, many=True)
            


            data = {
                
                'employees': employees_serializers.data,
                'employees_projects':employees_projects,
              
            }

            return successMessageWithData('Success', data)
        except Exception as e:
            return exception(e)






    


  

