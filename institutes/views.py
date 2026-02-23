import json
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
from rest_framework import generics
from helpers.employee_helper import preEmployeeDataChecks

# Create your views here.
class DegreeTypesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = DegreeTypes.objects.filter(is_active=True)
    serializer_class = DegreeTypesViewsetSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if not DegreeTypes.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'This Degree type does not exists', 'system_status_message': ''})

            obj = DegreeTypes.objects.get(id=pk)
            if obj.is_active == False:
                msg = "This Degree Type is already deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
            obj.is_active = False
            obj.save()
            serializer = DegreeTypesViewsetSerializers(obj)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Deactivated Successfully', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)


class InstitutesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Institutes.objects.filter(is_active=True)
    serializer_class = InstitutesViewsetSerializers


    

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if not Institutes.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'This Institute does not exists', 'system_status_message': ''})

            obj = Institutes.objects.get(id=pk)
            if obj.is_active == False:
                msg = "This Institute is already deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
            obj.is_active = False
            obj.save()
            serializer = InstitutesViewsetSerializers(obj)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Deactivated Successfully', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)


class EmployeeEducationsViewset(viewsets.ModelViewSet):
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

            obj = EmployeeEducations.objects.filter(employee__uuid=emp_uuid, employee__is_active = True, employee__organization=org_id, is_active = True).order_by('id')
            serializer = EmployeeEducationsViewsetSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def retrieve(self, request, *args, **kwargs):
        try:
            institute_id = self.kwargs['institute_id']
            emp_uuid = self.kwargs['emp_uuid']
            org_id = None
            
            # This function whether organization is_active or not
            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            # if user is admin
            if data_check['status'] == 400:
                return Response(data_check)
            elif data_check['status'] == 202:
                org_id = data_check['org_id']


            # if active emergency institute exists to that employee at this specific id
            obj = EmployeeEducations.objects.filter(id=institute_id, employee__uuid=emp_uuid, employee__organization__id = org_id)
            if not obj.exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This employee does not have any institute at this id', 'system_error_message': ''})
            
            if not obj.filter(is_active=True).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This employee institute is deactivated at this id', 'system_error_message': ''})

            obj = EmployeeEducations.objects.get(id = institute_id, employee__uuid=emp_uuid, employee__organization__id = org_id, is_active=True)
            serializer = EmployeeEducationsViewsetSerializers(obj, many=False)
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

            if 'degree_type' in request.data:
                request.data._mutable = True
                request.data['employee'] = emp.id
                request.data['is_active'] = True
                request.data._mutable = False
                
           

            serializer = EmployeeEducationsViewsetSerializers(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)
        
        except Exception as e:
            return exception(e)
    
    
    def patch(self, request, *args, **kwargs):
        try:
            emp_uuid = self.kwargs['emp_uuid']
            institute_id = self.kwargs['institute_id']
            
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



            # if no institute id exists
            if not EmployeeEducations.objects.filter(employee=emp.id, id=institute_id,  employee__organization = emp_org_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Institute does not exist at this id', 'system_status_message': ''})
            

            obj = EmployeeEducations.objects.get(employee = emp.id, id=institute_id)
            serializer = EmployeeEducationsViewsetSerializers(obj, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()
            
            return successfullyUpdated(serializer.data)
  
        except Exception as e:
            return exception(e)


    def delete(self, request, *args, **kwargs):
        try:
            institute_id = self.kwargs['institute_id']
            emp_uuid = self.kwargs['emp_uuid']
            
            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            if data_check['status'] == 400:
                return Response(data_check)
            elif data_check['status'] == 202:
                emp_org_id = data_check['org_id']
           
            emp = Employees.objects.get(uuid=emp_uuid)    
            request.data['employee'] = emp.id
            
            # if active emergency contact exists to that employee at this specific id
            if not EmployeeEducations.objects.filter(id=institute_id, employee__uuid=emp_uuid, employee__is_active=True,  employee__organization__id = emp_org_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This employee does not have any institute at this id', 'system_error_message': ''})

            obj = EmployeeEducations.objects.get(id=institute_id, employee__uuid=emp_uuid, employee__organization__id = emp_org_id)
            if obj.is_active == False:
                return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': '', 'message': 'This Institute is already deactivated', 'system_status_message': ''})

            obj.is_active = False
            obj.save()
            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT,  'data': '', 'message': 'Successfully Deleted', 'system_status_message': ''})


        except Exception as e:
            return exception(e)

















    def get_org_id_from_emp(self, emp_uuid):
        try:
            obj = Employees.objects.get(uuid=emp_uuid)
            if obj.organization is not None:
                return obj.organization.id

            return None
        except Exception as e:
            return None


    def multipleInstituteList(self, emp, institutes_data):
        institutes = []
        serializer_errors = []
        response = {'code': 200, 'message': '', 'system_error': ''}
        if isinstance(institutes_data, str):
            institutes_data = json.loads(institutes_data)
            institutes.append(institutes_data)
        else:
            institutes = institutes_data
        

        try:
            institute_array = {
                'id': '',
                'employee': None,
                'degree_type': '', 
                'institutes': '', 
                'degree_title': '', 
                'duration': '', 
                'institute_name': '', 
                'year_of_completion': '', 
                'degree_certificate': ''
            }
        
            if institutes is not None:
                
                for institute in institutes:
                    if 'institute_id' in institute:
                        if not EmployeeEducations.objects.filter(id = institute['institute_id']).exists():
                            response['code'] = 400
                            response['message'] = "No Emergency institute exists at this id"
                            return response
                        institute_array['id'] = institute['institute_id']


                    institute_array['employee'] = emp.id 
                    if 'degree_type' in institute:
                        institute_array['degree_type'] = institute['degree_type']
                    if 'institutes' in institute:
                        institute_array['institutes'] =  institute['institutes']
                    if 'degree_title' in institute:
                        institute_array['degree_title'] = institute['degree_title']
                    if 'duration' in institute:
                        institute_array['duration'] = institute['duration']
                    if 'institute_name' in institute:
                        institute_array['institute_name'] = institute['institute_name']
                    if 'year_of_completion' in institute:
                        institute_array['year_of_completion'] = institute['year_of_completion']
                    if 'degree_certificate' in institute:
                        institute_array['degree_certificate'] = institute['degree_certificate']
                    if 'institute_id' in institute:
                        if EmployeeEducations.objects.filter(id= institute['institute_id'], employee=emp.id).exists():
                            obj = EmployeeEducations.objects.get(id= institute['institute_id'], employee=emp.id)      
                            serializer = EmployeeEducationsViewsetSerializers(obj, data=institute_array, partial=True)
                    else:
                        serializer = EmployeeEducationsViewsetSerializers(data=institute_array)
                    
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        serializer_errors.append(serializer.errors)

                if (len(institutes) == len(serializer_errors)):
                    response['message'] = "No institute data processed, please update it again!"
                elif len(serializer_errors) > 0:
                    response['message'] = "Some of the institute data is processed, please update it again!"
                else:
                    response['message'] = "All of the institute data is processed Successfully."
                    response['code'] = 200
            else:
                response['message'] = "No data found"
                

            return response
        except Exception as e:
            response['code'] = 400
            response['system_error'] = str(e)
            return response


class PreInstituteDataView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        try:
            degree_obj = DegreeTypes.objects.filter(is_active=True)
            degree_serializer = DegreeTypesViewsetSerializers(degree_obj, many=True)

            institute_obj = Institutes.objects.filter(is_active=True)
            institute_serializer = InstitutesViewsetSerializers(institute_obj, many=True)

            data = {'degree_type': degree_serializer.data, 'institutes': institute_serializer.data}

            return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': data, 'message': 'Success', 'system_status_message': ''})

        except Exception as e:
            return exception(e)