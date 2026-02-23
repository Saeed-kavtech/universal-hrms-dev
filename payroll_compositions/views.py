from rest_framework import viewsets
from .serializers import EmployeeProcessedSalarySerializer,PFSerializer,PayrollCustomisedPFSerializer,PayrollCustomisedTrainingSerializer,PayrollCustomisedCertificationSerializer,ProcessedSalarySerilaizer,SalaryBatchAttributesSerializer,TaxSlabSerializer,PayrollAttributesViewsetSerializers, UpdatePayrollAttributesViewsetSerializers, PayrollBatchesViewsetSerializers, PayrollBatchCompositionsViewsetSerializers, UpdatePayrollBatchCompositionsViewsetSerializers, EmployeePayrollConfigurationSerializer, PayrollAttributesSerializer, MonthlyDistributionSerializer, EligibleEmployeesSerializer, FixedDistributionSerializer, VariableDistributionsSerializer, valueTypeChoicesSerializer, customisedAttributesSerializer, PayrollBatchAttributesSerializer, PayrollCustomisedGymSerializer, PayrollCustomisedMedicalSerializer, SalaryBatchSerilaizer, SalaryBatchAttributeSerilaizer
from .models import PFRecords,PayrollCustomisedPFProcesses,PayrollCustomisedTrainingProcesses,PayrollCustomisedCertificationsProcesses,ProcessedSalary,TaxSlab,CompositionAttributes, PayrollBatches, PayrollBatchCompositions, PayrollBatchAttributes, EmployeePayrollConfiguration, EmployeePayrollConfigurationLog, PayrollAttributes, MonthlyDistribution, EligibleEmployees, FixedDistribution, VariableDistributions, valueTypeChoices, customisedAttributes, PayrollCustomisedGymProcesses, PayrollCustomisedMedicalProcesses, SalaryBatch, SalaryBatchAttributes
from certifyskills.serializers import LNDCertificationsSerializers
from training.serializers import ListTrainingEmployeeSerializer
from organizations.models import StaffClassification
from employees.models import Employees
from employees.serializers import ListEmployeeViewsetSerializers
from reimbursements.models import EmployeesGymAllowance, EmployeesMedicalAllowance, ProvidentFunds, EmployeeProvidentFunds
from reimbursements.serializers import EmployeesGymAllowanceSerializers, EmployeesMedicalAllowanceSerializers
from banks.models import *
from certifyskills.models import LNDCertifications
from training.models import TrainingEmployee
from helpers.status_messages import success, successMessage, errorMessage, exception, serializerError, successfullyCreated
from helpers.custom_permissions import IsAuthenticated, DoesOrgExists, IsAdminOnly
import datetime
import uuid
from decimal import Decimal
from rest_framework import generics,status
from rest_framework.response import Response
from helpers.decode_token import decodeToken
from django.forms.models import model_to_dict
from django.db.models import Sum, Count
from django.db import transaction
from datetime import date, timedelta
from datetime import datetime as DATE
import re
import json
from helpers.status_messages import ( 
    exception, errorMessage, serializerError, successMessageWithData,
    success, successMessage, successfullyCreated, successfullyUpdated, errorMessageWithData
)

# Create your views here.
class PayrollAttributesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def list(self, request, *args, **kwargs):
        try: 
            user_organization = request.data.get('organization_profile')
            obj = CompositionAttributes.objects.filter(organization=user_organization.id, is_active=True).order_by('level')         
            serializer = PayrollAttributesViewsetSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def retrieve(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            pk = self.kwargs['pk']

            query = CompositionAttributes.objects.filter(id = pk, organization=user_organization.id)
            if not query.exists():
                return errorMessage('No attribute exists at this id')
            elif query.filter(is_active=False).exists():
                return errorMessage('This attribute is deactivated')

            obj = query.get()
            serializer = PayrollAttributesViewsetSerializers(obj)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def create(self, request, *args, **kwargs):
        try: 
            user_organization = request.data.get('organization_profile')
            request.data['organization'] = user_organization.id

            # checks if batch exists or not
            query = PayrollBatches.objects.filter(organization=user_organization.id, is_active=True)
            if not query.exists():
                return errorMessage("Create a new batch first")
            # if batch is locked the attribute cannot get created
            if query.filter(is_lock=True).exists():
                return errorMessage("Batch is locked. You cannot create attributes using the current batch")

            if 'title' not in request.data:
                return errorMessage("title is a required field")
            if 'level' not in request.data:
                return errorMessage("level is a required field")
            
            # level should be unique organization based
            level = request.data['level']
            if CompositionAttributes.objects.filter(organization=user_organization.id, level=level, is_active=True).exists():
                return errorMessage('Level is not unique')
            

            serializer = PayrollAttributesViewsetSerializers(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)    
            
            serializer.save()
            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)
    

    def patch(self, request, *args, **kwargs):
        try: 
            user_organization = request.data.get('organization_profile')
            pk = self.kwargs['pk']

            # checks if batch exists or not
            query = PayrollBatches.objects.filter(organization=user_organization.id, is_active=True)
            if not query.exists():
                return errorMessage("Create a new batch first")
            # if batch is locked the attribute cannot get updated
            if query.filter(is_lock=True).exists():
                return errorMessage("Batch is locked. You cannot updated using the current batch")


            # checks if attributes exists at this id or not
            query = CompositionAttributes.objects.filter(id = pk, organization=user_organization.id)
            if not query.exists():
                return errorMessage('No attribute exists at this id')

            obj = query.get()

            
            if 'is_active' in request.data:
                if request.data['is_active'] == 'False':
                    return errorMessage("You cannot change the is_active status to False from here")
            
            if 'level' in request.data:
                level = request.data['level']
                if CompositionAttributes.objects.filter(organization=user_organization.id, level=level, is_active=True).exclude(id=pk).exists():
                    return errorMessage('Level is not unique')
            

            serializer = UpdatePayrollAttributesViewsetSerializers(obj, data=request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)    
            
            serializer.save()
            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)


    def delete(self, request, *args, **kwargs):
        try: 
            user_organization = request.data.get('organization_profile')
            pk = self.kwargs['pk']

            # checks if batch exists or not
            query = PayrollBatches.objects.filter(organization=user_organization.id, is_active=True)
            if not query.exists():
                return errorMessage("No batch exists")
            if query.filter(is_lock=True).exists():
                return errorMessage("This batch is locked. You cannot change the attributes")
            payroll_obj = query.get()

            query = CompositionAttributes.objects.filter(id = pk, organization=user_organization.id)
            if not query.exists():
                return errorMessage('No attribute exists at this id')
            elif query.filter(is_active=False).exists():
                return errorMessage('This attribute is already deactivated')
            
            obj = query.get()

            if PayrollBatchCompositions.objects.filter(payroll_batch = payroll_obj.id,payroll_compositions_attribute=obj.id, payroll_compositions_attribute__organization = user_organization.id, is_active=True):
                return errorMessage('To deactivate this attribute. You need to deactivate the batch composition first')


            obj.is_active=False
            obj.save()

            return successMessage('Successfully deactivated')
        except Exception as e:
            return exception(e)



class PayrollBatchesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]
        
    def retrieve(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')

            query = PayrollBatches.objects.filter(organization=user_organization.id, is_active=True)
            
            if not query.exists():
                return successMessage("No active batch exists")

            obj = query.get()
            serializer = PayrollBatchesViewsetSerializers(obj)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def create(self, request, *args, **kwargs):
        try: 
            if not request.user.is_privileged:
                 return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            user_organization = request.data.get('organization_profile')
            request.data['organization'] = user_organization.id
            request.data['start_date'] = datetime.date.today()
            batch_no = str(uuid.uuid4())[:8]
            request.data['batch_no'] = batch_no
            batch = PayrollBatches.objects.filter(organization=user_organization.id)
            # if batch code already existed
            if batch.filter(batch_no=batch_no).exists():
                batch_no = str(uuid.uuid4())[:9]
                request.data['batch_no'] = batch_no

            serializer = PayrollBatchesViewsetSerializers(data = request.data)
            print(request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)    
            
            serializer.save()
            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)
    def patch_taxcountry(self, request, *args, **kwargs):
        try:
            if not request.user.is_privileged:
                 return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            user_organization = request.data.get('organization_profile')
            pk = self.kwargs['pk']
            country = request.data.get('country')
            # payroll_batch = request.data.get('payroll_batch')
            
            batch_query = PayrollBatches.objects.filter(id=pk, organization=user_organization.id, is_active=True)
            obj = batch_query.get()
            if not obj:
                return errorMessage("No active batch exists")
            elif obj.is_lock == True:
                return errorMessage("This batch is already locked")
            
            obj.country = country
            obj.created_by = request.user
            obj.save()
            return successMessage('Batch updated succesfully')
            
        except Exception as e:
            return exception(e)
        
    

            
            # deactivating all the existing batches
            # if batch.exclude(id=obj.id).filter(is_active=True).exists():
            #     for data in batch.exclude(id=obj.id).filter(is_active=True):
            #         data.is_active=False
            #         data.save()
            
            # batch_composition = PayrollBatchCompositions.objects.exclude(payroll_batch=obj.id).filter(payroll_compositions_attribute__organization=user_organization.id, is_active=True)
            # if batch_composition.exists():
            #     for data in batch_composition:
            #         self.createPayrollBatchCompositions(data, obj)
            #         data.is_active = False
            #         data.save()

            
        except Exception as e:
            return exception(e)


    def delete(self, request, *args, **kwargs):
        try: 
            if not request.user.is_privileged:
                     return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            user_organization = request.data.get('organization_profile')

            query = PayrollBatches.objects.filter(organization=user_organization.id, is_active=True)
            if not query.exists():
                return errorMessage('No active batch exists')

            obj = query.get()
            obj.end_date = datetime.date.today()
            obj.is_active=False
            obj.save()

            return successMessage('Successfully deactivated')
        except Exception as e:
            return exception(e)


    def createPayrollBatchCompositions(self,request, data, obj):
        try:
            if not request.user.is_privileged:
                 return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            composition_array = {
                'payroll_attribute': data.payroll_attribute.id,
                'payroll_batch': obj.id,
                'attribute_percentage': data.attribute_percentage,
                'is_active': True
            }
            serializer = PayrollBatchCompositionsViewsetSerializers(data = composition_array)
            if not serializer.is_valid():
                print(serializer.errors)
                return {'status': 400, 'message': 'validation_error'}
            serializer.save()
            return {'status': 200}
        except Exception as e:
            return {'status': 400, 'system_error_message': str(e)}


class PayrollBatchCompositionsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def list(self, request, *args, **kwargs):
        try: 
            user_organization = request.data.get('organization_profile')
            
            # checks if batch exists or not
            query = PayrollBatchCompositions.objects.filter(payroll_compositions_attribute__organization=user_organization.id, is_active=True).order_by('-id')
            if not query.exists():
                return errorMessage('Payroll batch composition does not exists')
            elif not query.filter(is_active=True):
                return errorMessage("Payroll composition is already deactivated")

            serializer = PayrollBatchCompositionsViewsetSerializers(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
                
    def retrieve(self, request, *args, **kwargs):
        try: 
            user_organization = request.data.get('organization_profile')
            pk = self.kwargs['pk']
            
            query = PayrollBatchCompositions.objects.filter(id=pk, payroll_compositions_attribute__organization=user_organization.id)
            if not query.exists():
                return errorMessage('Payroll batch composition does not exists')
            elif not query.filter(is_active=True):
                return errorMessage("Payroll composition is deactivated")

            obj = query.get()
            serializer = PayrollBatchCompositionsViewsetSerializers(obj)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
                
    def create(self, request, *args, **kwargs):
        try: 
            user_organization = request.data.get('organization_profile')
            payroll_batch = request.data.get('payroll_batch')
            if not request.user.is_privileged:
                return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            
            # checks if batch exists or not
            query = PayrollBatches.objects.filter(id=payroll_batch,organization=user_organization.id, is_active=True)
            if not query.exists():
                return errorMessage("Create a new batch first")
            if query.filter(is_lock=True).exists():
                return errorMessage("This batch is already used and it is locked. Kindly, create a new batch")
            # obj = query.get()
            # request.data['payroll_batch'] = obj.id

            if 'payroll_compositions_attribute' not in request.data:
                return errorMessage('Payroll attribute is a required field')
            if 'attribute_percentage' not in request.data:
                return errorMessage('The attribute percentage is a required field')
            

            # attributes percentage checks
            percentage = Decimal(request.data['attribute_percentage'])
            if not (percentage > Decimal(0.00) and percentage <= Decimal(100.00)):
                return errorMessage("Percentage should be greater than 0 but less than equal to 100")

            # checks if that payroll already exists or not
            payroll_compositions_attribute_id = request.data['payroll_compositions_attribute']
            try:
             batch_composition = PayrollBatchCompositions.objects.filter(payroll_batch=payroll_batch,payroll_compositions_attribute=payroll_compositions_attribute_id, payroll_compositions_attribute__organization=user_organization.id, is_active=True)
             if batch_composition.exists():
                return errorMessage("This payroll batch composition already exists")
            except Exception as e:
                print(exception(e))
                
                
            serializer = PayrollBatchCompositionsViewsetSerializers(data=request.data)   
            if not serializer.is_valid():
                return serializerError(serializer.errors)    
            
            serializer.save()
            return successfullyCreated(serializer.data)
            
        except Exception as e:
            return exception(e)
 
    def patch(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            if not request.user.is_privileged:
                return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            pk = self.kwargs['pk']
            
            batch_query = PayrollBatches.objects.filter(organization=user_organization.id, is_active=True)
            if not batch_query.exists():
                return errorMessage("No active batch exists")
            
            batch_obj = batch_query.get()
            if batch_obj.is_lock == True:
                return errorMessage('This batch is locked. It cannot get edited now')

            # checks if batch composition exists at that id or not
            query = PayrollBatchCompositions.objects.filter(id=pk, payroll_compositions_attribute__organization=user_organization.id)
            if not query.exists():
                return errorMessage('Payroll batch composition does not exists')
            if not query.filter(payroll_batch = batch_obj.id):
                return errorMessage('This batch is deactivated. Data cannot be modified')

            obj = query.get()
            
            # composition could not be deactivated from here
            if 'is_active' in request.data:
                if request.data['is_active'] == "False":
                    return errorMessage('You cannot deactivate the batch from here')
                
            # attributes percentage checks
            if 'attribute_percentage' in request.data:
                percentage = Decimal(request.data['attribute_percentage'])
                if not (percentage > Decimal(0.00) and percentage <= Decimal(100.00)):
                    return errorMessage("Percentage should be greater than 0 but less than equal to 100")

            serializer = UpdatePayrollBatchCompositionsViewsetSerializers(obj, data=request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)    
            serializer.save()
            return successfullyCreated(serializer.data)

        except Exception as e:
            return exception(e)
        
    def patch_taxable(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            if not request.user.is_privileged:
                return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            pk = self.kwargs['pk']
            is_Taxable = request.data.get('is_Taxable')
            payroll_batch = request.data.get('payroll_batch')
            
            batch_query = PayrollBatches.objects.filter(id=payroll_batch, organization=user_organization.id, is_active=True)
            obj = batch_query.get()
            if not obj:
                return errorMessage("No active batch exists")
            elif obj.is_lock == True:
                return errorMessage("This batch is already locked")
            
            query = PayrollBatchAttributes.objects.filter(id = pk, is_active= True)
            if not query.exists():
                return errorMessage('No attribute agianst this id exist')
            obj = query.get()
            
            obj.is_Taxable = is_Taxable
            obj.created_by = request.user
            obj.save()
            return successMessage('Attribute in current batch updated succesfully')
            
        except Exception as e:
            return exception(e)
            

    def delete(self, request, *args, **kwargs):
        try: 
            user_organization = request.data.get('organization_profile')
            if not request.user.is_privileged:
                return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            pk = self.kwargs['pk']
            payroll_batch = None
            
            
            query = PayrollBatchCompositions.objects.filter(id=pk, payroll_compositions_attribute__organization=user_organization.id)
            if not query.exists():
                return errorMessage('Payroll batch composition does not exists')
            else :
              obj = query.get()
              payroll_batch = obj.payroll_batch
              print(payroll_batch)
              if payroll_batch is None:
                  return errorMessage("Create a new batch first")
              if payroll_batch.is_lock == True:
                return errorMessage("This batch is locked. So payroll composition cannot get deactivated")
                 
              if not query.filter(is_active=True):
                return errorMessage("Payroll composition is already deactivated")
              elif not query.filter(payroll_batch = payroll_batch):
                return errorMessage('This batch is deactivated. Data cannot be modified')
              obj.is_active=False
              obj.save()
            return successMessage('Successfully deactivated')
        except Exception as e:
            return exception(e)
        
    def lockPayrollComposition(self, request, *args, **kwargs):
        try: 
            user_organization = request.data.get('organization_profile')
            payroll_batch = request.data.get('payroll_batch')

            attribute_query = CompositionAttributes.objects.filter(organization=user_organization.id, is_active=True)
            composition_query = PayrollBatchCompositions.objects.filter(payroll_batch=payroll_batch,payroll_compositions_attribute__organization=user_organization.id, is_active=True)

            # check if active batch exists and if batch is locked or not
            batch_query = PayrollBatches.objects.filter(id=payroll_batch,organization=user_organization.id, is_active=True)
            
            batch_obj = batch_query.get()
            if batch_obj is None:
                return errorMessage("No active batch exists")
            elif batch_obj.is_lock==True:
                return errorMessage("This batch is already locked")
            
            if attribute_query.count() != composition_query.count():
                return errorMessage('You did not entered all the attributes')

            aggregate_percentage = 0
            for obj in composition_query:
                aggregate_percentage += obj.attribute_percentage

            if aggregate_percentage > 100:
                return errorMessage("Total percentage is greater than 100. Kindly! adjust the percentage to exactly 100")
            elif aggregate_percentage < 100:
                return errorMessage("Total percentage is less than 100. Kindly! adjust the percentage to exactly 100")
            
            # Batch is locked
            
            batch_obj.batch_status = 'lock'
            batch_obj.is_lock = True
            batch_obj.lock_by = request.user
            batch_obj.end_date = datetime.date.today()
            batch_obj.save()

            return successMessage("This batch composition is successfully submitted")

        except Exception as e:
            return exception(e)
        
    def unlockPayrollComposition(self, request, *args, **kwargs):
        try: 
            user_organization = request.data.get('organization_profile')
            payroll_batch = request.data.get('payroll_batch')

            salary_query = SalaryBatch.objects.filter(payroll_batch=payroll_batch,organization=user_organization.id, is_active=True, batch_status='in-progress', is_lock=True)
            
            if salary_query.exists():
                return errorMessage('Cannot unlock batch as one or more active salary batches exist.')

            # check if active batch exists and if batch is locked or not
            batch_query = PayrollBatches.objects.filter(id=payroll_batch,organization=user_organization.id, is_active=True)
            
            batch_obj = batch_query.get()
            if batch_obj is None:
                return errorMessage("No active batch exists")
            
            # Batch is locked
            
            batch_obj.batch_status = 'unlock'
            batch_obj.is_lock = False
            batch_obj.lock_by = request.user
            batch_obj.is_active = False
            batch_obj.end_date = datetime.date.today()
            batch_obj.save()

            return successMessage("This batch composition is successfully submitted")

        except Exception as e:
            return exception(e)
    
    def listactivepayrollbatches(self, request, *args,**kwargs):
        try:
              user_organization = request.data.get('organization_profile')
              payroll_batch_query = PayrollBatches.objects.filter(organization=user_organization.id, is_active=True, is_lock=True)
              serializer = PayrollBatchesViewsetSerializers(payroll_batch_query, many=True)
              return successMessageWithData('success', serializer.data)
        except Exception as e:
            return exception(e)
        

class PrePayrollCompositionDataView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def get(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            data = {'attributes': None, 'batch': None, 'composition': None}
            
            attributes = CompositionAttributes.objects.filter(organization=user_organization.id, is_active=True)
            attributes_serializer = PayrollAttributesViewsetSerializers(attributes, many=True)
            data['attributes'] = attributes_serializer.data
            batch = PayrollBatches.objects.filter(organization=user_organization.id, is_active=True)
            # sending single batch
            # if batch.exists():
            #     obj = batch.get()
            #     batch_serializer = PayrollBatchesViewsetSerializers(obj, many=False)
            #     data['batch'] = batch_serializer.data
                
            # sending multiple data
            if batch.exists():
                objs = batch.all()  # Get all instances in the queryset
                batch_serializer = PayrollBatchesViewsetSerializers(objs, many=True)
                data['batch'] = batch_serializer.data

            composition = PayrollBatchCompositions.objects.filter(payroll_compositions_attribute__organization=user_organization.id, is_active=True)
            composition_serializer = PayrollBatchCompositionsViewsetSerializers(composition, many=True)
            data['composition'] = composition_serializer.data

            return success(data)
        except Exception as e:
            return exception(e)


# Class to view emoloyee payroll configuration

class EmployeePayrollConfigurationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]
    def get(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            data = EmployeePayrollConfiguration.objects.filter(organization=user_organization.id, is_active=True)

            return success(data)
        except Exception as e:
            # print(exception(e))
            return exception(e)
        
    def create(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class EmployeePayrollConfigurationCreateView(viewsets.ModelViewSet):
    queryset = EmployeePayrollConfiguration.objects.all()
    serializer_class = EmployeePayrollConfigurationSerializer    
   
    def create(self, request, *args, **kwargs):
     try:
        # Decode the token to get organization_id
        organization_id = decodeToken(request, self.request)['organization_id']
        
        
        # Convert values to their appropriate types
        employee_id = int(request.data['employee'])
        is_salary_allowed = request.data.get('is_salary_allowed', None)  
        is_payslip_allowed = request.data.get('is_payslip_allowed', None)  
        is_active = request.data.get('is_active', True) 
        takeAway = request.data.get('takeAway', None)
        payroll_batch = request.data.get('payroll_batch', None)
        if not payroll_batch is None:
            try:
                 payroll_batch = PayrollBatches.objects.get(id=payroll_batch, organization=organization_id, is_active=True)
                 salary_batch = SalaryBatch.objects.filter(payroll_batch = payroll_batch.id, is_active=True, batch_status='in-progress', is_lock=True)
                 if salary_batch:
                     return errorMessage('Active salary batch exist. First complete that')
            except PayrollBatches.DoesNotExist:
                 return errorMessage('Invalid payroll_batch ID or payroll_batch is inactive')
        else :
            payroll_batch=None
        emp = Employees.objects.filter(organization=organization_id, id=employee_id, is_active=True).first()
        # Check if data for the given employee and organization already exists
        existing_data = EmployeePayrollConfiguration.objects.filter(
            organization=organization_id,
            employee=employee_id,
            is_active= True
        ).first()
        
        if existing_data:
           takeAway = existing_data.takeAway if takeAway is None else takeAway
           is_payslip_allowed = existing_data.is_payslip_allowed if is_payslip_allowed is None else is_payslip_allowed
           is_salary_allowed = existing_data.is_salary_allowed if is_salary_allowed is None else is_salary_allowed
           payroll_batch = existing_data.payroll_batch if payroll_batch is None else payroll_batch
            # Data already exists, update it
           serializer = self.get_serializer(existing_data, data={
                'organization': organization_id,
                'employee': employee_id,
                'is_salary_allowed': is_salary_allowed,
                'is_payslip_allowed': is_payslip_allowed,
                'is_active': is_active,
                'takeAway': takeAway,
                'payroll_batch': payroll_batch.id
            })
        
        else:
            # Data doesn't exist, create a new record
            serializer = self.get_serializer(data={
                'organization': organization_id,
                'employee': employee_id,
                'is_salary_allowed': is_salary_allowed,
                'is_payslip_allowed': is_payslip_allowed,
                'is_active': is_active,
                'takeAway': takeAway,
                'payroll_batch' : payroll_batch.id
            })
        # if takeAway is None:
        #     return errorMessage('takeAway is required')
        if serializer.is_valid():
            
            old_data = {
            'is_salary_allowed': existing_data.is_salary_allowed if existing_data else None,
            'is_payslip_allowed': existing_data.is_payslip_allowed if existing_data else None,
            'is_active': existing_data.is_active if existing_data else None,
            'takeAway': existing_data.takeAway if existing_data else None,
            'payroll_batch': existing_data.payroll_batch if existing_data else None
        }
            serializer.save()
            new_data = serializer.data
            change_log = EmployeePayrollConfigurationLog(
            action_by=request.user,
            employee=emp,
            is_salary_allowed_old=old_data.get('is_salary_allowed'),
            is_payslip_allowed_old=old_data.get('is_payslip_allowed'),
            is_active_old=old_data.get('is_active'),
            is_salary_allowed_new=new_data.get('is_salary_allowed'),
            is_payslip_allowed_new=new_data.get('is_payslip_allowed'),
            old_payroll_batch = old_data.get('payroll_batch'),
            new_payroll_batch = payroll_batch,
            is_active_new=new_data.get('is_active'),
            takeAway_old=old_data.get('takeAway'),
            takeAway_new=new_data.get('takeAway')
        )
            change_log.save()
        else: print(serializer.errors)      
        return successMessageWithData('success', serializer.data)

     except Exception as e:
        return exception(e)
    
    def list(self, request, *args, **kwargs):
     try:
        # Decode the token to get organization_id
        organization_id = decodeToken(request, self.request)['organization_id']

        # Get a list of all employees for the organization
        all_employees = Employees.objects.filter(organization=organization_id, is_active=True)

        # Initialize a list to store data for each employee
        employee_data_list = []

        # Get all employee payroll configurations for the organization
        employee_payroll_configs = EmployeePayrollConfiguration.objects.filter(
            organization=organization_id,
            is_active=True
        )

        # Create a dictionary to map employee IDs to their respective payroll configurations
        payroll_config_map = {config.employee_id: config for config in employee_payroll_configs}

        # Iterate through all employees and include their name, ID, email, and profile image (if available) in the response
        for employee in all_employees:
            # Get the corresponding payroll configuration if it exists
            employee_payroll_config = payroll_config_map.get(employee.id)

            # Include the employee's name, ID, email, and profile image (if available) in the response
            employee_data = {
                'employee_id': employee.id,
                'employee_name': employee.name,
                'employee':employee.id,
                'employee_email': employee.personal_email,
                'staff_classification': None,
                'employee_profile_image': None,  # Default to None
                'takeAway':None,
                'is_salary_allowed': None,
                'is_payslip_allowed': None,
                'is_active': None,
                'payroll_batch' : None
            }

            if employee_payroll_config:
                # Data exists for this employee, serialize it and update the response
                serializer = self.get_serializer(employee_payroll_config)
                employee_data.update(serializer.data)

            if employee.profile_image:  # Check if profile image exists
                employee_data['employee_profile_image'] = employee.profile_image.url
                
            if employee.staff_classification:
                employee_data['staff_classification'] = employee.staff_classification.title

            employee_data_list.append(employee_data)

        return successMessageWithData('success', employee_data_list)

     except Exception as e:
        return exception(e)


class PayrollAddonAttributesView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]
    queryset = PayrollAttributes.objects.all()
    serializer_class = PayrollAttributesSerializer
    
    def list(self, request, *args, **kwargs):
        try:
            # Decode the token to get organization_id
            organization_id = decodeToken(request, self.request)['organization_id']

            # Filter the queryset to retrieve data related to the organization
            queryset = self.get_queryset().filter(organization=organization_id, is_active= True,payroll_type = 'Addon', is_customized=False)

            serializer = self.serializer_class(queryset, many=True)

            return successMessageWithData('success', serializer.data)

        except Exception as e:
            return exception(e)    
    def deductionlist(self, request, *args, **kwargs):
        try:
            # Decode the token to get organization_id
            organization_id = decodeToken(request, self.request)['organization_id']

            # Filter the queryset to retrieve data related to the organization
            queryset = self.get_queryset().filter(organization=organization_id, is_active= True,payroll_type = 'Deduction', is_customized=False)

            serializer = self.serializer_class(queryset, many=True)

            return successMessageWithData('success', serializer.data)

        except Exception as e:
            return exception(e)    
   
    def create(self, request, *args, **kwargs):
     try:
        organization_id = decodeToken(request, self.request)['organization_id']
        request.data['organization']=organization_id
        user_id = request.user.id
        request.data['created_by'] = user_id
        if not request.user.is_privileged:
            return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
        title = request.data.get('title')
        payroll_type = request.data.get('payroll_type', 'Addon')
        if PayrollAttributes.objects.filter(title=title, is_active=True, payroll_type=payroll_type, organization=organization_id).exists():
                return errorMessage("A record with this title already exists.")
        
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            
            serializer.save()
            
        else: print("invalid")      
        return successMessageWithData('success', serializer.data)

     except Exception as e:
        return exception(e)
    
    
    def patch(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            user_id = request.user
            if not request.user.is_privileged:
                return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            pk = self.kwargs['pk']
            title = request.data.get('title', None)
            payroll_type = request.data.get('payroll_type', 'Addon')
            valuetype = request.data.get('valueType')
            
            attribute_query = PayrollAttributes.objects.filter(id=pk,organization=user_organization, is_active=True)
            if not attribute_query.exists():
                return errorMessage("No active attribute exists")
            
            if title and PayrollAttributes.objects.filter(title=title, is_active=True, payroll_type=payroll_type, organization = user_organization).exclude(id=pk).exists():
                return errorMessage("A record with this title already exists.")
            
            valuetype = valueTypeChoices.objects.get(id=request.data.get('valueType'), is_active=True,organization = user_organization)
            
            attribute_obj = attribute_query.get()
            
            

            query = PayrollBatchAttributes.objects.filter(payroll_attribute__id=pk, payroll_attribute__organization=user_organization.id, is_active=True, payroll_batch__is_lock =True)
            if query.exists():
                return errorMessage('Cannot modify the Attribute. Attribute exists in the batch.')

            attribute_obj = attribute_query.get()
            
            # composition could not be deactivated from here
            if 'is_active' in request.data:
                if request.data['is_active'] == "False":
                    return errorMessage('You cannot deactivate the attribute from here')
                
            attribute_obj.is_active=False
            attribute_obj.save()
            attribute_data = model_to_dict(attribute_obj, exclude=['id', 'organization','is_active','created_by', 'valueType'])
            updated_attribute_obj = PayrollAttributes.objects.create(
                created_by = user_id,
                organization=user_organization,
                **attribute_data,
                valueType = valuetype,
                is_active=True
                 
            )

            serializer = PayrollAttributesSerializer(updated_attribute_obj, data=request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)    
            serializer.save()
            return successfullyCreated(serializer.data)

        except Exception as e:
            return exception(e)

    def delete(self, request, *args, **kwargs):
        try: 
            user_organization = request.data.get('organization_profile')
            if not request.user.is_privileged:
                return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            pk = self.kwargs['pk']
            
            # checks if batch exists or not
            attribute_query = PayrollAttributes.objects.filter(id=pk,organization=user_organization.id, is_active=True)
            if not attribute_query.exists():
                return errorMessage("No attribute exist against this id")


            query = PayrollBatchAttributes.objects.filter(payroll_attribute__id=pk, payroll_attribute__organization=user_organization.id,payroll_batch__is_lock=True, is_active=True)
            if query.exists():
                return errorMessage('Attribute exists in the batch')
            else :
             obj = attribute_query.get()
             obj.is_active=False
             obj.save()
            return successMessage('Successfully deleted')
        except Exception as e:
            return exception(e)
        
class MonthlydistributionView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]
    queryset = MonthlyDistribution.objects.all()
    serializer_class = MonthlyDistributionSerializer
    
    
    def create(self, request, *args, **kwargs):
     try:
        user_organization = request.data.get('organization_profile')
        organization_id = decodeToken(request, self.request)['organization_id']
        
        request.data['organization']=organization_id
        user_id = request.user.id
        request.data['created_by'] = user_id
        payroll_attribute = request.data.get('payroll_attribute')
        payroll_batch = request.data.get('payroll_batch')
        if not payroll_attribute:
                return errorMessage('Payroll Attribute is the required field')
        if not payroll_batch:
                return errorMessage('Payroll Batch is the required field')
        
        attribute_query = PayrollAttributes.objects.filter(id=payroll_attribute,organization=organization_id, is_active=True)
        
        if not attribute_query.exists():
                return errorMessage("Attribute does not exists")
        elif not attribute_query.filter(is_active=True).exists():
                return errorMessage("Attribute is deactivated")
        staff_classification_id = request.data.get('staff_classification', None)
        if not staff_classification_id:
                return errorMessage('Staff classification is the required field')    
        staff_classification = StaffClassification.objects.filter(id= staff_classification_id, organization=organization_id)
        if not staff_classification.exists():
                return errorMessage("Staff classification does not exists")
        elif not staff_classification.filter(is_active=True).exists():
                return errorMessage("staff classification is deactivated")
        request.data['staff_classification'] = staff_classification_id
        
        existing_data = MonthlyDistribution.objects.filter(payroll_batch=payroll_batch,payroll_attribute=payroll_attribute,staff_classification= staff_classification_id, organization=organization_id,is_active= True).first()
        
        if not existing_data:
         serializer = self.serializer_class(data=request.data)
        elif existing_data:
            exs_obj = existing_data
            exs_obj.is_active=False
            exs_obj.save()
            attribute_data = model_to_dict(exs_obj, exclude=['id', 'organization','is_active','created_by','payroll_attribute','payroll_batch'])
            updated_obj = MonthlyDistribution.objects.create(
                created_by = user_id,
                organization= user_organization,
                **attribute_data,
                is_active=True 
            )
            serializer = self.serializer_class(updated_obj, data=request.data, partial=True)
         
        if serializer.is_valid():
            serializer.save()
            
        else: print("invalid")      
        return successMessageWithData('success', serializer.data)

     except Exception as e:
        return exception(e)
    
    def patch(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            user_id = request.user
            pk = self.kwargs['pk']
            payroll_attribute_id = request.data.get('payroll_attribute')
            payroll_batch = request.data.get('payroll_batch')
            sc = request.data.get('staff_classification')
            salary_batch = SalaryBatch.objects.filter(payroll_batch=payroll_batch, organization = user_organization.id, is_active=True, is_lock=True, batch_status='in-progress')
            if salary_batch.exists():
                return errorMessage('Active Salary Batch Exist First unlock or complete that batch')
            payroll_batch_data = PayrollBatches.objects.get(id=payroll_batch, organization = user_organization.id, is_active=True)
            payroll_data = PayrollAttributes.objects.filter(id=payroll_attribute_id,organization=user_organization, is_active=True).first()
            scdata = StaffClassification.objects.filter(id= sc, organization=user_organization).first()
            attribute_query = MonthlyDistribution.objects.filter(id=pk,payroll_batch=payroll_batch,organization=user_organization, is_active=True)
            if not attribute_query.exists():
                return errorMessage("No active data exists")
            exs_obj = attribute_query.get()

                
            exs_obj.is_active=False
            exs_obj.save()
            attribute_data = model_to_dict(exs_obj, exclude=['id', 'organization','is_active','payroll_attribute','staff_classification','payroll_batch'])
            updated_obj = MonthlyDistribution.objects.create(
                organization= user_organization,
                **attribute_data,
                is_active=True,
                payroll_attribute = payroll_data,
                payroll_batch = payroll_batch_data,
                staff_classification = scdata
            )
            serializer = self.serializer_class(updated_obj, data=request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors) 
            serializer.save()
            return successfullyCreated(serializer.data)

        except Exception as e:
            return exception(e)

    
    def list(self, request, *args, **kwargs):
        try:
            # Decode the token to get organization_id
            # organization_id = decodeToken(request, self.request)['organization_id']
            user_organization = request.data.get('organization_profile')
            user_id = request.user
            payroll_attribute = request.data.get('payroll_attribute')
            payroll_batch = request.data.get('payroll_batch')
            
            all_staff = StaffClassification.objects.filter(organization = user_organization.id,is_active=True)
            
            payroll_attribute = PayrollAttributes(id=payroll_attribute, is_active=True)
            payroll_batch = PayrollBatches(id=payroll_batch, is_active=True)
            

            # Filter the queryset to retrieve data related to the organization
            queryset = self.get_queryset().filter(payroll_batch=payroll_batch,payroll_attribute=payroll_attribute,organization=user_organization.id, is_active= True)
            
            for staff in all_staff:
             if not queryset.filter(staff_classification=staff).exists():
               MonthlyDistribution.objects.create(
               organization=user_organization,
               payroll_attribute=payroll_attribute,
               payroll_batch=payroll_batch,
               staff_classification=staff,
               amount=0,
               is_active=True,
        )

            serializer = self.serializer_class(queryset, many=True)

            return successMessageWithData('success', serializer.data)

        except Exception as e:
            return exception(e)  
    
    def delete(self, request, *args, **kwargs):
        try: 
            user_organization = request.data.get('organization_profile')
            pk = self.kwargs['pk']
            
            # checks if batch exists or not
            distribution_query = MonthlyDistribution.objects.filter(id=pk,organization=user_organization.id, is_active=True)
            if not distribution_query.exists():
                return errorMessage("No data exist against this id")


            obj = distribution_query.get()
            obj.is_active=False
            obj.save()
            return successMessage('Successfully deleted')
        except Exception as e:
            return exception(e)   
    
class EligibleEmployeesView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]
    queryset = EligibleEmployees.objects.all()
    serializer_class = EligibleEmployeesSerializer
    
    def payrollbatchemployees(self, request, *args, **kwars):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            payroll_batch = request.data.get('payroll_batch')
            employees_payroll_configurations = EmployeePayrollConfiguration.objects.filter(payroll_batch=payroll_batch, is_active=True)

            employee_ids = employees_payroll_configurations.values_list('employee', flat=True)
            employees = Employees.objects.filter(id__in=employee_ids, is_active=True, organization = organization_id)

            # Serialize the employee data using EmployeeViewsetSerializers
            employee_serializer = ListEmployeeViewsetSerializers(employees, many=True)
            serialized_data = employee_serializer.data

            return successMessageWithData('success', serialized_data)
        except Exception as e:
            return exception(e)
    
    def view(self, request, *args, **kwargs):
     try:
        payroll_attribute_id = request.data.get('payroll_attribute')
        payroll_batch = request.data.get('payroll_batch')
        eligibleemployees = EligibleEmployees.objects.filter(payroll_batch=payroll_batch,payroll_attribute=payroll_attribute_id, is_active=True)
        serializer = EligibleEmployeesSerializer(eligibleemployees, many =True)
        return successMessageWithData('success', serializer.data)
     except Exception as e:
            return exception(e)   

    def create(self, request, *args, **kwargs):
     try:
        organization_id = decodeToken(request, self.request)['organization_id']
        request.data['organization'] = organization_id
        user_id = request.user.id
        request.data['created_by'] = user_id
        payroll_attribute_id = request.data.get('payroll_attribute')
        payroll_batch = request.data.get('payroll_batch')
        try:
              payroll_batch = PayrollBatches.objects.get(id=payroll_batch, organization=organization_id, is_active=True)
        except PayrollBatches.DoesNotExist:
            return errorMessage("Batch does not exist")
        
        try:
            payroll_attribute = PayrollAttributes.objects.get(id=payroll_attribute_id, organization=organization_id, is_active=True)
        except PayrollAttributes.DoesNotExist:
            return errorMessage("Attribute does not exist")
        
        salary_batch = SalaryBatch.objects.filter(batch_status='in-progress',payroll_batch=payroll_batch, organization = organization_id, is_active=True,is_lock=True)
        print(salary_batch.values())
        for batch in salary_batch:
             print(f"Batch ID: {batch.id}, Batch Status: {batch.batch_status}")
        if salary_batch.exists():
                return errorMessage('Active Salary Batch Exist First unlock or complete that batch')
        
        with transaction.atomic():
            # Get a list of employee IDs to be added
            employees_to_add = request.data.get('employee')
            
            # Get a list of existing eligible employees for this payroll attribute
            existing_eligible_employees = EligibleEmployees.objects.filter(
                payroll_batch = payroll_batch.id,payroll_attribute=payroll_attribute, is_active=True
            )
            
            # Create a set of existing employee IDs for quick look-up
            existing_employee_ids = set(e.employee.id for e in existing_eligible_employees)
            
            # Create eligible employee records for new employees
            for employee_id in employees_to_add:
                if employee_id not in existing_employee_ids:
                    try:
                        employee = Employees.objects.get(id=employee_id)
                        EligibleEmployees.objects.create(employee=employee, payroll_attribute=payroll_attribute, payroll_batch=payroll_batch, is_active=True)
                    except Employees.DoesNotExist:
                        continue
            
            # Remove employees that are no longer eligible
            for eligible_employee in existing_eligible_employees:
                if eligible_employee.employee.id not in employees_to_add:
                    eligible_employee.is_active = False
                    eligible_employee.save()

            eligible_employees = EligibleEmployees.objects.filter(payroll_batch=payroll_batch.id,payroll_attribute=payroll_attribute, is_active=True)
            serializer = EligibleEmployeesSerializer(eligible_employees, many=True)
            
        return successMessageWithData('Success', serializer.data)
     except Exception as e:
        return exception(e)
    
    
    
class FixedDistributionView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]
    queryset = FixedDistribution.objects.all()
    serializer_class = FixedDistributionSerializer
        
    # def create(self, request, *args, **kwargs):
    #  try:
    #     user_organization = request.data.get('organization_profile')
    #     user_id = request.user.id
    #     # request.data['organization'] = user_organization
    #     request.data['created_by'] = user_id
    #     payroll_attribute_id = request.data.get('payroll_attribute')
    #     payroll_batch_id = request.data.get('payroll_batch')
        
    #         # Make sure you get the PayrollAttribute instance
    #     payroll_attribute = PayrollAttributes.objects.get(id=payroll_attribute_id,organization=user_organization.id, is_active=True)
    #     payroll_batch = PayrollBatches.objects.get(id=payroll_batch_id,organization=user_organization.id, is_active=True)
    #     payroll_batch_attribute= PayrollBatchAttributes.objects.get(payroll_batch=payroll_batch_id, payroll_attribute= payroll_attribute_id, is_active=True)
    #     try:
    #         fixeddistribution = FixedDistribution.objects.get(
    #             payroll_batch= payroll_batch_id,
    #             payroll_attribute=payroll_attribute,
    #             organization=user_organization.id,
    #             is_active=True
    #         )
    #     except FixedDistribution.DoesNotExist:
    #         fixeddistribution = None

    #     if fixeddistribution:
    #         fixeddistribution.is_active = False
    #         fixeddistribution.save()
    #     request.data.pop('payroll_attribute', None)
    #     request.data.pop('organization_profile',None)
    #     request.data.pop('created_by',None)
    #     request.data.pop('payroll_batch',None)
    #     new_fixeddistribution = FixedDistribution.objects.create(
    #         organization=user_organization,
    #         is_active=True,
    #         payroll_attribute=payroll_attribute,
    #         payroll_batch=payroll_batch,
    #         **request.data
    #     )

    #     # Update the amount of the new FixedDistribution
    #     new_fixeddistribution.amount = request.data.get('amount')
    #     new_fixeddistribution.save()
        
    #     payroll_batch_attribute.is_processed=True
    #     payroll_batch_attribute.save()

    #     serializer = FixedDistributionSerializer(new_fixeddistribution, many=False)

    #     return successMessageWithData('success', serializer.data)
    #  except Exception as e:
    #     return exception(e)
    
    def create(self, request, *args, **kwargs):
     try:
        user_organization = request.data.get('organization_profile')
        request.data['organization']=user_organization.id
        user_id = request.user.id
        request.data['created_by'] = user_id
        payroll_attribute_id = request.data.get('payroll_attribute')
        # salary_batch = request.data.get('salary_batch')
        payroll_batch = request.data.get('payroll_batch')
        employee=request.data.get('employee')
        batch_query = PayrollBatches.objects.filter(id=payroll_batch,organization=user_organization.id, is_active=True)       
        if not batch_query.exists():
                return errorMessage("No active batch exists")
        # elif batch_query.filter(is_lock=True):
        #         return errorMessage("This batch is locked you cannot add value to this.")
        
        try:
            # Make sure you get the PayrollAttribute instance
            payroll_attribute = PayrollAttributes.objects.get(id=payroll_attribute_id, organization=user_organization.id, is_active=True)
        except PayrollAttributes.DoesNotExist:
            return errorMessage("Attribute does not exist")
        
        try:
            fixed_distribution = FixedDistribution.objects.get(
                payroll_attribute=payroll_attribute,
                payroll_batch=payroll_batch,
                payroll_batch__organization=user_organization.id,
                is_active=True,
            )
        except FixedDistribution.DoesNotExist:
            fixed_distribution = None

        if fixed_distribution is None:
            serializer = FixedDistributionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return successMessageWithData('success', serializer.data)
            else:
                return serializerError(serializer.errors)
        else:
            return errorMessage('Amount already set against this attribute')
            
     except Exception as e:
        return exception(e)

    def view(self, request, *args, **kwargs):
        try :
         organization_id = decodeToken(request, self.request)['organization_id']
         request.data['organization'] = organization_id
         payroll_attribute_id = request.data.get('payroll_attribute')
        #  salary_batch = request.data.get('salary_batch')
         payroll_batch = request.data.get('payroll_batch')
         try:
          fixedistribution = FixedDistribution.objects.get(payroll_batch=payroll_batch,payroll_attribute=payroll_attribute_id, organization=organization_id, is_active=True)
         except FixedDistribution.DoesNotExist:
            return errorMessage("Amount does not exist")
        
         serializer = FixedDistributionSerializer(fixedistribution, many=False)
         return successMessageWithData('success', serializer.data)

        except Exception as e:
            return exception(e)
        
        
class VariableDistributionsView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]
    queryset = VariableDistributions.objects.all()
    serializer_class = VariableDistributionsSerializer
    
    def create(self, request, *args, **kwargs):
     try:
        user_organization = request.data.get('organization_profile')
        user_id = request.user.id
        request.data['created_by'] = user_id
        payroll_attribute_id = request.data.get('payroll_attribute')
        salary_batch = request.data.get('salary_batch')
        employee=request.data.get('employee')
        
        batch_query = SalaryBatch.objects.filter(id=salary_batch,organization=user_organization.id, is_active=True)       
        if not batch_query.exists():
                return errorMessage("No active batch exists")
        elif batch_query.filter(is_lock=True):
                return errorMessage("This batch is locked you cannot add value to this.")
        
        try:
            # Make sure you get the PayrollAttribute instance
            payroll_attribute = PayrollAttributes.objects.get(id=payroll_attribute_id, organization=user_organization.id, is_active=True)
        except PayrollAttributes.DoesNotExist:
            return errorMessage("Attribute does not exist")
        
        try:
            variable_distributions = VariableDistributions.objects.get(
                payroll_attribute=payroll_attribute,
                salary_batch=salary_batch,
                salary_batch__organization=user_organization.id,
                is_active=True,
                employee=employee
            )
        except VariableDistributions.DoesNotExist:
            variable_distributions = None

        if variable_distributions is None:
            serializer = VariableDistributionsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return successMessageWithData('success', serializer.data)
            else:
                return serializerError(serializer.errors)
        else:
            return errorMessage('Employee Already Added')
            
     except Exception as e:
        return exception(e)

        
    # def create(self, request, *args, **kwargs):
    #  try:
    #     user_organization = request.data.get('organization_profile')
    #     user_id = request.user.id
    #     # request.data['organization'] = user_organization
    #     request.data['created_by'] = user_id
    #     payroll_attribute_id = request.data.get('payroll_attribute')
        
        
    #     try:
    #         # Make sure you get the PayrollAttribute instance
    #         payroll_attribute = PayrollAttributes.objects.get(id=payroll_attribute_id,organization=user_organization.id, is_active=True)
    #     except PayrollAttributes.DoesNotExist:
    #         return errorMessage("Attribute does not exist")

    #     # Try to get the existing FixedDistribution
    #     try:
    #         VariableDistributions = VariableDistributions.objects.get(
    #             payroll_attribute=payroll_attribute,
    #             organization=user_organization.id,
    #             is_active=True
    #         )
    #     except VariableDistributions.DoesNotExist:
    #         VariableDistributions = None

    #     if VariableDistributions:
    #         VariableDistributions.is_active = False
    #         VariableDistributions.save()
    #     request.data.pop('payroll_attribute', None)
    #     request.data.pop('organization_profile',None)
    #     request.data.pop('created_by',None)
    #     new_VariableDistributions = VariableDistributions.objects.create(
    #         organization=user_organization,
    #         is_active=True,
    #         payroll_attribute=payroll_attribute,
    #         **request.data
    #     )

    #     # Update the amount of the new FixedDistribution
    #     new_VariableDistributions.amount = request.data.get('amount')
    #     new_VariableDistributions.save()

    #     serializer = VariableDistributionsSerializer(new_VariableDistributions, many=False)

    #     return successMessageWithData('success', serializer.data)
    #  except Exception as e:
    #     return exception(e)

    def view(self, request, *args, **kwargs):
        try :
         organization_id = decodeToken(request, self.request)['organization_id']
         request.data['organization'] = organization_id
         payroll_attribute_id = request.data.get('payroll_attribute')
         salary_batch_id= request.data.get('salary_batch')
         variabledistributions = VariableDistributions.objects.filter(salary_batch=salary_batch_id,payroll_attribute=payroll_attribute_id, salary_batch__organization=organization_id, is_active=True)
         print(variabledistributions.values())
        #  serializer = EligibleEmployeesSerializer(eligibleemployees, many =True)
         serializer = VariableDistributionsSerializer(variabledistributions, many=True)
         return successMessageWithData('success', serializer.data)

        except Exception as e:
            return exception(e)
        
class CustomizedAttribuesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated , IsAdminOnly,  DoesOrgExists]
    queryset = PayrollAttributes.objects.all()
    serializer_class = PayrollAttributesSerializer
    customised_queryset = customisedAttributes.objects.all()
    serializer_customized = customisedAttributesSerializer
    
    def list(self, request, *args, **kwargs):
        try :
         organization_id = decodeToken(request, self.request)['organization_id']
         request.data['organization'] = organization_id
         customizedpayrollattributes = PayrollAttributes.objects.filter(organization=organization_id,is_customized=True, is_active=True)
         if customizedpayrollattributes.exists():
          serializer = PayrollAttributesSerializer(customizedpayrollattributes, many=True)  # Use many=True to serialize all results
          return successMessageWithData('success', serializer.data)
         else:
          return successMessage("No data exist")
        except Exception as e:
            return exception(e)
        
    def destroy(self, request, *args, **kwargs):  
        try: 
            user_organization = request.data.get('organization_profile')
            if not request.user.is_privileged:
                return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            pk = self.kwargs['pk']
            
            # checks if batch exists or not
            customized_query = PayrollAttributes.objects.filter(id=pk,organization=user_organization.id, is_active=True)
            if not customized_query.exists():
                return errorMessage("No data exist against this id")


            obj = customized_query.get()
            obj.is_active=False
            obj.save()
            return successMessage('Successfully deleted')
        except Exception as e:
            return exception(e) 
        
    def create(self, request, *args, **kwargs):
        # try:
        #     organization_id = decodeToken(request, self.request)['organization_id']
        #     request.data['organization'] = organization_id   
        #     request.data['created_by'] =request.user.id
        #     serializer = PayrollAttributesSerializer(data=request.data)
        #     # payrollattributesserializer = PayrollAttributesSerializer(data=request.data)
        #     if serializer.is_valid():
        #         serializer.save()
        #         return successMessageWithData('success', serializer.data)
            
        #     return serializerError(serializer.errors)

        # except Exception as e:
        #     return exception(e)
        
     try:
        organization_id = decodeToken(request, self.request)['organization_id']
        request.data['organization']=organization_id
        user_id = request.user.id
        request.data['created_by'] = user_id
        if not request.user.is_privileged:
            return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
        title = request.data.get('title')
        payroll_type = request.data.get('payroll_type', 'Addon')
        if PayrollAttributes.objects.filter(title=title, is_active=True, payroll_type=payroll_type, organization = organization_id).exists():
                return errorMessage("A record with this title already exists.")
        
        is_customized = request.data['is_customized']
        if is_customized==True:
         customised_serializer = customisedAttributesSerializer(data={'title': title})

         if customised_serializer.is_valid():
          customised_serializer.save()
          customised_id = customised_serializer.instance.id  
          request.data['customized_id'] = customised_id
        
         serializer = self.serializer_class(data=request.data)
        
         if serializer.is_valid():
            
            serializer.save()
            
        else: return errorMessage('Customised Attribute cannot be added')     
        return successMessageWithData('success', serializer.data)

     except Exception as e:
        return exception(e)
        
        
        
    def update(self, request, *args, **kwargs):
        try:
            if not request.user.is_privileged:
                return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            instance = self.get_object()
            serializer = PayrollAttributesSerializer(instance, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return successMessageWithData('Successfully updated',serializer.data)
            
            return errorMessageWithData('Error', serializer.errors)
        
        except Exception as e:
            return exception(e)
        
        
        
class ValueTypeChoicesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated , IsAdminOnly,  DoesOrgExists]
    queryset = valueTypeChoices.objects.all()
    serializer_class = valueTypeChoicesSerializer
    
    def list(self, request, *args, **kwargs):
        try :
         organization_id = decodeToken(request, self.request)['organization_id']
         request.data['organization'] = organization_id
         valueTypes = valueTypeChoices.objects.filter(organization=organization_id, is_active=True)
         serializer = valueTypeChoicesSerializer(valueTypes, many=True)  # Use many=True to serialize all results
         return successMessageWithData("sucsess", serializer.data)
        except Exception as e:
            return exception(e)
        
    def destroy(self, request, *args, **kwargs):  
        try: 
            user_organization = request.data.get('organization_profile')
            if not request.user.is_privileged:
                return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            pk = self.kwargs['pk']
            
            # checks if batch exists or not
            customized_query = valueTypeChoices.objects.filter(id=pk,organization=user_organization.id, is_active=True)
            if not customized_query.exists():
                return errorMessage("No data exist against this id")


            obj = customized_query.get()
            obj.is_active=False
            obj.save()
            return successMessage('Successfully deleted')
        except Exception as e:
            return exception(e) 
        
    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            request.data['organization'] = organization_id   
            request.data['created_by'] =request.user.id
            if not request.user.is_privileged:
                return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            serializer = valueTypeChoicesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return successMessageWithData('sucess', serializer.data)
            
            return serializerError(serializer.errors)

        except Exception as e:
            return exception(e)


class PayrollBatchAttributesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated , IsAdminOnly,  DoesOrgExists]
    queryset = PayrollBatchAttributes.objects.all()
    serializer_class = PayrollBatchAttributesSerializer
    
    def create(self, request, *args, **kwargs):
     try:
        organization_id = decodeToken(request, self.request)['organization_id']
        request.data['organization'] = organization_id
        user_id = request.user.id
        request.data['created_by'] = user_id
        if not request.user.is_privileged:
            return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
        payroll_attributes = request.data.get('payroll_attribute', [])
        payroll_batch = request.data.get('payroll_batch')
        
        batch_query = PayrollBatches.objects.filter(organization=organization_id, is_active=True, id=payroll_batch)
            
        if not batch_query.exists():
                return errorMessage("No active batch exists")
        elif batch_query.filter(is_lock=True):
                return errorMessage("This batch is locked")

        # Fetch existing attributes for the specified payroll_batch
        existing_attributes = PayrollBatchAttributes.objects.filter(
            payroll_batch__organization=organization_id,
            payroll_batch=payroll_batch,
            is_active = True
        )

        # Get a set of existing attributes that are also in the provided list
        existing_attributes_values = set(existing_attributes.values_list('payroll_attribute', flat=True))
        
        # Iterate through existing attributes and set is_active to False if not in the provided list
        for attribute in existing_attributes:
            if attribute.payroll_attribute.id not in payroll_attributes:
                attribute.is_active = False
                attribute.save()

        data_objects = []
        for attribute in payroll_attributes:
            if attribute not in existing_attributes_values:
                data_object = {
                    'created_by': user_id,
                    'payroll_attribute': attribute,
                    'payroll_batch': payroll_batch
                }
                data_objects.append(data_object)

        created_objects = []
        for data_object in data_objects:
            serializer = PayrollBatchAttributesSerializer(data=data_object)
            if serializer.is_valid():
                serializer.save()
                created_objects.append(serializer.data)
            else:
                return errorMessage(serializer.errors)

        return successMessageWithData('success', created_objects)
     except Exception as e:
        return exception(e)
    
    
    
    def list(self, request, *args, **kwargs):
     try:
        organization_id = decodeToken(request, self.request)['organization_id']
        request.data['organization'] = organization_id
        payroll_batch = request.data['payroll_batch']
        existing_attributes = PayrollBatchAttributes.objects.filter(
            payroll_batch__organization=organization_id,
            payroll_batch=payroll_batch,
            is_active = True,
            # payroll_attribute__payroll_type = 'Addon',
            # payroll_attribute__is_customized = False
        )
        serializer = PayrollBatchAttributesSerializer(existing_attributes, many=True)  
        return successMessageWithData('success',serializer.data)
     except Exception as e:
        return exception(e)
    
    
    
    def hrlist(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            request.data['organization'] = user_organization.id
            salary_batch = request.data.get('salary_batch')
            payroll_batch = request.data.get('payroll_batch')
            data = {'batch': None, 'salary':None}

            batch = PayrollBatches.objects.filter(id= payroll_batch, organization=user_organization.id,is_active=True,is_lock =True)
            if batch.exists():
                obj = batch.get()
                batch_serializer = PayrollBatchesViewsetSerializers(obj, many=False)
                data['batch'] = batch_serializer.data
            else :
                return errorMessage('No lock batch found')
            
            salary_batch = SalaryBatch.objects.filter(organization=user_organization.id,is_active=True, payroll_batch=data['batch']['id']).exclude(batch_status='transferred')
            if salary_batch.exists():
                salary_obj = salary_batch.get()
                salary_batch_serializer = PayrollBatchesViewsetSerializers(salary_obj, many=False)
                data['salary'] = salary_batch_serializer.data

            addon_criteria = {
                'payroll_batch__organization': user_organization.id,
                'payroll_batch': data['batch']['id'],
                'is_active': True,
                'payroll_attribute__payroll_type': 'Addon',
                'payroll_attribute__is_customized': False
            }

            deduction_criteria = {
                'payroll_batch__organization': user_organization.id,
                'payroll_batch': data['batch']['id'],
                'is_active': True,
                'payroll_attribute__payroll_type': 'Deduction',
                'payroll_attribute__is_customized': False
            }

            customized_criteria = {
                'payroll_batch__organization': user_organization.id,
                'payroll_batch': data['batch']['id'],
                'is_active': True,
                'payroll_attribute__is_customized': True
            }
            

            addon_data = PayrollBatchAttributes.objects.filter(**addon_criteria)
            deduction_data = PayrollBatchAttributes.objects.filter(**deduction_criteria)
            customized_data = PayrollBatchAttributes.objects.filter(**customized_criteria)
            addon_serializer = PayrollBatchAttributesSerializer(addon_data, many=True)
            deduction_serializer = PayrollBatchAttributesSerializer(deduction_data, many=True)
            customized_serializer = PayrollBatchAttributesSerializer(customized_data, many=True)
            
            
            response_data = {
                'Addon': addon_serializer.data,
                'Deduction': deduction_serializer.data,
                'Customized': customized_serializer.data,
                'predata': data
            }

           
            return successMessageWithData('success', response_data)
        except Exception as e:
            return exception(e)
    
    
    def salaryattributeslist(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            request.data['organization'] = user_organization.id
            salary_batch = request.data.get('salary_batch')
            payroll_batch = request.data.get('payroll_batch')
            data = {'batch': None, 'salary':None}

            batch = PayrollBatches.objects.filter(id=payroll_batch,organization=user_organization.id,is_active=True,is_lock =True)
            if batch.exists():
                obj = batch.get()
                batch_serializer = PayrollBatchesViewsetSerializers(obj, many=False)
                data['batch'] = batch_serializer.data
            else :
                return errorMessage('No lock batch found')
            
            salary_batch = SalaryBatch.objects.filter(organization=user_organization.id,is_active=True, payroll_batch=data['batch']['id']).exclude(batch_status='transferred')
            if salary_batch.exists():
                salary_obj = salary_batch.get()
                salary_batch_serializer = PayrollBatchesViewsetSerializers(salary_obj, many=False)
                data['salary'] = salary_batch_serializer.data

                addon_criteria = {
                    'is_active': True,
                    'salary_batch': data['salary']['id'],
                    'payroll_batch_attribute__payroll_attribute__payroll_type': 'Addon',
                    'payroll_batch_attribute__payroll_attribute__is_customized': False
                }

                deduction_criteria = {
                    'is_active': True,
                    'payroll_batch_attribute__payroll_attribute__payroll_type': 'Deduction',
                    'salary_batch': data['salary']['id'],
                    'payroll_batch_attribute__payroll_attribute__is_customized': False
                }

                customized_criteria = {
                    'is_active': True,
                    'salary_batch': data['salary']['id'],
                    'payroll_batch_attribute__payroll_attribute__is_customized': True
                }
                

                addon_data = SalaryBatchAttributes.objects.filter(**addon_criteria)
                deduction_data = SalaryBatchAttributes.objects.filter(**deduction_criteria)
                customized_data = SalaryBatchAttributes.objects.filter(**customized_criteria)
                addon_serializer = SalaryBatchAttributesSerializer(addon_data, many=True)
                deduction_serializer = SalaryBatchAttributesSerializer(deduction_data, many=True)
                customized_serializer = SalaryBatchAttributesSerializer(customized_data, many=True)
                
                
                response_data = {
                    'Addon': addon_serializer.data,
                    'Deduction': deduction_serializer.data,
                    'Customized': customized_serializer.data,
                    'predata': data
                }

            
                return successMessageWithData('success', response_data)
            else:
                return errorMessage('No active salary batch exist against this payroll batch')
        except Exception as e:
            return exception(e)


class EmployeesAllowanceList(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated , IsAdminOnly,  DoesOrgExists]

    def gymlist(self, request):
     try:
        user_organization = request.data.get('organization_profile')
        salary_batch = request.data.get('salary_batch')
        payroll_batch = request.data.get('payroll_batch')
        employees_payroll_configurations = EmployeePayrollConfiguration.objects.filter(payroll_batch=payroll_batch, is_active=True)

        employee_ids = employees_payroll_configurations.values_list('employee', flat=True)
        payroll_entry = PayrollCustomisedGymProcesses.objects.filter(salary_batch__organization = user_organization.id,salary_batch = salary_batch,is_active=True).get()
        queryset = EmployeesGymAllowance.objects.filter(employee__in=employee_ids,employee__organization= user_organization.id, is_active=True, status='approved', processed_status='processed-to-hr')

        serialized_data = EmployeesGymAllowanceSerializers(queryset, many=True).data

        response_data={
            'data': serialized_data,
            'total_amount': payroll_entry.amount,
            'data_processed' : payroll_entry.no_of_data
        }
        return successMessageWithData('success', response_data)
     except Exception as e:
            return exception(e)
     
        
    def medicallist(self, request):
     try:
        user_organization = request.data.get('organization_profile')
        salary_batch = request.data.get('salary_batch')
        payroll_batch = request.data.get('payroll_batch')
        employees_payroll_configurations = EmployeePayrollConfiguration.objects.filter(payroll_batch=payroll_batch, is_active=True)

        employee_ids = employees_payroll_configurations.values_list('employee', flat=True)
        
        payroll_entry = PayrollCustomisedMedicalProcesses.objects.filter(salary_batch__organization = user_organization.id,salary_batch = salary_batch,is_active=True).get()
        queryset = EmployeesMedicalAllowance.objects.filter(employee__in = employee_ids,employee__organization= user_organization.id, is_active=True,status='approved', processed_status='processed-to-hr')
        serialized_data = EmployeesMedicalAllowanceSerializers(queryset, many=True).data
        response_data={
            'data': serialized_data,
            'total_amount': payroll_entry.amount,
            'data_processed' : payroll_entry.no_of_data
        }
        return successMessageWithData('success', response_data)
     except Exception as e:
            return exception(e)
        
    def certifylist(self, request):
     try:
        user_organization = request.data.get('organization_profile')
        salary_batch = request.data.get('salary_batch')
        payroll_batch = request.data.get('payroll_batch')
        employees_payroll_configurations = EmployeePayrollConfiguration.objects.filter(payroll_batch=payroll_batch, is_active=True)

        employee_ids = employees_payroll_configurations.values_list('employee', flat=True)
        
        payroll_entry = PayrollCustomisedCertificationsProcesses.objects.filter(salary_batch__organization = user_organization.id,salary_batch = salary_batch,is_active=True).get()
        queryset = LNDCertifications.objects.filter(employee__in = employee_ids,employee__organization= user_organization.id, is_active=True,is_reimbursement=True, reimbursement_status=2)
        serialized_data = LNDCertificationsSerializers(queryset, many=True).data
        response_data={
            'data': serialized_data,
            'total_amount': payroll_entry.amount,
            'data_processed' : payroll_entry.no_of_data
        }
        return successMessageWithData('success', response_data)
     except Exception as e:
            return exception(e)
        
    def traininglist(self, request):
     try:
        user_organization = request.data.get('organization_profile')
        salary_batch = request.data.get('salary_batch')
        payroll_batch = request.data.get('payroll_batch')
        employees_payroll_configurations = EmployeePayrollConfiguration.objects.filter(payroll_batch=payroll_batch, is_active=True)

        employee_ids = employees_payroll_configurations.values_list('employee', flat=True)
        
        payroll_entry = PayrollCustomisedTrainingProcesses.objects.filter(salary_batch__organization = user_organization.id,salary_batch = salary_batch,is_active=True).get()
        queryset = TrainingEmployee.objects.filter(employee__in = employee_ids,employee__organization= user_organization.id, is_active=True,is_reimbursement=True, reimbursement_status=2)
        serialized_data = ListTrainingEmployeeSerializer(queryset, many=True).data
        response_data={
            'data': serialized_data,
            'total_amount': payroll_entry.amount,
            'data_processed' : payroll_entry.no_of_data
        }
        return successMessageWithData('success', response_data)
     except Exception as e:
            return exception(e)
        
    def pflist(self, request):
     try:
        user_organization = request.data.get('organization_profile')
        salary_batch = request.data.get('salary_batch')
        payroll_batch = request.data.get('payroll_batch')
        employees_payroll_configurations = EmployeePayrollConfiguration.objects.filter(payroll_batch=payroll_batch, is_active=True)

        employee_ids = employees_payroll_configurations.values_list('employee', flat=True)

        # Retrieve PF records for employees in the payroll batch
        queryset = PFRecords.objects.filter(employee__in=employee_ids, is_active=True, salary_batch=salary_batch, should_include=True)
        serialized_data = PFSerializer(queryset, many=True).data

        # Retrieve approved Provident Fund records for employees in the payroll batch
        approved_pf_records = EmployeeProvidentFunds.objects.filter(
            employee__in=employee_ids,
            employee__organization=user_organization.id,
            status='approved'
        )

        # Identify employees with approved PF but not present in PF records
        employees_not_in_pf = set(approved_pf_records.values_list('employee', flat=True)) - set(queryset.values_list('employee', flat=True))

        # Fetch details of employees with approved PF but not present in PF records
        employees_not_in_pf_details = Employees.objects.filter(id__in=employees_not_in_pf)

        # Serialize the details of employees with approved PF but not present in PF records
        serialized_employees_not_in_pf = ListEmployeeViewsetSerializers(employees_not_in_pf_details, many=True).data

        # Additional processing for payroll entry
        payroll_entry = PayrollCustomisedPFProcesses.objects.filter(salary_batch__organization=user_organization.id, salary_batch=salary_batch, is_active=True).get()

        response_data = {
            'data': serialized_data,
            'employees_not_in_pf': serialized_employees_not_in_pf,
            'total_amount': payroll_entry.amount,
            'data_processed': payroll_entry.no_of_data
        }

        return successMessageWithData('success', response_data)

     except Exception as e:
        return exception(e)
    
    def removefrompf(self, request, *args, **kwargs):
     try:
                pk = self.kwargs['pk']
                # Update PFRecords for the specified employee
                pf_record = PFRecords.objects.get(id=pk)
                pf_record.should_include = False
                pf_record.is_active = False
                salary_batch = pf_record.salary_batch
                salary_batch_record = SalaryBatch.objects.get(id=salary_batch.id, is_active=True)
                if salary_batch_record.is_lock==True:
                    return errorMessage('Salary batch is locked. You cannot change now')
                pf_amount  = pf_record.amount
                pf_process_query  = PayrollCustomisedPFProcesses.objects.get(salary_batch=salary_batch, is_active=True)
                amount = pf_process_query.amount - Decimal(pf_amount)
                no_of_data = pf_process_query.no_of_data - 1
                pf_process_query.amount = amount
                pf_process_query.no_of_data = no_of_data
                pf_process_query.save()
                pf_record.save()

                return successMessage('Employee removed from PF records successfully.')

     except Exception as e:
        return exception(e)
    
    def addtopf(self, request, *args, **kwargs):
         try:
            employee_id = request.data.get('employee_id')
            salary_batch_id = request.data.get('salary_batch')
            payroll_batch = request.data.get('payroll_batch')
            pf_amount=None
            payroll_composition = PayrollBatchCompositions.objects.filter(payroll_batch=payroll_batch, is_active=True)
            salary_batch = SalaryBatch.objects.get(id=salary_batch_id, is_active=True)
            if salary_batch.is_lock == True:
                return errorMessage('Salary batch is locked. You cannot change now.')
            pf_process_query  = PayrollCustomisedPFProcesses.objects.get(salary_batch=salary_batch_id, is_active=True)
            amount = pf_process_query.amount
            no_of_data = pf_process_query.no_of_data
            try:
                # Check if the employee has an active PF record for the given salary batch
                existing_pf_record = PFRecords.objects.get(employee=employee_id, should_include=True, salary_batch=salary_batch, is_active=True)
                return errorMessage('Employee is already in active PF records.')
            except PFRecords.DoesNotExist:
                # If the PF record doesn't exist, create a new one
                user_organization = request.data.get('organization_profile')
                percentagequery = ProvidentFunds.objects.get(organization=user_organization.id, is_active=True)
                percentage = percentagequery.percentage
                current_salary = Employees.objects.get(id=employee_id, organization=user_organization.id).current_salary
                
                basic_composition = next(
                    (composition for composition in payroll_composition if composition.payroll_compositions_attribute.title == 'Basic'),
                    None
                )
                if basic_composition:
                    basic_percentage = basic_composition.attribute_percentage
                    basic_salary = (current_salary * basic_percentage) / 100
                    # print(type(percentage))
                    pf_amount = (Decimal(percentage) / 100) * basic_salary
                    print(pf_amount)
                employee_instance = Employees.objects.get(id=employee_id)
                PFRecords.objects.create(
                    employee=employee_instance,
                    amount=pf_amount,
                    should_include=True,
                    created_by=request.user,
                    salary_batch=salary_batch
                )
                print(type(amount))
                amount = amount + Decimal(pf_amount)
                no_of_data = no_of_data + 1
                pf_process_query.amount = amount
                pf_process_query.no_of_data = no_of_data
                pf_process_query.save()

                return successMessage('Employee added to PF records successfully.')
         
         except Exception as e:
            return exception(e)
        
  
    def attributestobatch(self, request):
     try:
      user_organization = request.data.get('organization_profile')
      request.data['organization']=user_organization.id
      user_id = request.user.id
      request.data['created_by'] = user_id
      batch_ids = request.data.get('payroll_batch_attribute', [])
      payroll_batch = request.data.get('payroll_batch')
      salary_batch = request.data.get('salary_batch')
      payroll_composition = PayrollBatchCompositions.objects.filter(payroll_batch=payroll_batch, is_active=True)
      batch_query = SalaryBatch.objects.filter(id=salary_batch,organization=user_organization.id, is_active=True, payroll_batch = payroll_batch)       
      if not batch_query.exists():
                return errorMessage("No active batch exists")
      elif batch_query.filter(is_lock=True):
                return errorMessage("This batch is locked you cannot add attribute to this.")
      batch_obj=batch_query.get()
      request.data['salary_batch']=batch_obj.id
      for id in batch_ids:
       payroll_batch_query = PayrollBatchAttributes.objects.filter(id = id ,is_active=True)
       request.data['payroll_batch_attribute'] = id 
       payroll_batch_obj = payroll_batch_query.get()
       is_customized = payroll_batch_obj.payroll_attribute.is_customized
       process_name = payroll_batch_obj.payroll_attribute.title
       if is_customized:
        employees_payroll_configurations = EmployeePayrollConfiguration.objects.filter(payroll_batch=payroll_batch, is_active=True)

        employee_ids = employees_payroll_configurations.values_list('employee', flat=True)
        if re.search(r'\b\s*Gym\s*\b', process_name, re.IGNORECASE):
         PayrollCustomisedGymProcesses.objects.filter(salary_batch__organization=user_organization.id).update(is_active=False)
         queryset = EmployeesGymAllowance.objects.filter( employee__in=employee_ids,employee__organization=user_organization.id,
         status='approved'
         ).exclude(processed_status__in=[
         'processed-by-accountant',
         'processed-to-accountant',
    ])
         queryset.update(processed_status='processed-to-hr')
         total_amount = queryset.aggregate(total_amount=Sum('amount'))['total_amount']
         total_rows = queryset.aggregate(total_rows=Count('id'))['total_rows']
         request.data['amount'] = total_amount
         request.data['no_of_data'] = total_rows
         customisedgymserializer = PayrollCustomisedGymSerializer(data=request.data)
         serializer = SalaryBatchAttributeSerilaizer(data=request.data)
         if customisedgymserializer.is_valid() and serializer.is_valid():
                customisedgymserializer.save()
                serializer.save()
         else: return errorMessage(customisedgymserializer.errors)
             
        elif re.search(r'\b\s*Medical\s*\b', process_name, re.IGNORECASE):  
         PayrollCustomisedMedicalProcesses.objects.filter(salary_batch__organization=user_organization.id).update(is_active=False)
         queryset = EmployeesMedicalAllowance.objects.filter(
         employee__in=employee_ids,
         employee__organization=user_organization.id,
         status='approved'
         ).exclude(processed_status__in=[
         'processed-by-accountant',
         'processed-to-accountant',
        # 'processed-to-hr'
    ])
         queryset.update(processed_status='processed-to-hr')
         total_amount = queryset.aggregate(total_amount=Sum('amount'))['total_amount']
         total_rows = queryset.aggregate(total_rows=Count('id'))['total_rows']
         request.data['amount'] = total_amount
         request.data['no_of_data'] = total_rows
         customisedmedicalserializer = PayrollCustomisedMedicalSerializer(data=request.data)
         serializer = SalaryBatchAttributeSerilaizer(data=request.data)
         if customisedmedicalserializer.is_valid() and serializer.is_valid():
                customisedmedicalserializer.save()
                serializer.save()
         else: return errorMessage(customisedmedicalserializer.errors)
         
        elif re.search(r'\b\s*Certifications\s*\b', process_name, re.IGNORECASE):  
         PayrollCustomisedCertificationsProcesses.objects.filter(salary_batch__organization=user_organization.id).update(is_active=False)
         queryset = LNDCertifications.objects.filter(
         employee__in=employee_ids,
         employee__organization=user_organization.id,
         is_reimbursement=True
         ).exclude(reimbursement_status__in=[
         3,4
        # 'processed-to-hr'
    ])
         queryset.update(reimbursement_status=2)
         print(queryset)
         total_amount = queryset.aggregate(total_amount=Sum('cost'))['total_amount']
         total_rows = queryset.aggregate(total_rows=Count('id'))['total_rows']
         request.data['amount'] = total_amount
         request.data['no_of_data'] = total_rows
         customisedcertificationserializer = PayrollCustomisedCertificationSerializer(data=request.data)
         serializer = SalaryBatchAttributeSerilaizer(data=request.data)
         if customisedcertificationserializer.is_valid() and serializer.is_valid():
                customisedcertificationserializer.save()
                serializer.save()
         else: return errorMessage(customisedcertificationserializer.errors)
         
        elif re.search(r'\b\s*Training\s*\b', process_name, re.IGNORECASE):  
         PayrollCustomisedTrainingProcesses.objects.filter(salary_batch__organization=user_organization.id).update(is_active=False)
         queryset = TrainingEmployee.objects.filter(
         employee__in=employee_ids,
         employee__organization=user_organization.id,
         is_reimbursement=True
         ).exclude(reimbursement_status__in=[
         3,4
        # 'processed-to-hr'
    ])
         queryset.update(reimbursement_status=2)
         print(queryset)
         total_amount = queryset.aggregate(total_amount=Sum('reimbursed_cost'))['total_amount']
         total_rows = queryset.aggregate(total_rows=Count('id'))['total_rows']
         request.data['amount'] = total_amount
         request.data['no_of_data'] = total_rows
         customisedtrainingserializer = PayrollCustomisedTrainingSerializer(data=request.data)
         serializer = SalaryBatchAttributeSerilaizer(data=request.data)
         if customisedtrainingserializer.is_valid() and serializer.is_valid():
                customisedtrainingserializer.save()
                serializer.save()
         else: return errorMessage(customisedtrainingserializer.errors)
        

        elif re.search(r'\b\s*PF\s*\b', process_name, re.IGNORECASE):
            PayrollCustomisedPFProcesses.objects.filter(salary_batch__organization=user_organization.id).update(is_active=False)
            percentagequery = ProvidentFunds.objects.get(organization=user_organization.id, is_active=True)
            percentage = percentagequery.percentage
            queryset = EmployeeProvidentFunds.objects.filter(
                employee__in=employee_ids,
                employee__organization=user_organization.id,
                status='approved'
            )
            basic_salary = None
            current_salary = None

            # Fetch current salaries of employees
            employee_salaries = Employees.objects.filter(
                id__in=employee_ids,
                organization=user_organization.id
            ).values('id', 'current_salary')

            # Logic to associate salaries with employee_ids in the queryset
            salary_mapping = {employee['id']: employee['current_salary'] for employee in employee_salaries}

            # Calculate and save PF amounts
            total_pf_amount = 0
            

            for record in queryset:
                employee_id = record.employee_id
                current_salary = salary_mapping.get(employee_id, 0)

                # Find the "Basic" composition for the current employee
                basic_composition = next(
                    (composition for composition in payroll_composition if composition.payroll_compositions_attribute.title == 'Basic'),
                    None
                )
                pf_amount = 0
                if basic_composition:
                    basic_percentage = basic_composition.attribute_percentage
                    basic_salary = (current_salary * basic_percentage) / 100
                    pf_amount = (Decimal(percentage) / 100) * basic_salary 
                    total_pf_amount += round(pf_amount,2)
                
                employee_instance = Employees.objects.get(id=employee_id)
                PFRecords.objects.create(
                    salary_batch=batch_obj,
                    employee=employee_instance,
                    amount=round(pf_amount,2),
                    should_include=True,
                    created_by=request.user
                )
                
            request.data['amount'] = total_pf_amount
            request.data['no_of_data'] = queryset.count()

            # Save data using serializers
            customisedpfserializer = PayrollCustomisedPFSerializer(data=request.data)
            serializer = SalaryBatchAttributeSerilaizer(data=request.data)

            if customisedpfserializer.is_valid() and serializer.is_valid():
                customisedpfserializer.save()
                serializer.save()
            else:
                return errorMessage(customisedpfserializer.errors)
           

      
       else:                  
        serializer = SalaryBatchAttributeSerilaizer(data=request.data)
        if serializer.is_valid():
          serializer.save()
        #   return successMessageWithData('success', serializer.data)
        # return errorMessageWithData('error',serializer.errors)
        
      return successMessage('Eligible Attributes have been added to Salary batch')
     except Exception as e:
            return exception(e)
  
class SalaryBatchList(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated , IsAdminOnly,  DoesOrgExists]
    def listactivesalarybatches(self, request, *args,**kwargs):
        try:
              user_organization = request.data.get('organization_profile')
              salary_batch_query = SalaryBatch.objects.filter(
                organization=user_organization.id,
                is_active=True,
                is_lock=True
            ).exclude(batch_status='transferred')

              serializer = SalaryBatchSerilaizer(salary_batch_query, many=True)
              return successMessageWithData('success', serializer.data)
        except Exception as e:
            return exception(e)
    def create(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            request.data['organization'] = user_organization.id
            payroll_batch = request.data.get('payroll_batch')
            data = {'batch': None}

            batch = PayrollBatches.objects.filter(id=payroll_batch,organization=user_organization.id,is_active=True,is_lock =True)
            if batch.exists():
                obj = batch.get()
                batch_serializer = PayrollBatchesViewsetSerializers(obj, many=False)
                data['batch'] = batch_serializer.data
            else :
                return errorMessage('No lock batch found')
            user_organization = request.data.get('organization_profile')
            request.data['organization'] = user_organization.id
            user_id = request.user.id
            request.data['created_by'] = user_id
            request.data['payroll_batch'] = data['batch']['id']
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            batch_no = f"{start_date}_{end_date}"

            # Add the batch_no to the request data
            request.data['batch_no'] = batch_no

            payroll_batch_id = data['batch']['id']

            # Check if an active payroll batch exists for the given organization
            query = PayrollBatches.objects.filter(id=payroll_batch_id, organization=user_organization.id, is_active=True)
            if not query.exists():
                return errorMessage('No active payroll batch exists')

            # Deactivate previous salary batches for the same payroll batch
            # previous_batches = SalaryBatch.objects.filter(is_active=True)
            # for batch in previous_batches:
            #     batch.is_active = False
            #     batch.save()

            # Continue with the creation of the SalaryBatch object
            serializer = SalaryBatchSerilaizer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return successMessageWithData('success', serializer.data)
            return errorMessageWithData('error', serializer.errors)

        except Exception as e:
            return exception(e)
        
    def view(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            request.data['organization'] = user_organization.id
            payroll_batch = request.data.get('payroll_batch')
            data = {'batch': None}

            batch = PayrollBatches.objects.filter(id=payroll_batch,organization=user_organization.id,is_active=True,is_lock =True)
            if batch.exists():
                obj = batch.get()
                batch_serializer = PayrollBatchesViewsetSerializers(obj, many=False)
                data['batch'] = batch_serializer.data
            else :
                return errorMessage('No lock batch found')
            user_organization = request.data.get('organization_profile')
            # payroll_batch = data['batch']['id']
            # Query all salary batches
            salary_batches = SalaryBatch.objects.filter(organization=user_organization.id,payroll_batch=payroll_batch,is_active=True).exclude(batch_status='transferred')
            serializer = SalaryBatchSerilaizer(salary_batches, many=True)
            return successMessageWithData('message', serializer.data)
            # return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return exception(e)
        
    def lockSalaryBatch(self, request, *args, **kwargs):
        try: 
            user_organization = request.data.get('organization_profile')
            salary_batch = request.data.get('salary_batch')
            value_type=None

            # check if active batch exists and if batch is locked or not
            batch_query = SalaryBatch.objects.filter(id=salary_batch,organization=user_organization.id, is_active=True)
            attribute_query = SalaryBatchAttributes.objects.filter(salary_batch__organization=user_organization.id,salary_batch=salary_batch, is_active=True)
            for attribute in attribute_query:
                if attribute.payroll_batch_attribute.payroll_attribute.valueType:
                    value_type = attribute.payroll_batch_attribute.payroll_attribute.valueType.title
                else:
                    pass
                if value_type == 'Variable':
                    variable_query = VariableDistributions.objects.filter(payroll_attribute=attribute.payroll_batch_attribute.payroll_attribute.id,salary_batch=salary_batch,is_active=True)
                    for amount in variable_query:
                        variable_amount = amount.amount
                        if variable_amount is None:
                            return errorMessage('Attribute amount cannot be null')
            # Batch is locked
            batch_obj = batch_query.get()
            batch_obj.batch_status = 'in-progress'
            batch_obj.is_lock = True
            batch_obj.lock_by = request.user
            batch_obj.end_date = datetime.date.today()
            batch_obj.save()

            return successMessage("This salary batch is successfully submitted")

        except Exception as e:
            return exception(e)
        
    def unlockSalaryBatch(self, request, *args, **kwargs):
        try: 
            user_organization = request.data.get('organization_profile')
            salary_batch = request.data.get('salary_batch')

            # check if active batch exists and if batch is locked or not
            batch_query = SalaryBatch.objects.filter(id=salary_batch,organization=user_organization.id, is_active=True)
            
            # Batch is locked
            batch_obj = batch_query.get()
            batch_obj.batch_status = 'unlock'
            batch_obj.is_lock = False
            batch_obj.is_active = False
            batch_obj.lock_by = request.user
            batch_obj.end_date = datetime.date.today()
            batch_obj.save()

            return successMessage("This salary batch is successfully submitted")

        except Exception as e:
            return exception(e)
        
        
        
class PayrollAcountantViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated , IsAdminOnly,  DoesOrgExists]
    # queryset = PayrollBatchAttributes.objects.all()
    # serializer_class = PayrollBatchAttributesSerializer
    
    def view(self, request, *args, **kwargs):
     try:
        user_organization = request.data.get('organization_profile')
        salary_batch = request.data.get('salary_batch')
        payroll_batch = request.data.get('payroll_batch')
        data = { 'salary':None}
            
        payroll_batch_query = PayrollBatches.objects.get(id=payroll_batch,organization=user_organization.id,is_active=True)
        if not payroll_batch_query:
            return errorMessage('No active payroll bathch exist against this id')
        salary_batch = SalaryBatch.objects.filter(id=salary_batch,organization=user_organization.id,is_active=True, is_lock=True)
        if salary_batch.exists():
            salary_obj = salary_batch.get()
            salary_batch_serializer = SalaryBatchSerilaizer(salary_obj, many=False)
            data['salary'] = salary_batch_serializer.data
            value_type = None

        else :
            return errorMessage('No locked salary batch exist')
        
        
        employee_data = []
        unverified_data = []
        unprocessed_data = []
        processed_data = []
        employees_payroll_configurations = EmployeePayrollConfiguration.objects.filter(payroll_batch=payroll_batch, is_active=True)

        employee_ids = employees_payroll_configurations.values_list('employee', flat=True)
        attribute_query = SalaryBatchAttributes.objects.filter(salary_batch__organization=user_organization.id,salary_batch=data['salary']['id'], is_active=True)
        salary_batch = SalaryBatch.objects.get(id=data['salary']['id'],is_active=True)
        employees = Employees.objects.filter(id__in=employee_ids,organization=user_organization.id, is_active=True)
        
        payroll_composition = PayrollBatchCompositions.objects.filter(payroll_batch=payroll_batch, is_active=True)
        for employee in employees:
         employees_bank=None
         bank_code = None
         employees_bank_title = None
         basic_percentage = None
         basic_salary = None
         try:
            employees_bank_query = EmployeeBankDetails.objects.get(employee=employee.id, is_active=True)
            employees_bank = employees_bank_query.account_no
            bank_code = employees_bank_query.bank.code
            employees_bank_title = employees_bank_query.bank.name
         except EmployeeBankDetails.DoesNotExist:
            employees_bank = None
         net_salary_before_tax = 0
         taxable_total = 0
         non_taxable_total = 0
         taxable_total_addons = 0
         taxable_total_deductions = 0
         if salary_batch.is_gross_allowed == True:
            if employee.current_salary is not None:
                net_salary_before_tax = employee.current_salary
                taxable_total_addons = employee.current_salary
         is_verified=False
         transfer_status = 'pending'
         non_taxable_total_addons = 0
         non_taxable_total_deductions = 0
         tax_rate = 0
         tax = None
         tax_amount = 0
         total_addons = 0
         total_customized = 0
         total_deductions =0
         try:
          is_verified_query = ProcessedSalary.objects.get(salary_batch=data['salary']['id'],employee=employee.id,is_active=True)
          if is_verified_query:
                is_verified=True
                transfer_status = is_verified_query.transfer_status
         except ProcessedSalary.DoesNotExist:
                is_verified=False
         employee_info = {
                'employee_id': employee.id,
                'employee_name':employee.name,
                'jobtitle':employee.staff_classification.title if employee.staff_classification and employee.staff_classification.title else None,
                'joining_date': employee.joining_date,
                'employee_type': employee.employee_type.title if employee.employee_type and employee.employee_type.title else None,
                'email': employee.official_email,
                'bank_name': employees_bank_title,
                'employee_bank_account_no' : employees_bank,
                'cnic' : employee.cnic_no,
                'department' : employee.department.title if employee.department and employee.department.title else None,
                'bank_code' : bank_code,
                'gross_salary': net_salary_before_tax,
                'addons': [],
                'deductions' : [],
                'customised': [],
                'net_salary_before_tax': 0,
                'taxable_total': 0,
                'non_taxable_total': 0,
                'tax_rate': 0,
                'tax_amount': 0,
                'net_salary_after_tax': 0,
                'net_salary': 0,
                'is_verified':is_verified,
                'transfer_status': transfer_status,
                'compositions': []
            }
         for composition in payroll_composition:
            basic_composition = next(
                    (composition for composition in payroll_composition if composition.payroll_compositions_attribute.title == 'Basic'),
                    None
                )
            if basic_composition:
                    basic_percentage = basic_composition.attribute_percentage
                    basic_salary = (net_salary_before_tax * basic_percentage) / 100
            payroll_composition_attribute = composition.payroll_compositions_attribute.title
            attribute_percentage = composition.attribute_percentage
            percentage_value = (net_salary_before_tax * attribute_percentage) / 100
            composition_info = {
                        payroll_composition_attribute : percentage_value
            }
                    # employee_info[payroll_composition_attribute] = percentage_value
                    # employee_data.append(employee_info)
            employee_info['compositions'].append(composition_info)
         employee_data.append(employee_info)
         if is_verified == False and transfer_status == 'pending':
             unverified_data.append(employee_info)
         elif is_verified == True and transfer_status == 'pending':
             unprocessed_data.append(employee_info)
         elif is_verified == True and transfer_status == 'transferred':
             processed_data.append(employee_info)
         for attribute in attribute_query:
           if attribute.payroll_batch_attribute.payroll_attribute.valueType:
            value_type = attribute.payroll_batch_attribute.payroll_attribute.valueType.title
           else:
              pass
           attribute_type = attribute.payroll_batch_attribute.payroll_attribute.payroll_type
           is_Taxable = attribute.payroll_batch_attribute.is_Taxable
           is_organization = attribute.payroll_batch_attribute.payroll_attribute.is_organization_base
           is_employee_base = attribute.payroll_batch_attribute.payroll_attribute.is_employee_base
           is_customized = attribute.payroll_batch_attribute.payroll_attribute.is_customized
           if value_type == 'Fixed':
            if is_organization:
              fixed_query = FixedDistribution.objects.filter(payroll_attribute=attribute.payroll_batch_attribute.payroll_attribute.id,payroll_batch=payroll_batch,is_active=True)
              for amount in fixed_query:
                  fixed_amount = amount.amount
                  attribute_info = {
                    'attribute_name': attribute.payroll_batch_attribute.payroll_attribute.title,
                    'value_type': value_type,
                    'amount': fixed_amount,
                    'from_fixed':True,
                    'attribute_type': attribute_type,
                    "is_Taxable": is_Taxable
                }
                  
                  if attribute_type == 'Addon':
                    employee_info['addons'].append(attribute_info)
                    total_addons += fixed_amount
                    net_salary_before_tax += fixed_amount or 0
                    if is_Taxable:
                        taxable_total_addons += fixed_amount or 0
                    else:
                        non_taxable_total_addons += fixed_amount or 0
                  elif attribute_type == 'Deduction':
                   employee_info['deductions'].append(attribute_info)
                   net_salary_before_tax -= fixed_amount or 0
                   total_deductions += fixed_amount or 0
                   if is_Taxable:
                        taxable_total_deductions += fixed_amount or 0
                   else:
                        non_taxable_total_deductions += fixed_amount or 0
                  attribute_info = {}
            elif is_employee_base:
                eligible_employees = EligibleEmployees.objects.filter(payroll_batch=payroll_batch,employee=employee,payroll_attribute=attribute.payroll_batch_attribute.payroll_attribute.id,is_active=True)
                if eligible_employees.exists():
                 fixed_query = FixedDistribution.objects.filter(payroll_attribute=attribute.payroll_batch_attribute.payroll_attribute.id,payroll_batch=payroll_batch,is_active=True)
                 for amount in fixed_query:
                  fixed_amount = amount.amount
                  attribute_info = {
                    'attribute_name': attribute.payroll_batch_attribute.payroll_attribute.title,
                    'value_type': value_type,
                    'amount': fixed_amount,
                    'attribute_type': attribute_type,
                    "is_Taxable": is_Taxable
                }
                 
                 if attribute_type == 'Addon':
                    employee_info['addons'].append(attribute_info)
                    total_addons += fixed_amount or 0
                    net_salary_before_tax += fixed_amount or 0
                    if is_Taxable:
                       taxable_total_addons += fixed_amount or 0
                    else:
                       non_taxable_total_addons += fixed_amount or 0
                
                 elif attribute_type == 'Deduction':
                   employee_info['deductions'].append(attribute_info)
                   net_salary_before_tax -= fixed_amount or 0
                   total_deductions += fixed_amount or 0
                   if is_Taxable:
                       taxable_total_deductions += fixed_amount or 0
                   else:
                       non_taxable_total_deductions += fixed_amount or 0
                 attribute_info={}
           elif value_type == 'Variable':
              variable_query = VariableDistributions.objects.filter(employee=employee,payroll_attribute=attribute.payroll_batch_attribute.payroll_attribute.id,salary_batch=data['salary']['id'],is_active=True)
              for amount in variable_query:
                  variable_amount = amount.amount
                  attribute_info = {
                    'attribute_name': attribute.payroll_batch_attribute.payroll_attribute.title,
                    'value_type': value_type,
                    'amount': variable_amount,
                    'attribute_type': attribute_type,
                    "is_Taxable": is_Taxable
                }
                  
                  if attribute_type == 'Addon':
                   employee_info['addons'].append(attribute_info)
                   net_salary_before_tax += variable_amount or 0
                   total_addons += variable_amount or 0
                   if is_Taxable:
                       taxable_total_addons += variable_amount or 0
                   else:
                       non_taxable_total_addons += variable_amount or 0
                  elif attribute_type == 'Deduction':
                   employee_info['deductions'].append(attribute_info)  
                   net_salary_before_tax -= variable_amount or 0
                   total_deductions += variable_amount or 0
                   if is_Taxable:
                       taxable_total_deductions += variable_amount or 0
                   else:
                       non_taxable_total_deductions += variable_amount or 0
                  attribute_info={}
           elif value_type == 'FFSC':
             if is_employee_base:
              eligible_employees = EligibleEmployees.objects.filter(payroll_batch=payroll_batch,employee=employee,payroll_attribute=attribute.payroll_batch_attribute.payroll_attribute.id,is_active=True)
              for staff in eligible_employees:
                  sc = staff.employee.staff_classification
                  sc_query = MonthlyDistribution.objects.filter(payroll_batch=payroll_batch,payroll_attribute=attribute.payroll_batch_attribute.payroll_attribute.id, staff_classification=sc, is_active=True)
                  for amount in sc_query:
                   staff_amount = amount.amount
                   attribute_info = {
                    'attribute_name': attribute.payroll_batch_attribute.payroll_attribute.title,
                    'value_type': value_type,
                    'amount': staff_amount,
                    'attribute_type': attribute_type,
                    "is_Taxable": is_Taxable
                }
                  
                  if attribute_type == 'Addon':
                   employee_info['addons'].append(attribute_info)
                   net_salary_before_tax += staff_amount or 0
                   total_addons += staff_amount or 0
                   if is_Taxable:
                       taxable_total_addons += staff_amount or 0
                   else:
                       non_taxable_total_addons += staff_amount or 0
                  elif attribute_type == 'Deduction':
                   employee_info['deductions'].append(attribute_info)
                   net_salary_before_tax -= staff_amount or 0
                   total_deductions += staff_amount or 0
                   if is_Taxable:
                       taxable_total_deductions += staff_amount or 0
                   else:
                       non_taxable_total_deductions += staff_amount or 0
                  attribute_info={}
             elif is_organization:
                 sc = employee.staff_classification
                 sc_query = MonthlyDistribution.objects.filter(payroll_batch=payroll_batch,payroll_attribute=attribute.payroll_batch_attribute.payroll_attribute.id, staff_classification=sc, is_active=True)
                 for amount in sc_query:
                   staff_amount = amount.amount
                   attribute_info = {
                    'attribute_name': attribute.payroll_batch_attribute.payroll_attribute.title,
                    'value_type': value_type,
                    'amount': staff_amount,
                    'attribute_type': attribute_type,
                    "is_Taxable": is_Taxable
                 }
                 
                 if attribute_type == 'Addon':
                   employee_info['addons'].append(attribute_info)
                   net_salary_before_tax += staff_amount or 0
                   total_addons += staff_amount or 0
                   if is_Taxable:
                       taxable_total_addons += staff_amount or 0
                   else:
                       non_taxable_total_addons += staff_amount or 0
                 elif attribute_type == 'Deduction':
                   employee_info['deductions'].append(attribute_info)
                   net_salary_before_tax -= staff_amount or 0
                   total_deductions += staff_amount or 0
                   if is_Taxable:
                       taxable_total_deductions += staff_amount or 0
                   else:
                       non_taxable_total_deductions += staff_amount or 0
                 
                 attribute_info={}
           if is_customized:
              if attribute.payroll_batch_attribute.payroll_attribute.title == 'Medical' or attribute.payroll_batch_attribute.payroll_attribute.title =='medical':
                queryset = EmployeesMedicalAllowance.objects.filter(
                employee=employee,
                employee__organization=user_organization.id,
                status='approved'
                 ).exclude(processed_status__in=[
                  'processed-by-accountant',
                  'not-processed'
                #   'processed-to-accountant',
                # 'processed-to-hr'
                 ])
                for amount in queryset:
                 approved_amount = amount.amount
                 attribute_info = {
                     'id':amount.id,
                    'attribute_name': attribute.payroll_batch_attribute.payroll_attribute.title,
                    'value_type': value_type,
                    'amount': approved_amount,
                    'attribute_type': attribute_type,
                    "is_Taxable": is_Taxable
                 }
                 employee_info['customised'].append(attribute_info)
                 total_customized += approved_amount or 0
                 net_salary_before_tax += approved_amount or 0
                 if is_Taxable:
                       taxable_total_addons += approved_amount or 0
                 else:
                       non_taxable_total_addons += approved_amount or 0
                 attribute_info={}
              if attribute.payroll_batch_attribute.payroll_attribute.title == 'Gym' or attribute.payroll_batch_attribute.payroll_attribute.title =='gym':
                queryset = EmployeesGymAllowance.objects.filter(
                employee=employee,
                employee__organization=user_organization.id,
                status='approved'
                 ).exclude(processed_status__in=[
                  'processed-by-accountant',
                  'not-processed'
                #   'processed-to-accountant',
                # 'processed-to-hr'
                 ])
                for amount in queryset:
                 approved_amount = amount.amount
                 attribute_info = {
                     'id': amount.id,
                    'attribute_name': attribute.payroll_batch_attribute.payroll_attribute.title,
                    'value_type': value_type,
                    'amount': approved_amount,
                    'attribute_type': attribute_type,
                    "is_Taxable": is_Taxable
                 }
                 employee_info['customised'].append(attribute_info)
                 net_salary_before_tax += approved_amount or 0
                 total_customized += approved_amount or 0
                 if is_Taxable:
                       taxable_total_addons += approved_amount or 0
                 else:
                       non_taxable_total_addons += approved_amount or 0
                 attribute_info={}
              if attribute.payroll_batch_attribute.payroll_attribute.title == 'Certifications' or attribute.payroll_batch_attribute.payroll_attribute.title =='certifications':
                queryset = LNDCertifications.objects.filter(
                employee=employee,
                employee__organization=user_organization.id,
                is_reimbursement=True
                 ).exclude(reimbursement_status__in=[
                  4,
                  1,
                #   'processed-to-accountant',
                # 'processed-to-hr'
                 ])
                for amount in queryset:
                 approved_amount = amount.cost
                 attribute_info = {
                     'id':amount.id,
                    'attribute_name': attribute.payroll_batch_attribute.payroll_attribute.title,
                    'value_type': value_type,
                    'amount': approved_amount,
                    'attribute_type': attribute_type,
                    "is_Taxable": is_Taxable
                 }
                 employee_info['customised'].append(attribute_info)
                 total_customized += approved_amount or 0
                 net_salary_before_tax += approved_amount or 0
                 if is_Taxable:
                       taxable_total_addons += approved_amount or 0
                 else:
                       non_taxable_total_addons += approved_amount or 0
                 attribute_info={}
              if attribute.payroll_batch_attribute.payroll_attribute.title == 'Training' or attribute.payroll_batch_attribute.payroll_attribute.title =='training':
                queryset = TrainingEmployee.objects.filter(
                employee=employee,
                employee__organization=user_organization.id,
                is_reimbursement=True
                 ).exclude(reimbursement_status__in=[
                  4,
                  1
                #   'processed-to-accountant',
                # 'processed-to-hr'
                 ])
                for amount in queryset:
                 approved_amount = amount.reimbursed_cost
                 attribute_info = {
                     'id':amount.id,
                    'attribute_name': attribute.payroll_batch_attribute.payroll_attribute.title,
                    'value_type': value_type,
                    'amount': approved_amount,
                    'attribute_type': attribute_type,
                    "is_Taxable": is_Taxable
                 }
                 employee_info['customised'].append(attribute_info)
                 total_customized += approved_amount or 0
                 net_salary_before_tax += approved_amount or 0
                 if is_Taxable:
                       taxable_total_addons += approved_amount or 0
                 else:
                       non_taxable_total_addons += approved_amount or 0
                 attribute_info={}
              if attribute.payroll_batch_attribute.payroll_attribute.title == 'PF' or attribute.payroll_batch_attribute.payroll_attribute.title =='pf':
                queryset = ProvidentFunds.objects.get(
                organization=user_organization.id,
                is_active=True
                 )
                percentage = queryset.percentage
                employeequery = EmployeeProvidentFunds.objects.filter(employee = employee, is_active=True, has_approval=True, status='approved')
                for emp in employeequery:
                    amount = (basic_salary * percentage) / 100
                    attribute_info = {
                    'id':emp.id,
                    'attribute_name': attribute.payroll_batch_attribute.payroll_attribute.title,
                    'value_type': value_type,
                    'amount': amount,
                    'attribute_type': attribute_type,
                    "is_Taxable": is_Taxable
                 }
                    employee_info['deductions'].append(attribute_info)
                    net_salary_before_tax -= amount or 0
                    total_deductions += amount or 0
                    if is_Taxable:
                       taxable_total_deductions += amount or 0
                    else:
                       non_taxable_total_deductions += amount or 0
                    attribute_info={}
           taxable_total = Decimal(taxable_total_addons) - Decimal(non_taxable_total_deductions)
           taxable_total = Decimal(taxable_total)
           non_taxable_total = non_taxable_total_addons - non_taxable_total_deductions    
           tax_check = taxable_total * 12
           tax_slab = TaxSlab.objects.filter(
             organization = user_organization.id,
             initial_income_threshold__lte=tax_check,
             income_ceiling__gte=tax_check,
             country__iexact=payroll_batch_query.country,
             year=DATE.now().year,
             is_active=True, is_lock=True).first()
           if tax_slab:
             tax_rate = tax_slab.tax_rate
             tax=tax_slab.id
           else:
             tax_rate = None
             tax=None
           if tax_rate:
            
            exemption_amount = tax_slab.exemption_amount
            if not exemption_amount is None:
                exemption_amount = exemption_amount/12
            else:
                exemption_amount = 0
            fixed_amount = tax_slab.fixed_amount
            if not fixed_amount is None:
                fixed_amount = fixed_amount /12
            else :
                fixed_amount = 0
             
            
            tax_on_salary = taxable_total - Decimal(exemption_amount)
            # print("Test",tax_on_salary)
            tax_amount = (Decimal(str(tax_on_salary)) / Decimal('100')) * Decimal(str(tax_rate))
            tax_amount = Decimal(tax_amount) + Decimal(fixed_amount)
            # print("Test2",type(net_salary_before_tax))
            net_salary_before_tax=int(net_salary_before_tax)
            # print("Test2",type(net_salary_before_tax))
           employee_info['net_salary_before_tax'] =  net_salary_before_tax
           employee_info['taxable_total'] =  taxable_total
           employee_info['non_taxable_total'] =  non_taxable_total
           employee_info['taxable_amount_addons'] =  taxable_total_addons
           employee_info['non_taxable_amount_addons'] =  non_taxable_total_addons
           employee_info['taxable_amount_deductions'] =  taxable_total_deductions
           employee_info['non_taxable_amount_deductions'] =  non_taxable_total_deductions
           employee_info['tax_rate'] = tax_rate
           employee_info['tax_amount'] = tax_amount
           employee_info['net_salary_after_tax'] = net_salary_before_tax - tax_amount
           employee_info['net_salary'] = net_salary_before_tax - tax_amount
           employee_info['total_deductions'] = total_deductions 
           employee_info['total_addons'] = total_addons
           employee_info['total_customized'] = total_customized 
           employee_info['tax'] = tax 
          
          
        overall_totals = {
         'taxable_total': 0,
         'non_taxable_total': 0,
         'tax_rate': 0,
         'tax_amount': 0,
         'net_salary': 0,
         'total_deductions': 0,
         'total_addons': 0,
         'total_customized': 0,
         'batch_total': 0
               }
        for employee_info in employee_data:
            overall_totals['taxable_total'] += round(employee_info['taxable_total'] or 0, 2)
            overall_totals['non_taxable_total'] += round(employee_info['non_taxable_total'] or 0, 2)
            overall_totals['tax_rate'] += round(employee_info['tax_rate'] or 0, 2)
            overall_totals['tax_amount'] += round(employee_info['tax_amount'] or 0, 2)
            overall_totals['net_salary'] += round(employee_info['net_salary'] or 0, 2)
            overall_totals['total_deductions'] += round(employee_info['total_deductions'] or 0, 2)
            overall_totals['total_addons'] += round(employee_info['total_addons'] or 0, 2)
            overall_totals['total_customized'] += round(employee_info['total_customized'] or 0, 2)
            overall_totals['batch_total'] += round(
                (employee_info['total_customized'] or 0) +
                (employee_info['gross_salary'] or 0) +
                (employee_info['total_addons'] or 0) -
                (employee_info['total_deductions'] or 0),
                2
            )
        response_data = {
            'salary': data['salary'],
            'employee_data': employee_data,
            'overall_totals': overall_totals,
            'unverified_data': unverified_data,
            'unprocessed_data': unprocessed_data,
            'processed_data': processed_data
        }      
        return successMessageWithData('success', response_data)

        
                
     except Exception as e:
        return exception(e)
  
    def verifyemployeesalary(self, request, *args, **kwargs):
     try:
        data=request.data
        salary_batch_id = data.get('salary_batch')
        payroll_batch_id = data.get('payroll_batch')

        salary_batch = SalaryBatch.objects.get(id=salary_batch_id, payroll_batch=payroll_batch_id, is_active =True)
        if not salary_batch:
            return errorMessage('Salary Batch does not exist')      

        
        with transaction.atomic():
                for employee_data in data.get('employee_data', []):
                    employee_id = employee_data.get('employee_id')
                    employee = Employees.objects.filter(id=employee_id).first()
                    existing_record = ProcessedSalary.objects.filter(
                        salary_batch=salary_batch,
                        employee=employee,
                        is_active=True,
                    ).first()
                    customised = employee_data['customised']
                    addons_records = employee_data['addons']
                    deductions_records = employee_data['deductions']
                    # print(addons_records)
                    if not existing_record:
                      for custom in customised:
                        custom_id = custom['id']
                        if custom['attribute_name'] == 'Gym' or custom['attribute_name'] =='gym':
                            queryset = EmployeesGymAllowance.objects.filter(id=custom_id,employee=employee_id,
                                status='approved'
                                ).exclude(processed_status__in=[
                                'processed-to-accountant',
                                ])
                            queryset.update(processed_status='processed-to-accountant', processed_in=salary_batch)
                        if custom['attribute_name'] == 'Medical' or custom['attribute_name'] =='medical':
                            queryset = EmployeesMedicalAllowance.objects.filter(id=custom_id,employee=employee_id,
                                status='approved'
                                ).exclude(processed_status__in=[
                                'processed-to-accountant',
                                ])
                            queryset.update(processed_status='processed-to-accountant', processed_in=salary_batch)
                        if custom['attribute_name'] == 'Training' or custom['attribute_name'] =='training':
                            queryset = TrainingEmployee.objects.filter(id=custom_id,employee=employee_id,
                                is_reimbursement=True
                                ).exclude(reimbursement_status__in=[
                                3,
                                ])
                            queryset.update(reimbursement_status=3, processed_in=salary_batch)
                        if custom['attribute_name'] == 'Certifications' or custom['attribute_name'] =='certifications':
                            queryset = LNDCertifications.objects.filter(id=custom_id,employee=employee_id,
                                is_reimbursement=True
                                ).exclude(reimbursement_status__in=[
                                3,
                                ])
                            queryset.update(reimbursement_status=3, processed_in=salary_batch)
                      try:
                        tax=TaxSlab.objects.get(id=employee_data.get('tax'))
                      except TaxSlab.DoesNotExist:
                        tax=None
                      ProcessedSalary.objects.create(
                            salary_batch=salary_batch,
                            employee=employee,
                            net_salary=employee_data.get('net_salary'),
                            gross_salary=employee_data.get('gross_salary'),
                            taxable_amount=employee_data.get('taxable_total'),
                            non_taxable_amount=employee_data.get('non_taxable_total'),
                            taxable_amount_addons=employee_data.get('taxable_total_addons'),
                            non_taxable_amount_addons=employee_data.get('non_taxable_total_addons'),
                            taxable_amount_deductions=employee_data.get('taxable_total_deductions'),
                            non_taxable_amount_deductions=employee_data.get('non_taxable_total_deductions'),
                            tax_amount=employee_data.get('tax_amount'),
                            tax_rate=employee_data.get('tax_rate'),
                            total_addons=employee_data.get('total_addons'),
                            total_deductions=employee_data.get('total_deductions'),
                            total_customized=employee_data.get('total_customized'),
                            tax=tax,
                            addons =addons_records,
                            deductions = deductions_records,
                            customised = customised,
                            compositions = employee_data.get('compositions')   
                        )

        return successMessage('success')

     except Exception as e:
            return exception(e)

    def process_employee_salary(self, request, *args, **kwargs):
     try:
        data = request.data
        salary_batch_id = data.get('salary_batch')
        payroll_batch_id = data.get('payroll_batch')

        salary_batch = SalaryBatch.objects.get(id=salary_batch_id, payroll_batch=payroll_batch_id, is_active=True)
        if not salary_batch:
            return errorMessage('Salary Batch does not exist')

        all_verified = True  # Flag to track if all employee salaries are verified

        with transaction.atomic():
            for employee_data in data.get('employee_data', []):
                employee_id = employee_data.get('employee_id')
                employee = Employees.objects.filter(id=employee_id).first()
                existing_record = ProcessedSalary.objects.filter(
                    salary_batch=salary_batch,
                    employee=employee,
                    is_active=True,
                ).first()

                # bank_account_no = employee_data['employee_bank_account_no']
                # bank_code = employee_data['bank_code']
                # bank_name = employee_data['bank_name']

                if not existing_record:
                    all_verified = False
                    break 
            if not all_verified:
                return errorMessage('Please verify all selected employee salaries before updating records.')

            # If all employees are verified, proceed to create/update records
            for employee_data in data.get('employee_data', []):
                employee_id = employee_data.get('employee_id')
                employee = Employees.objects.filter(id=employee_id).first()
                existing_record = ProcessedSalary.objects.filter(
                    salary_batch=salary_batch,
                    employee=employee,
                    is_active=True,
                ).first()

                bank_account_no = employee_data['employee_bank_account_no']
                bank_code = employee_data['bank_code']
                bank_name = employee_data['bank_name']

                if existing_record:
                    existing_record_obj = existing_record
                    existing_record_obj.transfer_status = 'transferred'
                    existing_record_obj.bank_account_no = bank_account_no
                    existing_record_obj.bank_code = bank_code
                    existing_record_obj.bank_name = bank_name
                    existing_record_obj.save()
                else:
                    # If any employee is not verified, don't create new records
                    return errorMessage('Please verify all selected employee salaries before updating records.')

        return successMessage('Records Updated')

     except Exception as e:
        return exception(e)

        
    def transfer(self, request, *args, **kwargs):
     try:
        data=request.data
        user_organization = request.data.get('organization_profile')
        salary_batch_id = data.get('salary_batch')
        payroll_batch_id = data.get('payroll_batch')

        salary_batch = SalaryBatch.objects.get(id=salary_batch_id, payroll_batch=payroll_batch_id, is_active =True)
        if not salary_batch:
            return errorMessage('Salary Batch does not exist')      
        employees_payroll_configurations = EmployeePayrollConfiguration.objects.filter(payroll_batch=payroll_batch_id, is_active=True)
        employee_ids = employees_payroll_configurations.values_list('employee', flat=True)
        for employee_id in employee_ids:
            try:
               processed_query = ProcessedSalary.objects.get(salary_batch=salary_batch_id, employee=employee_id, is_active=True)
               if processed_query.transfer_status != 'transferred':
                   return errorMessage('Please first process salary of all employee')
            except ProcessedSalary.DoesNotExist:
                return errorMessage('Please verify all employees')
        salary_batch.batch_status='transferred'
        salary_batch.batch_total=data.get('batch_total')
        salary_batch.salary_amount = data.get('salary_amount')
        salary_batch.tax_amount = data.get('tax_amount')
        salary_batch.addons_amount = data.get('addons_amount')
        salary_batch.deduction_amount = data.get('deduction_amount')
        salary_batch.customised_amount = data.get('customised_amount')
        salary_batch.save() 
        employees_payroll_configurations = EmployeePayrollConfiguration.objects.filter(payroll_batch=payroll_batch_id, is_active=True)

        employee_ids = employees_payroll_configurations.values_list('employee', flat=True)
        employees = Employees.objects.filter(id__in=employee_ids,organization=user_organization.id, is_active=True)
        for employee in employees:
                            queryset_gym = EmployeesGymAllowance.objects.filter(employee=employee.id,
                                status='approved'
                                ).exclude(processed_status__in=[
                                'processed-by-accountant',
                                ])
                            queryset_gym.update(processed_status='processed-by-accountant', processed_in=salary_batch)
                            queryset_medical = EmployeesMedicalAllowance.objects.filter(employee=employee_id,
                                status='approved'
                                ).exclude(processed_status__in=[
                                'processed-by-accountant',
                                ])
                            queryset_medical.update(processed_status='processed-by-accountant', processed_in=salary_batch)
                            queryset_certifications = LNDCertifications.objects.filter(employee=employee_id,
                                is_reimbursement=True
                                ).exclude(reimbursement_status__in=[
                                4
                                ])
                            queryset_certifications.update(reimbursement_status=4, processed_in=salary_batch)
                            queryset_training = TrainingEmployee.objects.filter(employee=employee_id,
                                is_reimbursement=True
                                ).exclude(reimbursement_status__in=[
                                4
                                ])
                            queryset_training.update(reimbursement_status=4, processed_in=salary_batch)
            
        
        return successMessage('success')
       

     except Exception as e:
                    return exception(e)
        
    
class TaxSlabViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated , IsAdminOnly,  DoesOrgExists]
    serializer_class = TaxSlabSerializer
    
    def create(self, request, *args, **kwargs):
     try:
        organization_id = decodeToken(request, self.request)['organization_id']
        request.data['organization'] = organization_id
        request.data['created_by'] = request.user.id
        if not request.user.is_privileged:
            return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.")       
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            
            serializer.save()
            
        else: return errorMessage('Tax Slab cannot be added')     
        return successMessageWithData('success', serializer.data)
     except Exception as e:
         return exception(e)
     
    # def View(self, request, *args, **kwargs):
    #  try:
    #     user_organization = request.data.get('organization_profile')
    #     query = TaxSlab.objects.filter(organization = user_organization.id, is_active=True)
    #     serializer = self.serializer_class(query, many=True) 
    #     return successMessageWithData('success', serializer.data)
    #  except Exception as e:
    #      return exception(e)
    
    def View(self, request, *args, **kwargs):
     try:
        user_organization = request.data.get('organization_profile')
        query = TaxSlab.objects.filter(organization=user_organization.id, is_active=True)

        # Create a dictionary to organize tax slabs by country
        tax_slabs_by_country = {}

        for tax_slab in query:
            country = tax_slab.country  # Replace with the actual field name for the country
            if country not in tax_slabs_by_country:
                tax_slabs_by_country[country] = []
            serializer = self.serializer_class(tax_slab)
            tax_slabs_by_country[country].append(serializer.data)

        # Return the data organized by country
        return successMessageWithData('success', tax_slabs_by_country)
     except Exception as e:
        return exception(e)

     
    def Patch(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            request.data['organization'] = organization_id
            request.data['created_by'] = request.user.id
            if not request.user.is_privileged:
               return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            pk = self.kwargs['pk']
            processed_salary_query = ProcessedSalary.objects.filter(tax=pk, is_active=True)
            if processed_salary_query.exists():
                return errorMessage('Unable to patch Tax Slab: it is currently in use within salary records.')
            active_tax_slab = TaxSlab.objects.filter(id=pk,organization=organization_id, is_active=True)
            if active_tax_slab.exists():
                exs_obj = active_tax_slab.get()
                exs_obj.is_active=False
                exs_obj.save()
            #     tax_data = model_to_dict(exs_obj, exclude=['id', 'organization','is_active','created_by'])
            #     updated_obj = TaxSlab.objects.create(
            #     organization= user_organization,
            #     created_by= request.user,
            #     **tax_data,
            #     is_active=True,
            # )
                serializer = self.serializer_class( data=request.data)
                if not serializer.is_valid():
                 return errorMessageWithData('error',serializer.errors) 
                serializer.save()
                return successMessageWithData('success',serializer.data)
            else:
                return errorMessage('No active tax slab exist against this id')
        except Exception as e:
            return exception(e)
        
    def lock(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            request.data['organization'] = organization_id
            request.data['created_by'] = request.user.id
            if not request.user.is_privileged:
               return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            pk = self.kwargs['pk']
            active_tax_slab = TaxSlab.objects.filter(id=pk,organization=organization_id, is_active=True)
            if active_tax_slab.exists():
                exs_obj = active_tax_slab.get()
                exs_obj.is_lock=True
                exs_obj.save()
                return successMessage('Batch locked successfully')
            else:
                return errorMessage('No active tax slab exist against this id')
        except Exception as e:
            return exception(e)
        
    def unlock(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            request.data['organization'] = organization_id
            request.data['created_by'] = request.user.id
            if not request.user.is_privileged:
                return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            pk = self.kwargs['pk']
            processed_salary_query = ProcessedSalary.objects.filter(tax=pk, is_active=True).exclude(salary_batch__batch_status='transferred')
            if processed_salary_query.exists():
                return errorMessage('Unable to unlock Tax Slab: it is currently in use within salary records.')
            active_tax_slab = TaxSlab.objects.filter(id=pk,organization=organization_id, is_active=True)
            if active_tax_slab.exists():
                exs_obj = active_tax_slab.get()
                exs_obj.is_lock=False
                exs_obj.save()
                return successMessage('Batch locked successfully')
            else:
                return errorMessage('No active tax slab exist against this id')
        except Exception as e:
            return exception(e)
        
    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            organization_id = decodeToken(request, self.request)['organization_id']
            if not request.user.is_privileged:
                return errorMessage("Access Denied: You do not have the necessary privileges to perform this action. Please contact your developer for assistance.") 
            active_tax_slab = TaxSlab.objects.filter(id=pk,organization=organization_id, is_active=True)
            processed_salary_query = ProcessedSalary.objects.filter(tax=pk, is_active=True).exclude(salary_batch__batch_status='transferred')
            if processed_salary_query.exists():
                return errorMessage('Unable to delete Tax Slab: it is currently in use within salary records.')
            if active_tax_slab.exists():
                exs_obj = active_tax_slab.get()
                exs_obj.is_active=False
                exs_obj.save()
                return successMessage('success')
            else:
                return errorMessage('No active tax slab exist against this id')
        except Exception as e:
            return exception(e)
        
class SalaryRecordsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated , IsAdminOnly,  DoesOrgExists]
    def view(self, request, *args, **kwargs):
        try:
            user_organization = request.data.get('organization_profile')
            request.data['organization'] = user_organization.id
            salary_batches = SalaryBatch.objects.filter(organization=user_organization.id,is_active=True,batch_status='transferred')
            serializer = SalaryBatchSerilaizer(salary_batches, many=True)
            return successMessageWithData('message', serializer.data)
            # return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return exception(e)
        
    def record(self, request, *args, **kwargs):
     try:
        user_organization = request.data.get('organization_profile')
        request.data['organization'] = user_organization.id
        salary_batch_id = request.data.get('salary_batch')
        payroll_batch_id = request.data.get('payroll_batch')
        
        payroll_batch_query = PayrollBatches.objects.get(id=payroll_batch_id, organization = user_organization.id)
        if not  payroll_batch_query:
            return errorMessage('No active payroll batch exist against this id')
        
        salary_batch_query = SalaryBatch.objects.get(id=salary_batch_id, organization=user_organization.id, is_active=True, batch_status='transferred')
        if not salary_batch_query:
            return errorMessage('No active salary batch exist against this id')
        
        salary_query = ProcessedSalary.objects.filter(salary_batch = salary_batch_id, is_active=True)
        
        serializer = ProcessedSalarySerilaizer(salary_query, many=True)
        
        return successMessageWithData('success', serializer.data)
     except Exception as e:
          return exception(e)
      
      
      
      
class EmployeeSalaryRecordsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    def record(self, request, *args, **kwargs):
     try:
        year = request.data.get('year')
        if year is None:
                year = DATE.now().year
        employee_id = decodeToken(request, self.request)['employee_id']

        # Retrieve processed salaries for the given employee with batch status 'transferred'
        salary_query = ProcessedSalary.objects.filter(
            employee=employee_id, salary_batch__batch_status='transferred', is_active=True, salary_batch__year=year
        )

        # Serialize processed salaries
        serializer = EmployeeProcessedSalarySerializer(salary_query, many=True)

        # Get salary batch details for each processed salary
        processed_salaries_data = serializer.data
        for salary_data in processed_salaries_data:
            salary_batch_id = salary_data['salary_batch']
            if salary_batch_id:
                # Retrieve salary batch details
                salary_batch = SalaryBatch.objects.filter(id=salary_batch_id).first()
                if salary_batch:
                    # Use .first() to get a single instance, and check if it exists
                    salary_batch_serializer = SalaryBatchSerilaizer(salary_batch)
                    salary_data['salary_batch_details'] = salary_batch_serializer.data
                else:
                    salary_data['salary_batch_details'] = None
            else:
                salary_data['salary_batch_details'] = None

        return successMessageWithData('success', processed_salaries_data)

     except Exception as e:
        return exception(e)

        
    
        
    
        
        

    # permission_classes = [IsAuthenticated, DoesOrgExists]
    # queryset = EmployeePayrollConfiguration.objects.all()
    # serializer_class = EmployeePayrollConfigurationSerializer
