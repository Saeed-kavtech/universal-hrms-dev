from urllib.parse import urlencode
from django.forms import IntegerField
from django.http import JsonResponse
import requests
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from helpers.custom_permissions import IsSuperUser
from helpers.decode_token import decodeToken
from helpers.renderers import Renderer
from organizations.models import *
from training.models import Training
from training.serializers import ListTrainingViewSetSerializer
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
# import numpy as np
from helpers.status_messages import *
import json
from .staff_classification_views import StaffClassificationViewset
from departments.models import GroupHeads, Departments
from positions.models import Positions
from departments.serializers import GroupHeadsOrgSerializer, DepartmentsOrgSerializer
from positions.serializers import PositionsOrgSerializers
from logs.views import UserLoginLogsViewset
# Create your views here.

class OrganizationViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Organization.objects.all()

    def list(self, request, *args, **kwargs):
        try:
            obj = Organization.objects.filter(is_active=True).order_by('name')
            serializer = OrganizationAndLocationSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def retrieve(self, request, pk=None):
        try:
            if Organization.objects.filter(id=pk).exists():
                obj = Organization.objects.get(id=pk)
                if obj.is_active == False:
                    msg = "Please update the organization status to active"
                    return Response({'status':400, 'system_status': '', 'message': msg, 'data': '', 'system_error_message': ''})
                serializer = OrganizationAndLocationSerializers(obj, many=False)
                return success(serializer.data)
            else:
                return nonexistent(var = 'Organization')
        except Exception as e:
            return exception(e)
            

    def create(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            is_admin = request.user.is_admin
            # if 'created_by' in request.data:
            request.data._mutable = True
            request.data['created_by'] = user_id
            if request.user.is_admin==True:
                request.data['user'] = user_id
            request.data._mutable = False
            
            print('add _mutable')

            user_obj = HrmsUsers.objects.get(id=user_id)

            # This variable stores user id of the admin user. This admin user will get assigned organization
            admin_id = None

            if 'user' in request.data:
                admin_id = request.data['user']

            if is_admin == True and admin_id == None:
                admin_id = user_id
             
             
            if admin_id is not None:
                # This checks whether organization exists at this id or not
                if not HrmsUsers.objects.filter(id=admin_id).exists():
                    return Response({'status': 400, 'system_status': status.HTTP_404_NOT_FOUND, 'data': '', 'message': 'No user exists at this index', 'system_error_message': ''})

                # superuser cannot assign organization to a superuser
                admin_obj = HrmsUsers.objects.get(id=admin_id)
                if admin_obj.is_superuser:
                    return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Superuser cannot assign the organization to himself or to another superuser', 'system_error_message': ''})

                # Admin user don't have privileges to assign organization to another admin user
                if user_obj.is_admin == True and user_obj.is_superuser == False:
                    if admin_id != user_id:
                        return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Admin could only assign organization to himself', 'system_error_message': ''})

                # This checks whether admin user is already assigned to some organization or not
                org_obj = Organization.objects.filter(user__id=admin_id, is_active=True)
                org_count = org_obj.count()
                if user_obj.user_level == 1:
                    if org_count >= 1:
                        return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Organization is already assigned to the user', 'system_error_message': ''})
                elif user_obj.user_level == 2:
                    if org_count >= 1:
                        return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Right now you do not have access to multiple organization', 'system_error_message': ''})

            print('serializer start')
            serializer = OrganizationSerializers(data=request.data)

            if serializer.is_valid():
                org = serializer.save()
                if request.user.is_admin==True:
                    print('assign user')
                    org.user=user_obj
                    org.save()
                    print('user assigned')
                    user_log = UserLoginLogsViewset().userLogin(user_obj.id)

                # now get the locations data of organization.

                locations_data = request.data.get('locations')

                # process the location data

                location_result = self.cuLocation(org, locations_data)

                message = f"Organization successfully added and {location_result['message']}".format(
                    location_result)

                obj = Organization.objects.get(id=org.id)
                org_serializer = OrganizationAndLocationSerializers(
                    obj, many=False)

                return Response({'status': 200, 'system_status': status.HTTP_201_CREATED, 'data': org_serializer.data, 'message': message, 'system_status_message': ''})
            else:
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': '', 'system_status_message': serializer.errors})
        except Exception as e:
            return exception(e)


    def partial_update(self, request, pk):
        try:
            admin_id = request.user.id
            pk = self.kwargs['pk']
           
            #checks whether Organization id exists or not
            if not Organization.objects.filter(id=pk).exists():
                return nonexistent(var = 'Organization')
           
            # requested organization object
            organization = Organization.objects.get(id=pk)
            # currently logged user data
            user_obj = HrmsUsers.objects.get(id=admin_id)
            
            # admin user cannot assign to another admin user
            if user_obj.is_admin == True and user_obj.is_superuser == False:
                if admin_id != organization.user.id:
                    return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Admin do not have privileges to update another admin user', 'system_error_message': ''})
            
            serializer = UpdateOrganizationSerializers(organization, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'SerializerError', 'system_status_message': serializer.errors})
                
            # updated status 
            org_updated_status = serializer.validated_data.get('is_active')
        
            # old status values
            org_old_status = organization.is_active
            
            # Current organization belongs to the following user_id
            user_id = None
            if organization.user is not None:
                user_id = organization.user.id
    
            # if status does not exist
            if org_updated_status is None:
                org_updated_status = org_old_status
            
            # if user_id is none. This means organization is unassigned
            if user_id is not None:
                # if organization is_active status is false. Then user could edit the organization without any restrictions
                if org_updated_status == True:
                
                    org_obj = Organization.objects.filter(user__id=user_id, is_active=True)
                    org_count = org_obj.count() 
                    org_count -= org_obj.filter(id=organization.id).count()

                    # checks whether user is single level user or not
                    hrmsuser = HrmsUsers.objects.get(id=user_id)
                    if hrmsuser.user_level == 1:
                        # One organization is current organization, and if some other active organization exists then user is forbid to activate another organization
                        if org_count >= 1:
                            return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Organization is already assigned to the user', 'system_error_message': ''})
                    elif hrmsuser.user_level == 2:
                        if org_count >= 1:
                            return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Right now you do not have access to multiple organization', 'system_error_message': ''})
            

            serializer.save()

            # now get the locations data of organization.
            locations_data = request.data.get('locations') or None

            # process the location data
            location_result = self.cuLocation(organization, locations_data)

            message = f"Organization successfully added and {location_result['message']}".format(
                location_result)

            obj = Organization.objects.get(id=organization.id)
            org_serializer = OrganizationAndLocationSerializers(obj, many=False)

            return Response({'status': 200, 'system_status_message': status.HTTP_200_OK, 'data': org_serializer.data, 'message': message, 'system_error_message': ''})
        

                
        except Exception as e:
            return exception(e)


    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            is_superuser = request.user.is_superuser
            # only superuser has the previlages to change the status of the organization
            if not is_superuser == True:
                return Response({'status': 400,  'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Only superuser can deactivate the organization', 'system_status_message': ''})

            # if organization does not exists
            if not Organization.objects.filter(id=pk).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This Organization does not exists', 'system_status_message': ''})
                
            obj = Organization.objects.get(id=pk)
            
            # checks whether organization is already deactivated
            if obj.is_active == False:
                msg = "Organization is already deactivated"
                return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': '', 'message': msg, 'system_status_message': ''})
            
            obj.is_active = False
            obj.save()

            return Response({'status': 200, 'system_status': status.HTTP_204_NO_CONTENT, 'data': '', 'message': 'Deleted Successfully', 'system_status_message': ''})
            
        except Exception as e:
            return exception(e)

    def cuLocation(self, organization, locations_data):
        
        loc_errors = []
        locations = []
        response = {'message':'', 'location_errors':''}

        if isinstance(locations_data, str):
            locations_data = json.loads(locations_data)
            locations.append(locations_data)
        else:
            locations = locations_data
        
        try:     
            location_array = {'organization':'', 'address':'', 'city_name':'', 'zipcode':'', 'longitute':'', 'latitute':''}
            if locations is not None:
                for location in locations:
                    
                    org_location = None
                    # check if location_id is none or null then create the location
                    # if 'location_id' in location:
                    if OrganizationLocation.objects.filter(organization__id=organization.id).exists():
                        org_location = OrganizationLocation.objects.filter(organization__id=organization.id).last()
                    # elif location['location_id'] is None or location['location_id'] == '0':
                    #     pass
                    else:
                        # here update the location error
                        msg = "Location with this address: {} does not exist".format(location['address'])
                        loc_errors.append(msg)
                        # continue

                    location_array['organization'] = organization.id 
                    if 'address' in location:
                        location_array['address'] = location['address']
                    if 'zipcode' in location:
                        location_array['zipcode'] = location['zipcode']

                    location_array['city_name'] = location['city_name'] or 'Lahore'
                    if 'longitute' in location:
                        location_array['longitute'] = location['longitute']
                    if 'latitute' in location:
                        location_array['latitute'] = location['latitute']
                    
                    if org_location is not None:
                        serializer = OrganizationLocationSerializers(org_location, data = location_array, partial=True)
                    else:
                        serializer = OrganizationLocationSerializers(data = location_array)
                    
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        loc_errors.append("Location with this address {} has error({})".format(location['address'], serializer.errors))
                
                if(len(locations)==len(loc_errors)):
                    response['message'] = "No location data processed, please update it again!"
                elif len(loc_errors)>0:
                    response['message'] = "Some of the location is not updated, please update it again!"
                else: 
                    response['message'] = "All organization location data updated Successfully."

            else: 
                response['message'] = 'No location data found.'
                loc_errors.append("No location data found.")


        except Exception as e:
            response['message'] = "Location process through error, please update it again!"
            loc_errors.append("Location process has error({})".format(str(e)))

        response['location_errors'] = loc_errors
        return response
        


    def organizationObjects(self, request, pk, *args, **kwargs):
        pk = self.kwargs['pk']
        data = {}
        try:
            if Organization.objects.filter(pk=pk).exists():
                organization = Organization.objects.get(id=pk)

                staff_classifications_obj = StaffClassification.objects.filter(organization=organization.id, is_active=True).order_by('level')
                staff_classifications = StaffClassificationOrgSerializers(staff_classifications_obj, many=True)
                data['staff_classifications'] = staff_classifications.data

                groupheads_obj = GroupHeads.objects.filter(organization=organization.id, is_active=True)
                groupheads = GroupHeadsOrgSerializer(groupheads_obj, many=True)
                data['groupheads'] = groupheads.data

                departments_obj = Departments.objects.filter(grouphead__organization__id=organization.id, is_active=True)
                departments = DepartmentsOrgSerializer(departments_obj, many=True)
                data['departments'] = departments.data

                positions_obj = Positions.objects.filter(staff_classification__organization__id=organization.id, is_active=True).order_by('staff_classification')
                positions = PositionsOrgSerializers(positions_obj, many=True)
                data['positions'] = positions.data

                return Response({'status':200, 'system_status': 200, 'data':data, 'message': 'Success', 'system_error_message': ''})

            else:
                return Response({'status':400,  'system_status': 400, 'data':data, 'message': 'Organization does not exist', 'system_error_message': ''})


        except Exception as e:
            return exception(e)



