from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from helpers.custom_permissions import IsSuperUser, IsSuperUserOrAdmin
from organizations.serializers import OrganizationSerializers
from .serializers import *
from django.contrib.auth import authenticate
from helpers.renderers import Renderer
from .models import HrmsUsers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework import viewsets
from helpers.status_messages import *
from organizations.models import Organization,SubadminOrganization
from .serializers_users import *


# User would be able to list user based on their usertype and status
class HrmsUsersListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    prenderer_classes = [Renderer]

    def list(self, request, *args, **kwargs):
        try:
            uid = request.user.id
            status = request.GET.get('status')
            # usertype = request.GET.get('usertype')

            # obj = HrmsUsers.objects.get(id=uid)
            if status not in ['all', 'active', 'inactive']:
                status =  'all'
            # if user is superuser
            # if obj.is_superuser == True:
                # if usertype == 'superuser' or usertype == '' or usertype == None:
            if status == 'all':
                obj_user = HrmsUsers.objects.filter(is_superuser=False, is_admin=True)

            elif status == 'active':
                obj_user = HrmsUsers.objects.filter(
                    is_superuser=False, is_admin=True, is_active=True)

            elif status == 'inactive':
                obj_user = HrmsUsers.objects.filter(
                    is_superuser=False, is_admin=True, is_active=False)

            serializer = HrmsUsersSerializers(obj_user, many=True)
            return Response({'status': 200, 'system_status': '', 'data': serializer.data, 'message': 'Success', 'system_error_message': ''})
        except Exception as e:
            return exception(e)




            #     elif usertype == 'admin':
            #         if status == 'all' or status == '' or status == None:
            #             obj_user = HrmsUsers.objects.filter(
            #                 is_superuser=False, is_admin=True)

            #         elif status == 'active':
            #             obj_user = HrmsUsers.objects.filter(
            #                 is_superuser=False, is_admin=True, is_active=True)

            #         elif status == 'inactive':
            #             obj_user = HrmsUsers.objects.filter(
            #                 is_superuser=False, is_admin=True, is_active=False)

            #         serializer = HrmsUsersSerializer(obj_user, many=True)
            #         return Response({'status': 200, 'system_status': '', 'data': serializer.data, 'message': 'Success', 'system_error_message': ''})
            #     # elif usertype == 'employee':
            #     #     obj_user = HrmsUsers.objects.filter(is_admin=False, is_employee=True)
            #     #     serializer = HrmsUsersSerializer(obj_user, many=True)
            #     #     return Response({'status': 200, 'system_status': '', 'data': serializer.data, 'message': 'Success', 'system_error_message': '' })
            #     elif usertype == 'all':
            #         if status == 'all' or status == '' or status == None:
            #             obj_user = HrmsUsers.objects.all()
            #         elif status == 'active':
            #             obj_user = HrmsUsers.objects.filter(is_active=True)
            #         elif status == 'inactive':
            #             obj_user = HrmsUsers.objects.filter(is_active=False)

            #         serializer = HrmsUsersSerializer(obj_user, many=True)
            #         return Response({'status': 200, 'system_status': '', 'data': serializer.data, 'message': 'Success', 'system_error_message': ''})
            #     else:
            #         return Response({'status': 400, 'system_status': '', 'data': '', 'message': 'Wrong usertype entered', 'system_error_message': ''})

            # # if user is admin
            # elif obj.is_superuser == False and obj.is_admin == True:
            #     if usertype == 'superuser':
            #         return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Admin do not have the required previleges to access the superusers', 'system_error_message': ''})

            #     elif usertype == 'admin' or usertype == '' or usertype == None:
            #         obj_user = HrmsUsers.objects.filter(
            #             is_superuser=False, is_admin=True)
            #         serializer = HrmsUsersSerializer(obj_user, many=True)
            #         return Response({'status': 200, 'system_status': '', 'data': serializer.data, 'message': 'Success', 'system_error_message': ''})
            #     # elif usertype == 'employee':
            #     #     obj_user = HrmsUsers.objects.filter(is_admin=False, is_employee=True)
            #     #     serializer = HrmsUsersSerializer(obj_user, many=True)
            #     #     return Response({'status': 200, 'system_status': '', 'data': serializer.data, 'message': 'Success', 'system_error_message': '' })
            #     elif usertype == 'all':
            #         obj_user = HrmsUsers.objects.filter(is_superuser=False)
            #         serializer = HrmsUsersSerializer(obj_user, many=True)
            #         return Response({'status': 200, 'system_status': '', 'data': serializer.data, 'message': 'Success', 'system_error_message': ''})
            #     else:
            #         return Response({'status': 400, 'system_status': '', 'data': '', 'message': 'Wrong usertype entered', 'system_error_message': ''})

            # if user is employee
            # elif obj.is_admin == False and obj.is_employee == True:
            #     if usertype == 'superuser':
            #         return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Employee do not have the required previleges to access the superusers', 'system_error_message': '' })

            #     elif usertype == 'admin':
            #         return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Employee do not have the required previleges to access the superusers', 'system_error_message': '' })

            #     elif usertype == 'employee' or  usertype == '' or usertype == None or usertype == 'all'  :
            #         obj_user = HrmsUsers.objects.filter(is_admin=False, is_employee=True)
            #         serializer = HrmsUsersSerializer(obj_user, many=True)
            #         return Response({'status': 200, 'system_status': '', 'data': serializer.data, 'message': 'Success', 'system_error_message': '' })
            #     else:
            #         return Response({'status': 400, 'system_status': '', 'data': '', 'message': 'Wrong usertype entered', 'system_error_message': '' })

        

