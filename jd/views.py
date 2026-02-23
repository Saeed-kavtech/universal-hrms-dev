from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.response import Response
from .models import JdDescriptions, JdSpecifications
from rest_framework import viewsets
from .serializers import JdDescriptionsSerializers, JdSpecificationsSerializers, CreateJdDescriptionsSerializers
from helpers.status_messages import *

from logs.views import UserLoginLogsViewset
import uuid

class JobDescriptionViewSet(viewsets.ModelViewSet):

    queryset = JdDescriptions.objects.filter(is_active=True)
    serializer_class = JdDescriptionsSerializers
    permission_classes = [IsAuthenticated]

    def list(self, request):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            obj = JdDescriptions.objects.filter(is_active=True, staff_classification__organization__id=user_organization.id).order_by('-id')
            serializer = JdDescriptionsSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request):
        try:
            user_organization_id = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization_id is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            jd_specifications_data_array = {
                'jd': '', 'jd_dimension': '', 'essential': '', 'desirable': ''}
            jd_specifications_data = request.data.get('jd_specifications') or None


            # generating unique job code
            unique_code = str(uuid.uuid4())[:6]
            if JdDescriptions.objects.filter(code=unique_code, staff_classification__organization=user_organization_id.id).exists():
                return errorMessage('This job code already exists. Please contact the administrator or try again')
            request.data['code'] = unique_code

            serializer = CreateJdDescriptionsSerializers(data=request.data)
            if serializer.is_valid():
                serializer.is_active = True
                jd = serializer.save()
                jd_specifications_result = self.jdSpecifications(jd, jd_specifications_data)

                message = f"JD successfully added and {jd_specifications_result['message']}".format(jd_specifications_result)

                job_descriptions = JdDescriptions.objects.get(pk=jd.id)
                jd_data = JdDescriptionsSerializers(job_descriptions, many=False)

                return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': jd_data.data, 'message': message, 'system_status_message': ''})

            else:
                return serializerError(serializer.errors)

        except Exception as e:
            return exception(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            user_organization_id = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization_id is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            if JdDescriptions.objects.filter(id=pk, department__grouphead__organization=user_organization_id).exists():
                obj = JdDescriptions.objects.get(id=pk)
                if obj.is_active == False:
                    msg = "Please update the Job Description status to active"
                    return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': msg, 'system_status_message': ''})
                serializer = JdDescriptionsSerializers(obj, many=False)
                return success(serializer.data)
            else:
                return nonexistent(var='Job Description')
        except Exception as e:
            return exception(e)

    # def update(self, request, pk=None):
    #     message = 'Update function is not offered in this path.'
    #     return Response({'status':403, 'data': '','message': message, 'system_error_message': ''})

    def partial_update(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            user_organization_id = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization_id is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
            if JdDescriptions.objects.filter(id=pk, department__grouphead__organization=user_organization_id).exists():
                obj = JdDescriptions.objects.get(id=pk)
                serializer = CreateJdDescriptionsSerializers(
                    obj, data=request.data, partial=True)
                if serializer.is_valid():
                    jd = serializer.save()

                    jd_specifications_data = request.data.get('jd_specifications')

                    jd_specifications_result = self.jdSpecifications(jd, jd_specifications_data)

                    message = f"JD successfully added and {jd_specifications_result['message']}".format(
                        jd_specifications_result)

                    job_descriptions = JdDescriptions.objects.get(pk=jd.id)
                    jd_data = JdDescriptionsSerializers(job_descriptions, many=False)
                    return successfullyUpdated(jd_data.data)

                else:
                    return serializerError(serializer.errors)
            else:
                return nonexistent(var='Job Description')
        except Exception as e:
            return exception(e)

    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            user_organization_id = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization_id is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            if JdDescriptions.objects.filter(id=pk, department__grouphead__organization=user_organization_id).exists():
                obj = JdDescriptions.objects.get(id=pk)
                if obj.is_active == False:
                    msg = "Job Description is already deactivated"
                    return Response({'status': 200, 'system_status': 200, 'data': '', 'message': msg, 'system_status_message': ''})
                obj.is_active = False
                obj.save()
                serializer = JdDescriptionsSerializers(obj)
                return successfullyDeleted(serializer.data)
            else:
                return nonexistent(var='Job Description')
        except Exception as e:
            return exception(e)

    def jdSpecifications(self, jd, jd_specifications_data):
        spec_errors = []
        specifications = []
        response = {'message': '', 'specification_errors': ''}
        
        if isinstance(jd_specifications_data, str):
            jd_specifications_data = json.loads(jd_specifications_data)
            specifications.append(jd_specifications_data)
        else:
            specifications = jd_specifications_data

        try:
            jd_specifications_data_array = {'jd': '', 'jd_dimension': '', 'essential': '', 'desirable': ''}
            if specifications is not None:
                for jd_specifications in specifications:
                    
                    jd_specifications_data_array['jd'] = jd.id
                    jd_specifications_data_array['jd_dimension'] = jd_specifications['jd_dimension']

                    if 'essential' in jd_specifications:
                        jd_specifications_data_array['essential'] = jd_specifications['essential']
                    if 'desirable' in jd_specifications:
                        jd_specifications_data_array['desirable'] = jd_specifications['desirable']
                    
                    if 'jd_dimension' not in jd_specifications:
                        continue
                    if JdSpecifications.objects.filter(jd=jd.id, jd_dimension=jd_specifications['jd_dimension'], is_active=True).exists():
                        jds_obj = JdSpecifications.objects.get(jd=jd.id, jd_dimension=jd_specifications['jd_dimension'], is_active=True)
                        jd_serializer = JdSpecificationsSerializers(jds_obj, data=jd_specifications_data_array, partial=True)
                    else:
                        jd_serializer = JdSpecificationsSerializers(data=jd_specifications_data_array)

                    if jd_serializer.is_valid():
                        jd_serializer.save()
                        
                    else:
                        spec_errors.append(jd_serializer.errors)

                if (len(specifications) == len(spec_errors)):
                    response['message'] = "No specifications data processed, please update it again!"
                elif len(spec_errors) > 0:
                    response['message'] = "Some of the specifications are not processed, please update it again!"
                else:
                    response['message'] = "All JD Specifications data processed Successfully."

            else:
                
                response["message"] = "No specifications found."
                spec_errors.append("No specifications found.")

        except Exception as e:
            response['message'] = "JD Specifications process through error, please update it again!"
            spec_errors.append("Specifications process has error({})".format(str(e)))

        response['specification_errors'] = spec_errors
        return response