class DashboardSetupCount(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        try:
            user_organization_id = UserLoginLogsViewset().getUserOrganization(request.user.id)
            if user_organization_id is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            # org = Organization.objects.filter(is_active=True).first()
            organization = Organization.objects.get(id=user_organization_id.id)
            org_id = organization.id
            org_count = 1
            grouphead_count = GroupHeads.objects.filter(organization=org_id, is_active=True).count()
            
            department_count = Departments.objects.filter(grouphead__organization=org_id, is_active=True).count()
            
            staff_count = StaffClassification.objects.filter(organization=org_id, is_active=True).count()

            position_count = Positions.objects.filter(grouphead__organization=org_id, is_active=True).count()
            
            data = {'org_count': org_count,'grouphead_count': grouphead_count, 'staff_count': staff_count, 'department_count': department_count, 'position_count': position_count}
            
            return Response({'status':200, 'system_status':200, 'data': data, 'message': 'Success', 'system_error_message': ''})
            
        except Exception as e:
            return exception(e)
        

class OrganizationApikeysviewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationApikeysSerializer
    # queryset = OrganizationApikeys.objects.all()
    def list(self,request,*args, **kwargs):
        try:
            user_organization_id = UserLoginLogsViewset().getUserOrganization(request.user.id)
            # print(user_organization_id.id)
            # query=OrganizationApikeys.objects.filter(is_active=True)
            queryset = OrganizationApikeys.objects.filter(organization=user_organization_id.id,is_active=True)
            print(queryset)
            if not queryset.exists():
                return errorMessage("Data not exists")
            serializer=OrganizationApikeysSerializer(queryset, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

        
    def create(self, request, *args, **kwargs):
        try:
            user_organization_id = UserLoginLogsViewset().getUserOrganization(request.user.id)
            print(user_organization_id.id)
            required_fields = ['google_api','client_id']
            if not all(field in request.data for field in required_fields):
                    return errorMessageWithData('make sure you have added all required fields','google_api,client_id')

            request.data['organization'] = user_organization_id.id
            existing_data = OrganizationApikeys.objects.filter(organization=user_organization_id.id,is_active=True).first()

            if existing_data:
                # If data already exists, update it
                serializer = OrganizationApikeysSerializer(existing_data, data=request.data)
            else:
                # If data doesn't exist, create new data
                serializer = OrganizationApikeysSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return successMessageWithData("Success", serializer.data)
            else:
                return errorMessage(serializer.errors)

        except Exception as e:
          return exception(e)



class ThirdPartyTokensviewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    def list(self,request,*args, **kwargs):
        try:
            user_organization_id = UserLoginLogsViewset().getUserOrganization(request.user.id)
            # print(user_organization_id.id)
            # query=OrganizationApikeys.objects.filter(is_active=True)
            queryset = ThirdPartyTokens.objects.filter(organization=user_organization_id.id,is_active=True)
            # print(queryset)
            if not queryset.exists():
                return errorMessage("Data not exists")
            serializer=ThirdPartyTokensSerializer(queryset, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

        
    def create(self, request, *args, **kwargs):
        try:
            user_organization_id = UserLoginLogsViewset().getUserOrganization(request.user.id)
            # print(user_organization_id.id)

            required_fields = ['token_type','code','client_id','client_secret','redirect_uri']
            if not all(field in request.data for field in required_fields):
                    return errorMessageWithData('make sure you have added all required fields','token_type,code,client_id,client_secret,redirect_uri')

            api_url = "https://zoom.us/oauth/token"

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }

            body = {
                "grant_type": request.data['token_type'],
                  
                "client_id": request.data['client_id'],  
                "client_secret": request.data['client_secret'],
                "redirect_uri":request.data['redirect_uri'],
                "code": request.data['code'],
            }
            encoded_data = urlencode(body)
            # print(encoded_data)
            response = requests.post(api_url, headers=headers,data=encoded_data)

            if response.status_code == 201 or response.status_code == 200:
                        data = response.json()
                        request.data['access_token']=data['access_token']
                        request.data['token_type']=data['token_type']
                        request.data['refresh_token']=data['refresh_token']
                        request.data['expires_in']=data['expires_in']
                        request.data['scope']=data['scope']
                        request.data['organization'] = user_organization_id.id
                        serializer = ThirdPartyTokensSerializer(data=request.data)

                        if serializer.is_valid():
                            serializer.save()
                            return successMessageWithData("Success", serializer.data)
                        else:
                            return errorMessage(serializer.errors)

            else:
               return errorMessageWithData("Failed",response.text)
        except Exception as e:
          return exception(e)

  

    def update_tokens(self, request, *args, **kwargs):
        try:
            user_organization_id = UserLoginLogsViewset().getUserOrganization(request.user.id)
            # required_fields = ['token_type']
            # if not all(field in request.data for field in required_fields):
            # print("Test")
            #         return errorMessageWithData('make sure you have added all required fields','token_type')
            existing_data =ThirdPartyTokens.objects.filter(organization=user_organization_id.id,is_active=True).last()
       
            if existing_data is None:
                return errorMessage("Data not exists")

            api_url = "https://zoom.us/oauth/token"

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }

            # JSON data for the POST request
            body = {
                "grant_type":'refresh_token', 
                "client_id":existing_data.client_id,  
                "client_secret": existing_data.client_secret,
                "refresh_token":existing_data.refresh_token
            }
            encoded_data = urlencode(body)
            response = requests.post(api_url, headers=headers,data=encoded_data)

            if response.status_code == 201 or response.status_code == 200:
                        data = response.json()

                        refresh_data={
                            "refresh_token":data['refresh_token'],
                            "access_token":data['access_token']
                        }
                        
                        serializer = ThirdPartyTokensSerializer(existing_data,data=refresh_data,partial=True)
                        if serializer.is_valid():
                            serializer.save()
                            return successMessageWithData("Success", serializer.data)
                        else:
                            return errorMessage(serializer.errors)

            else:
               return errorMessageWithData("Failed", status=response.text)

        except Exception as e:
            return exception(e)
        


class OrganizationModuleAccessViewset(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated,IsSuperUser]
    queryset=OrganizationModuleAccess.objects.all()
    serializer_class=OrganizationModuleAccessSerializer

    def create(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)

            
            user_id = request.user.id
            
            required_fields = ['title','level','is_default','is_allowed']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all required fields','title,level,is_default,is_allowed')
            
            is_default=request.data['is_default']
            check_query=True
            if not is_default:
               if 'organization' not in request.data:
                   return errorMessage('Organization is required for custom modules')
               organization_id=request.data['organization']
            
               check_query=self.queryset.filter(organization=organization_id,is_default=False,is_active=True)

            else:
               check_query=self.queryset.filter(organization__isnull=True,is_default=True,is_active=True)

            
            if check_query.exists():

                    if check_query.filter(title=request.data['title']).exists():
                        return errorMessage("This status title already exists")
                    
                    elif check_query.filter(level=request.data['level']).exists():
                        return errorMessage("This level  already assign to other title")
                
            request.data['created_by'] = user_id

            serializer=self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)

        except Exception as e:
          return exception(e)
        
    def list(self, request, *args, **kwargs):
        try:
            organization_id=request.data.get('organization',None)
            check_query=self.queryset.filter(is_active=True)
            if organization_id:
                check_query=check_query.filter(organization=organization_id)
            serializer =self.serializer_class(check_query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']

            query = self.queryset.filter(id=pk)
            if not query.exists():
                return errorMessage('Module does not exists')
            if not query.filter(is_active=True).exists():
                return errorMessage('Module is already deactivated at this id')
            
            obj = query.get()
 
            obj.is_active=False
            obj.save()

            return successMessage('Module deactivated successfully')
        except Exception as e:
            return exception(e)
        
    
        

    

    
   