# Admin user is created via this API


class RegisterHrmsAdminView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    prenderer_classes = [Renderer]

    def post(self, request):
        try:
            if 'email' in request.data:
                email = request.data['email'].lower()
                request.data['email'] = email
            
            if HrmsUsers.objects.filter(email = email):
                return errorMessage('This email already exists')
            
            serializer = HrmsUserRegisterationSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': serializer.data, 'message': "Successfully Created", 'system_error_message': ''})
            else:
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': 'Validation error', 'message': serializer.errors, 'system_error_message': ''})

        except Exception as e:
            return exception(e)


# Retrieve, update and delete any type of user
class HrmsUsersGenericView(generics.RetrieveUpdateAPIView):
    # permission_classes = [IsAuthenticated]
    # renderer_classes = [Renderer]

    def retrieve(self, request, *args, **kwargs):
        try:
            pk = request.user.id
            obj = HrmsUsers.objects.get(id=pk)
            if obj.is_active == False:
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Activate the user first', 'system_error_message': ''})
            serializer = HrmsUsersSerializers(obj)
            return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': serializer.data, 'message': 'Success', 'system_error_message': ''})
        except Exception as e:
            return exception(e)

    def update(self, request, pk=None):
        message = 'Update function is not offered in this path.'
        return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': message, 'system_error_message': ''})

    def patch(self, request, *args, **kwargs):
        try:
            pk = request.user.id
            obj = HrmsUsers.objects.get(id=pk)
            if obj.is_active == False:
                return Response({'status': 400, 'data': serializer.data, 'message': 'Activate the user first'})
            if obj.is_superuser == False and obj.is_admin == True:
                serializer = HrmsUsersSerializers(obj, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': serializer.data, 'message': 'Updated Successfully', 'system_error_message': ''})
                else:
                    return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'message': serializer.errors, 'system_error_message': ''})
            elif obj.is_superuser == True:
                serializer = HrmsUsersUpdateSerializers(obj, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return successfullyUpdated(data=serializer.data)
                else:
                    return serializerError(data=serializer.errors)
            # elif obj.is_admin == False:
            #     pass
            else:
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'User does not have the required privileges to update', 'system_error_message': ''})
        except Exception as e:
            return exception(e)

    def delete(self, request, *args, **kwargs):
        try:
            pk = request.user.id
            obj = HrmsUsers.objects.get(id=pk)
            if obj.is_superuser == True:
                msg = "Superuser can't get deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_error_message': ''})
            if obj.is_active == False:
                msg = "This User is already deactivated"
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_error_message': ''})
            obj.is_active = False
            obj.save()
            serializer = HrmsUsersSerializers(obj)
            return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': serializer.data, 'message': 'Successfully deactivated', 'system_error_message': ''})

        except Exception as e:
            return exception(e)


class OrganizationAssignmentViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsSuperUser]
    renderer_classes = [Renderer]

    # superuser could view all the assigned organization to the admin user
    def list(self, request, *args, **kwargs):
        try:
            obj = Organization.objects.filter(
                user__is_superuser=False, user__is_admin=True)
            serializer = AssignedOrganizationListSerializers(obj, many=True)
            return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': serializer.data, 'message': 'Success', 'system_error_message': ''})
        except Exception as e:
            return exception(e)

    # superuser could retrieve all the assigned organizations related to the  specific admin user
    def retrieve(self, request, *args, **kwargs):
        try:
            uid = self.kwargs['uid']
            org_id = self.kwargs['org_id']
            status = request.GET.get('status')

            if not Organization.objects.filter(id=org_id).exists():
                return Response({'status': 400, 'system_status': 404, 'data': '', 'message': 'Organization does not exists', 'system_error_message': ''})

            if not Organization.objects.filter(user__id=uid).exists():
                return Response({'status': 400, 'system_status': 404, 'data': '', 'message': 'No user belongs to this organization', 'system_error_message': ''})

            if status not in ['all', 'active', 'inactive']:
                status = 'all'
            
            if status == 'all':
                obj = Organization.objects.get(id=org_id, user__id=uid)
            elif status == 'active':
                obj = Organization.objects.get(id=org_id, user__id=uid, is_active=True)
            elif status == 'inactive':
                obj = Organization.objects.get(id=org_id,
                    user__id=uid, is_active=False)

            serializer = AssignedOrganizationListSerializers(obj)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Success', 'system_error_message': ''})
        except Exception as e:
            return exception(e)

    # Assigning Organization to Admin user
    def post(self, request, *args, **kwargs):
        try:
            uid = self.kwargs['uid']

            obj = Organization.objects.filter(user__id=uid, is_active=True)
            hrmsuser = HrmsUsers.objects.get(id=uid)
            if not HrmsUsers.objects.filter(id=uid, is_admin=True, is_superuser=False, is_active=True).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Admin user does not exist or inactive at this id', 'system_error_message': ''})

            # if hrmsuser.user_level == 1:
            # print(hrmsuser.id)
            # print(hrmsuser.is_admin)
            org_count = obj.count()
            if org_count > 0:
                return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Organization is already assigned to the user', 'system_error_message': ''})
            # else:
            #     return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Your type is invalid', 'system_error_message': ''})
            
            # if hrmsuser.is_superuser == True:
            #     return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Organization cannot be assigned to the superuser', 'system_error_message': ''})
            # elif hrmsuser.is_admin == False:
            #     return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Organization cannot be assigned to the employee', 'system_error_message': ''})


        
            org_id = self.kwargs['org_id']
            obj_org = Organization.objects.get(id=org_id, is_active=True)
            # print(obj_org)
            if obj_org is not None:
                # if obj_org.user_id in [None, '', 'null']:
                obj_org.user = hrmsuser
                obj_org.save()
                serializer = OrganizationSerializers(obj_org, many=False)
                return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': serializer.data, 'message': 'Successfully Assigned', 'system_error_message': ''})
                # todo can organization assigned to multiple users?
                # return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Organization is already assigned', 'system_error_message': ''})
            else:
                return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Organization does not exist at this id', 'system_error_message': ''})
        except Exception as e:
            return exception(e)
        


    def get_subadminorganization_data(self, request, *args, **kwargs):
            
        try:
            uid = self.kwargs['uid']
            org_id = self.kwargs['org_id']
            status = request.GET.get('status')

            if not SubadminOrganization.objects.filter(organization__id=org_id).exists():
                return Response({'status': 400, 'system_status': 404, 'data': '', 'message': 'Organization does not exists', 'system_error_message': ''})

            if not SubadminOrganization.objects.filter(user__id=uid).exists():
                return Response({'status': 400, 'system_status': 404, 'data': '', 'message': 'No user belongs to this organization', 'system_error_message': ''})

            if status not in ['all', 'active', 'inactive']:
                status = 'all'
            
            if status == 'all':
                obj = SubadminOrganization.objects.get(organization__id=org_id, user__id=uid)
            elif status == 'active':
                obj = SubadminOrganization.objects.get(organization__id=org_id,user__id=uid,is_active=True)
            elif status == 'inactive':
                obj = SubadminOrganization.objects.get(organization__id=org_id,user__id=uid,is_active=False)

            serializer = SubadminOrganizationSerializers(obj)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Success', 'system_error_message': ''})
        except Exception as e:
            return exception(e)


        


    def assign_org_subadmin(self, request, *args, **kwargs):
        try:
            uid = self.kwargs['uid']

            obj = Organization.objects.filter(user__id=uid, is_active=True)
            hrmsuser = HrmsUsers.objects.get(id=uid)
            # print("Test", obj)
            if not HrmsUsers.objects.filter(id=uid, is_admin=True,is_superuser=False, is_active=True).exists():
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Admin not exists or inactive at this id', 'system_error_message': ''})

            org_count = obj.count()
            # print( org_count)
            if org_count > 0:
                return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Organization is already assigned to the user', 'system_error_message': ''})
            

            if hrmsuser.is_subadmin!=True:
                return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'User is not subamdin ', 'system_error_message': ''})

            org_id = self.kwargs['org_id']
            obj_org = Organization.objects.get(id=org_id, is_active=True)


            if obj_org is None:
                
             return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Organization does not exist at this id', 'system_error_message': ''})

            # print(obj_org)
            suborg_query=SubadminOrganization.objects.filter(organization=obj_org,user=hrmsuser,is_active=True)

            if suborg_query.exists():
                return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Organization is already assigned to sub admin user', 'system_error_message': ''})
            
            
            # print("test1")
            
            data={
                    'user':hrmsuser.id,
                    'organization':obj_org.id,
                    'is_active':True
                }
            
            # print(data)
            
            serializer=SubadminOrganizationSerializers(data=data)

            if not serializer.is_valid():
                    return serializerError(serializer.errors)
                

            serializer.save()

            return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': serializer.data, 'message': 'Successfully Assigned', 'system_error_message': ''})
        
            # print(obj_org)
            
        except Exception as e:
            return exception(e)
        



    def update(self, request, *args, **kwargs):
        try:
            message = 'Update function is not offered in this path.'
            return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': message, 'system_error_message': ''})
        except Exception as e:
            return exception(e)

    def patch(self, request, *args, **kwargs):
        pass

    # def destroy(self, request, *args, **kwargs):
    #     try:
    #         org_id = self.kwargs['org_id']
    #         obj_org = Organization.objects.get(id=org_id)
    #         if Organization.objects.filter(id=org_id).exists():
    #             if obj_org.user_id not in [None, '', 'null']:
    #                 obj_org.user_id = None
    #                 obj_org.save()
    #                 serializer = OrganizationSerializers(obj_org, many=False)
    #                 return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': serializer.data, 'message': 'Organization is unassigned', 'system_error_message': ''})
    #             # todo can organization assigned to multiple users?
    #             return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'Organization is already unassigned', 'system_error_message': ''})
    #         else:
    #             return Response({'status': 400, 'system_status': status.HTTP_403_FORBIDDEN, 'data': '', 'message': 'Organization does not exist at this id', 'system_error_message': ''})
    #     except Exception as e:
    #         return exception(e)
