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
class SkillCategoriesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = SkillCategories.objects.filter(is_active=True)
    serializer_class = SkillCategoriesViewsetSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if not SkillCategories.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'This Skill category does not exists', 'system_status_message': ''})

            obj = SkillCategories.objects.get(id=pk)
            if obj.is_active == False:
                msg = "This Skill Category is already deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
            obj.is_active = False
            obj.save()
            serializer = SkillCategoriesViewsetSerializers(obj)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Deactivated Successfully', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)


class SkillsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Skills.objects.filter(is_active=True)
    serializer_class = SkillsViewsetSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if not Skills.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'This Skill does not exists', 'system_status_message': ''})

            obj = Skills.objects.get(id=pk)
            if obj.is_active == False:
                msg = "This Skill is already deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
            obj.is_active = False
            obj.save()
            serializer = SkillsViewsetSerializers(obj)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Deactivated Successfully', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)


class ProficiencyLevelsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ProficiencyLevels.objects.filter(is_active=True)
    serializer_class = ProficiencyLevelsViewsetSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if not ProficiencyLevels.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'This Skill does not exists', 'system_status_message': ''})

            obj = ProficiencyLevels.objects.get(id=pk)
            if obj.is_active == False:
                msg = "This Skill is already deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
            obj.is_active = False
            obj.save()
            serializer = ProficiencyLevelsViewsetSerializers(obj)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Deactivated Successfully', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)


class EmployeeSkillsViewset(viewsets.ModelViewSet):
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

            obj = EmployeeSkills.objects.filter(employee__uuid=emp_uuid, employee__organization__id=org_id, employee__is_active = True, is_active = True).order_by('id')
            serializer = EmployeeSkillsViewsetSerializers(obj, many=True)
            return success(serializer.data)

        except Exception as e:
            return exception(e)


    def retrieve(self, request, *args, **kwargs):
        try:
            skill_id = self.kwargs['skill_id']
            emp_uuid = self.kwargs['emp_uuid']
            org_id = None
            
            # This function whether organization is_active or not
            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            # if user is admin
            if data_check['status'] == 400:
                return Response(data_check)
            elif data_check['status'] == 202:
                org_id = data_check['org_id']


            # if Skills exists to that employee at this specific id
            obj = EmployeeSkills.objects.filter(id=skill_id, employee__uuid=emp_uuid, employee__is_active=True,  employee__organization__id = org_id)
            if not obj.exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This employee does not have any skill at this id', 'system_error_message': ''})
            
            if not obj.filter(is_active=True).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This employee skill is deactivated at this id', 'system_error_message': ''})

            obj = EmployeeSkills.objects.get(id = skill_id, employee__uuid=emp_uuid, employee__is_active=True,  employee__organization__id = org_id, is_active=True)
            serializer = EmployeeSkillsViewsetSerializers(obj, many=False)
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
           
            serializer = EmployeeSkillsViewsetSerializers(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
              
            serializer.save()
            
            return successfullyCreated(serializer.data)
        
        except Exception as e:
            return exception(e)

    
    def patch(self, request, *args, **kwargs):
        try:
            skill_id = self.kwargs['skill_id']
            emp_uuid = self.kwargs['emp_uuid']
    
            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            
            if data_check['status'] == 400:
                return Response(data_check)

            emp = Employees.objects.get(uuid=emp_uuid)    
            request.data['employee'] = emp.id

            # if no employee id exists
            if not EmployeeSkills.objects.filter(employee__id=emp.id, id=skill_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': 'No skill exists at this id', 'message': '', 'system_status_message': ''})
            
    
            obj = EmployeeSkills.objects.get(employee__id = emp.id, id=skill_id)
            serializer = EmployeeSkillsViewsetSerializers(obj, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()
            
            return successfullyUpdated(serializer.data)
        
        except Exception as e:
            return exception(e)


    def delete(self, request, *args, **kwargs):
        try:
            skill_id = self.kwargs['skill_id']
            emp_uuid = self.kwargs['emp_uuid']

            data_check = preEmployeeDataChecks(self, request, emp_uuid)
            if data_check['status'] == 400:
                return Response(data_check)
            elif data_check['status'] == 202:
                emp_org_id = data_check['org_id']
           
            emp = Employees.objects.get(uuid=emp_uuid)    
            request.data['employee'] = emp.id
            
        
            # if active emergency contact exists to that employee at this specific id
            if not EmployeeSkills.objects.filter(id = skill_id, employee__id=emp.id, employee__organization__id = emp_org_id).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This employee does not have any skill at this id', 'system_error_message': ''})

            obj = EmployeeSkills.objects.get(id=skill_id, employee__id=emp.id, employee__organization__id = emp_org_id)
            if obj.is_active == False:
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This skill is already deactivated', 'system_status_message': ''})

            obj.is_active = False
            obj.save()
            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT, 'data': '', 'message': 'Successfully Deleted', 'system_status_message': ''})
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

class PreSkillDataView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        try:
            skill_categories_obj = SkillCategories.objects.filter(is_active=True)
            skill_categories_serializer = SkillCategoriesViewsetSerializers(skill_categories_obj, many=True)

            skills_obj = Skills.objects.filter(is_active=True).order_by('title')
            skills_serializer = SkillsViewsetSerializers(skills_obj, many=True)

            proficiency_level_obj = ProficiencyLevels.objects.filter(is_active=True).order_by('level')
            proficiency_level_serializer = ProficiencyLevelsViewsetSerializers(proficiency_level_obj, many=True)

            data = {'skills': skills_serializer.data, 'skill_category': skill_categories_serializer.data, 'proficiency_level': proficiency_level_serializer.data}

            return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': data, 'message': 'Success', 'system_status_message': ''})

        except Exception as e:
            return exception(e)