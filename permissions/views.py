from rest_framework import viewsets
from rest_framework import generics
from django.contrib.contenttypes.models import ContentType
from helpers.status_messages import errorMessage, exception, success, serializerError
from helpers.custom_permissions import IsAuthenticated, DoesOrgExists
from helpers.decode_token import decodeToken
from roles.models import Roles
from roles.serializers import PreDataRolesSerializers
from .models import AppPermissions
from .serializers import AppPermissionsViewsetSerializers, ContentTypeSerializers



class AppPermissionsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def pre_data(self, request, *args, **kwargs):
        try:
            token = decodeToken(self, request)
            organization_id = token['organization_id']
            content_query = ContentType.objects.filter().order_by('app_label').distinct('app_label')
            serializer = ContentTypeSerializers(content_query, many=True)


            role_query = Roles.objects.filter(is_active=True, organization=organization_id)
            role_serializer = PreDataRolesSerializers(role_query, many=True)

            data = {'content_type': serializer.data, 'role': role_serializer.data}

            return success(data)

        except Exception as e:
            return exception(e)


    def list(self, request, *args, **kwargs):
        try:
            token = decodeToken(self, request)
            organization_id = token['organization_id']
            role_id = self.kwargs['role_id']
            permission_query = AppPermissions.objects.filter(role=role_id, role__organization=organization_id, is_active=True) 
            serializer = AppPermissionsViewsetSerializers(permission_query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def app_permissions(self, request, *args, **kwargs):
        try:
            token = decodeToken(self, request)
            organization_id = token['organization_id']

            # Get roles 
            if not 'role' in request.data:
                return errorMessage('Role is a required field')

            role_id = request.data['role']
            role_query = Roles.objects.filter(id=role_id, organization=organization_id)
            if not role_query.exists():
                return errorMessage('No role exists at this id')
            
            role = role_query.get()
            role_id = role.id
            
            if not 'content_type' in request.data:
                return errorMessage('content_type is a required field')

            content_type_id = request.data['content_type']
            content_type_query = ContentType.objects.filter(id = content_type_id)
            if not content_type_query.exists():
                return errorMessage('No content type exists at this id')
            # print(content_type_query)
            content_type_obj = content_type_query.first()
            app_name = content_type_obj.app_label
            app_permissions = AppPermissions.objects.filter(content_type__app_label=app_name, role=role_id, role__organization=organization_id, is_active=True)
            if app_permissions.exists():
                app_permission = app_permissions.get()
                serializer = AppPermissionsViewsetSerializers(app_permission, data=request.data, partial=True)
            else:
                serializer  = AppPermissionsViewsetSerializers(data=request.data)

            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

class PrePermissionsDataView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, DoesOrgExists]

    def get(self, request, *args, **kwargs):
        try:
            token = decodeToken(self, request)
            organization_id = token['organization_id']
            print(organization_id)
            content_query = ContentType.objects.filter().order_by('app_label').distinct('app_label')
            serializer = ContentTypeSerializers(content_query, many=True)


            role_query = Roles.objects.filter(is_active=True, organization=organization_id)
            role_serializer = PreDataRolesSerializers(role_query, many=True)

            data = {'content_type': serializer.data, 'role': role_serializer.data}

            return success(data)
        except Exception as e:
            return exception(e)


    # def app_permission(self, request, *args, **kwargs):
    #     try:
    #         # Get groups 
    #         if not 'group' in request.data:
    #             return errorMessage('Group is a required field')

    #         group_id = request.data['group']
    #         group_query = Group.objects.filter(id=group_id)
    #         if not group_query.exists():
    #             return errorMessage('No group exists at this id')
    #         group = group_query.get()
            
    #         if not 'content_type' in request.data:
    #             return errorMessage('No content type exists at this id')

    #         content_type_id = request.data['content_type']
    #         content_type_query = ContentType.objects.filter(id = content_type_id)
    #         if not content_type_query.exists():
    #             return errorMessage('No content type exists at this id')
    #         content_type_obj = content_type_query.get()
    #         app_name = content_type_obj.app_label
    #         view = None
    #         edit=None
    #         add=None
    #         delete=None
    #         perm = Permission.objects.filter(content_type__app_label=app_name)
    #         if not perm.exists():
    #             return successMessage('This permission does not exists')
            
    #         if 'can_view' in request.data:
    #             view = request.data['can_view']
    #             view_permissions = perm.filter(codename__startswith='view_')
    #             for view_perm in view_permissions:
    #                 if view == "True": 
    #                     group.permissions.add(view_perm)
    #                 elif view == "False":
    #                     group.permissions.remove(view_perm)
                    
    #         if 'can_edit' in request.data:
    #             edit = request.data['can_edit']
    #             edit_permissions = perm.filter(codename__startswith='change_')
    #             for edit_perm in edit_permissions:
    #                 if edit == "True":
    #                     group.permissions.add(edit_perm)
    #                 elif edit == "False":
    #                     group.permissions.remove(edit_perm)

    #         if 'can_add' in request.data:
    #             add = request.data['can_change']
    #             add_permissions = perm.filter(codename__startswith='add_').first()
    #             for add_perm in add_permissions:
    #                 if add == "True":
    #                     group.permissions.add(add_perm)
    #                 elif add == "False":
    #                     group.permissions.remove(add_perm)

    #         if 'can_delete' in request.data:
    #             delete = request.data['delete']
    #             delete_permissions = perm.filter(codename__startswith='delete_').first()
    #             for delete_perm in delete_permissions:
    #                 if delete == "True":
    #                     group.permissions.add(delete_perm)
    #                 elif delete == "False":
    #                     group.permissions.remove(delete_perm)
 
    #         if view == None and add == None and delete == None and edit == None:
    #             return errorMessage("No permission added")
            
    #         group.save()
    #         return successMessage("Successfully assigned the permission to the respective groups")
        
    #     except Exception as e:
    #         return exception(e)
        





    # assign group to the user
    # def assign_group(self, request, *args, **kwargs):
    #     try:
    #         token = decodeToken(self, request)
    #         organization_id = token['organization_id']
    #         role_id = token['role_id']

    #         if organization_id == None:
    #             return errorMessage('No organization belong to this user')
    #         elif role_id == None:
    #             return errorMessage('No role belong to this user')

    #         role_obj = Roles.objects.get(id=role_id)
    #         role_title = role_obj.title.lower()

    #         upper_management = ['ceo', 'cto']
    #         admin = ['hr', 'admin']
    #         developers = ['developer', 'graphics designer', 'sqa', 'scrum']
    #         user = request.user

    #         if role_title in upper_management:
    #             group = Group.objects.get(name='Upper_Management')
    #         elif role_title in admin:
    #             group = Group.objects.get(name='HR')
    #         elif role_title in developers:
    #             group = Group.objects.get(name='Developers')
    #         else:
    #             return errorMessage("This employee already belong to the group")

          
    #         if not group.user_set.filter(id=user.id).exists():
    #             group.user_set.add(user)
    #         else:
    #             return errorMessage("Permission already exists")
            
    #         return successMessage("Successfully assigned to the group")
    #     except Exception as e:
    #         return exception(e)
        
    # def group_permissions(self, request, *args, **kwargs):
    #     try:
    #         # Define permissions
    #         multiple_view = Permission.objects.filter(codename__startswith='view_').order_by('id')
    #         multiple_edit = Permission.objects.filter(codename__startswith='change_').order_by('id')
    #         multiple_delete = Permission.objects.filter(codename__startswith='delete_').order_by('id')
    #         multiple_post = Permission.objects.filter(codename__startswith='add_').order_by('id')

    #         # Get groups
    #         upper_management_group = Group.objects.get(name='Upper_Management')
    #         hr_group = Group.objects.get(name='HR')
    #         developers_group = Group.objects.get(name='Developers')


    #         # If the group already exists, remove old permissions and add new ones
    #         upper_management_group.permissions.clear()
    #         hr_group.permissions.clear()
    #         developers_group.permissions.clear()
            
    #         # for can_view in multiple_view:
    #         #     upper_management_group.permissions.add(can_view)
    #         #     hr_group.permissions.add(can_view)
    #         #     developers_group.permissions.add(can_view)
    #         #     # saving the permissions
    #         #     upper_management_group.save()
    #         #     hr_group.save()
    #         #     developers_group.save()

    #         # for can_edit in multiple_edit:
    #         #     upper_management_group.permissions.add(can_edit)
    #         #     hr_group.permissions.add(can_edit)
    #         #     # saving the permissions
    #         #     upper_management_group.save()
    #         #     hr_group.save()
    #         #     developers_group.save()

    #         # for can_post in multiple_post:
    #         #     hr_group.permissions.add(can_post)
    #         #     # saving the permissions
    #         #     upper_management_group.save()
    #         #     hr_group.save()
    #         #     developers_group.save()

    #         # for can_delete in multiple_delete:
    #         #     upper_management_group.permissions.add(can_delete)
    #         #     hr_group.permissions.add(can_delete)
    #         #     # saving the permissions
    #         #     upper_management_group.save()
    #         #     hr_group.save()
    #         #     developers_group.save()


            
    #         # You can also add or remove individual permissions from a group like this:
    #         # upper_management_group.permissions.add(can_view)
    #         # hr_group.permissions.remove(can_view)

    #         return successMessage("Successfully assigned the permissions to the respective groups")
        
    #     except Exception as e:
    #         return exception(e)