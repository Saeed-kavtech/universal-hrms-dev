from rest_framework import viewsets
from rest_framework.response import Response
from helpers.status_messages import errorMessage, successMessage, exception, success, serializerError, successfullyCreated, successfullyUpdated
from helpers.custom_permissions import IsAuthenticated
from helpers.decode_token import decodeToken
from .serializers import NavigationsViewsetSerializers, UpdateNavigationsViewsetSerializers, RolesNavigationsViewsetSerializers, UpdateRolesNavigationsViewsetSerializers, NavigationHierarchySerializers
from .models import Navigations, RolesNavigations
from employees.models import *
from roles.models import Roles
from roles.serializers import PreDataRolesSerializers
import json

# Create your views here.
class NavigationsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs): 
        try:
            token = decodeToken(self, request)
            organization_id = token['organization_id']

            root_navigations = Navigations.objects.filter(parent__isnull=True, organization=organization_id, is_active=True)
            # navigation_hierarchy = self.get_navigation_hierarchy(root_navigations)
            serializer = NavigationHierarchySerializers(root_navigations, many=True)

            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def create(self, request, *args, **kwargs):
        try:
            print('here')
            token = decodeToken(self, request)
            organization_id = token['organization_id']

            if not 'title' in request.data:
                return errorMessage('Title is a required field')
            if not 'url' in request.data:
                return errorMessage('url is a required field')
            

            request.data['organization'] = organization_id
            if 'level' in request.data:
                level = request.data.get('level')
            else:
                level = 0

            # check if navigation has level 1 or 2 then it must has level-1 navigation as parent
            if level == 1 or level == 2:
                # must has parent 
                parent_level = level-1
                if not 'parent' in request.data:
                    return errorMessage('Level 1 navigation must has level 0 navigation as parent')
                parent = request.data.get('parent')
                # print(parent)
                #now check is this parent belongs to level 0 or not
                parent_navigation = self.check_navigation(parent, organization_id)
                if parent_navigation:
                    print(parent_navigation)
                    if parent_navigation.level!=parent_level:
                        return errorMessage('Parent level is not correct.')
                    if parent_navigation.has_child == False:
                        return errorMessage('Parent navigation is not enabled for the child navigations')
                else:
                    return errorMessage('Parent navigation does not exists or have some error.')


            serializer = NavigationsViewsetSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return successfullyCreated(serializer.data)
            else:
                return serializerError(serializer.errors)

        except Exception as e:
            return exception(e)


    def patch(self, request, *args, **kwargs):
        try:
            token = decodeToken(self, request)
            organization_id = token['organization_id']

            pk = self.kwargs['pk']

            nav = Navigations.objects.filter(id=pk, organization=organization_id)
            if not nav.exists():
                return errorMessage("No navigation exists at this id")

            obj = nav.get()

            if 'level' in request.data:
                level = request.data.get('level')
            else:
                level = obj.level

            # check if navigation has level 1 or 2 then it must has level-1 navigation as parent
            if level == 1 or level == 2:
                # must has parent 
                parent_level = level-1
                if not 'parent' in request.data:
                    return errorMessage('Level 1 navigation must has level 0 navigation as parent')
                parent = request.data.get('parent')
                #now check is this parent belongs to level 0 or not
                parent_navigation = self.check_navigation(parent, organization_id)
                if parent_navigation:
                    if parent_navigation.level!=parent_level:
                        return errorMessage('Parent level is not correct.')
                else:
                    return errorMessage('Parent navigation does not exists or have some error.')

            serializer = UpdateNavigationsViewsetSerializers(obj, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()
            
            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            token = decodeToken(self, request)
            organization_id = token['organization_id']

            root_navigations = Navigations.objects.filter(pk=self.kwargs['pk'], organization=organization_id, is_active=True)
            navigation_hierarchy = self.get_navigation_hierarchy(root_navigations)
            serializer = NavigationHierarchySerializers(root_navigations.first(), many=False)

            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def delete(self, request, *args, **kwargs):
        try:
            token = decodeToken(self, request)
            organization_id = token['organization_id']

            pk = self.kwargs['pk']

            nav = Navigations.objects.filter(id=pk, organization=organization_id)
            if not nav.exists():
                return errorMessage("No navigation exists at this id")
            
            obj = nav.get()
            if obj.is_active == False:
                return errorMessage("This navigation is already deactivated")
            
            if RolesNavigations.objects.filter(navigation=pk, is_active=True).exists():
                return errorMessage('This navigation cannot be deleted as it is assigned to some role. Please deactivate that role first')

            obj.is_active=False
            obj.save()
            return successMessage("This navigation is successfully deactivated")
        except Exception as e:
            return exception(e)

    def check_navigation(self, navigation_id, organization_id):
        try:
            navigation = Navigations.objects.filter(id=navigation_id, organization=organization_id)
            if navigation.exists():
                # print(navigation)
                navigation = navigation.first()
                return navigation
            else:
                return False
        except Exception as e:
            return False

    def get_navigation_hierarchy(self, navigations, level=0):
        navigation_list = []
        for navigation in navigations:
            navigation_list.append({'id': navigation.id, 'title': navigation.title, 'url': navigation.url, 'icon':navigation.icon, 'level':navigation.level, 'parent': navigation.parent})
            if navigation.children.exists():
                navigation_list += self.get_navigation_hierarchy(navigation.children.all(), level+1)
        return navigation_list

    def pre_data(self, request, *args, **kwargs):
        try:
            token = decodeToken(self, request)
            organization_id = token['organization_id']

            role_id = None
            if 'role_id' in request.data:
                role_id = request.data['role_id']
            
            data = {'role': None, 'navigation': None, 'role_navigation': None}

            role_query = Roles.objects.filter(is_active=True, organization=organization_id)
            if role_query.exists():
                role_query = role_query.filter(role_type__title__iexact='system roles')
            role_serializer = PreDataRolesSerializers(role_query, many=True)
            data['role'] = role_serializer.data
            
            nav_roles = Navigations.objects.filter(is_active=True, organization=organization_id, is_default=False, parent__isnull=True).order_by('id')
            nav_serializer = NavigationsViewsetSerializers(nav_roles, many=True)
            data['navigation'] = nav_serializer.data
            
            if role_id is not None:
                role_nav_query = RolesNavigations.objects.filter(role= role_id, role__organization=organization_id, is_active=True)
                role_nav_serializer = RolesNavigationsViewsetSerializers(role_nav_query, many=True)
                data['role_navigation'] = role_nav_serializer.data

            return success(data)

        except Exception as e:
            return exception(e)

class RolesNavigationsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs): 
        try:
            token = decodeToken(self, request)
            organization_id = token['organization_id']
            role_id = token['role_id']

            obj = RolesNavigations.objects.filter(role=role_id, role__organization=organization_id, is_active=True).order_by('id')
            serializer = RolesNavigationsViewsetSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def create(self, request, *args, **kwargs):
        try:
            print("here")
            token = decodeToken(self, request)
            organization_id = token['organization_id']

            role_nav_data = request.data
            print(role_nav_data)
            role_nav = self.navigationList(role_nav_data, organization_id)
            print(role_nav)

            if role_nav['code'] == 400:
                return Response({'status': 400, 'message': role_nav['message'], 'system_error_message': role_nav['system_error']})
            return successMessage(role_nav['message'])
        except Exception as e:
            return exception(e)
        

    # def LoginUserNavigationList(self, request, *args, **kwargs):
    #     try:
    #         token = decodeToken(self, request)
    #         organization_id = token['organization_id']
    #         if request.user.is_admin == True:
    #             root_navigations = Navigations.objects.filter(parent__isnull=True, organization=organization_id, is_active=True)
    #             serializer = NavigationHierarchySerializers(root_navigations, many=True)
    #             return success(serializer.data)
            
    #         role_id = token['role_id']
    #         obj = RolesNavigations.objects.filter(role=role_id, can_view=True, navigation__parent__isnull=True, role__organization=organization_id, is_active=True).order_by('id')
    #         serializer = RolesNavigationsViewsetSerializers(obj, many=True)
    #         return success(serializer.data)
            
    #     except Exception as e:
    #         return exception(e)
        
    

    # def navigationList(self, navigations_data, organization_id):
    #     navigations = []
    #     serializer_errors = []
    #     response = {'code': 200, 'message': '', 'system_error': ''}
    #     if isinstance(navigations_data, str):
    #         navigations_data = json.loads(navigations_data)
    #         navigations.append(navigations_data)
    #     else:
    #         navigations = navigations_data
        

    #     try:
    #         navigation_array = {
    #             'id': '',
    #             'role': '',
    #             'navigation': '', 
    #             'can_view': False,
    #             'can_update': False,
    #             'can_add': False,
    #             'can_delete': False,
    #             'is_active': False, 
    #         }
        
    #         if navigations is not None:
    #             for nav in navigations:
    #                 if 'role' in nav:
    #                     role_query = Roles.objects.filter(id=nav['role'], organization=organization_id)
    #                     if not role_query:
    #                         response['code'] = 400
    #                         response['message'] = "No Roles exists at this id"
    #                         return response
    #                     if not role_query.filter(role_type__title__iexact='system roles').exists():
    #                         response['code'] = 400
    #                         response['message'] = "System roles does not exists at this id"
    #                         return response
    #                 if 'navigation' in nav:
    #                     if not Navigations.objects.filter(id=nav['navigation'], organization=organization_id):
    #                         response['code'] = 400
    #                         response['message'] = "No Navigation exists at this id"
    #                         return response
                    
    #                 if 'role' in nav:
    #                     navigation_array['role'] = nav['role']
    #                 if 'navigation' in nav:
    #                     navigation_array['navigation'] = nav['navigation']
                    
    #                 if 'can_view' in nav:
    #                     navigation_array['can_view'] = nav['can_view']
    #                     if nav['can_view']:
    #                         navigation_array['is_active']=True
    #                 if 'can_update' in nav:
    #                     navigation_array['can_update'] =  nav['can_update']
    #                 if 'can_delete' in nav:
    #                     navigation_array['can_delete'] = nav['can_delete']
    #                 if 'can_add' in nav:
    #                     navigation_array['can_add'] = nav['can_add']
                    
    #                 role_nav_query = RolesNavigations.objects.filter(role = nav['role'], navigation=nav['navigation'], navigation__organization=organization_id)
    #                 if role_nav_query.exists():
    #                     obj = role_nav_query.first()      
    #                     serializer = UpdateRolesNavigationsViewsetSerializers(obj, data=navigation_array, partial=True)
    #                 else:
    #                     serializer = RolesNavigationsViewsetSerializers(data=navigation_array)
                    
    #                 if serializer.is_valid():
    #                     serializer.save()
    #                     child_update = self.updateNavChild(navigation_array)
    #                 else:
    #                     serializer_errors.append(serializer.errors)

    #             if (len(navigations) == len(serializer_errors)):
    #                 response['message'] = "No role navigation data processed, please update it again!"
    #             elif len(serializer_errors) > 0:
    #                 response['message'] = "Some of the role navigation data is processed, please update it again!"
    #             else:
    #                 response['message'] = "All of the role navigation data is processed Successfully."
    #                 response['code'] = 200
    #         else:
    #             response['message'] = "No data found"
                

    #         return response
    #     except Exception as e:
    #         response['code'] = 400
    #         response['system_error'] = str(e)
    #         return response

    def navigationList(self, navigations_data, organization_id):
        navigations = []
        serializer_errors = []
        response = {'code': 200, 'message': '', 'system_error': ''}
        if isinstance(navigations_data, str):
            navigations_data = json.loads(navigations_data)
            navigations.append(navigations_data)
            # print("IF")
        else:
            navigations = navigations_data
            # print("Else")

        # print("Test:",type(navigations))
        

        try:
            navigation_array = {
                'id': '',
                'role': '',
                'navigation': '', 
                'can_view': False,
                'can_action': False,
                'is_submodule': False,
                'is_active': False, 
            }
            print("here")
            if navigations is not None:
                # print(navigations)
                # nav_list = [{key: value} for key, value in navigations.items()]
                # print(nav_list)
                nav_list = navigations
                print(nav_list)
                # print(nav_list)
                for nav in nav_list:
                    print(nav)
                    # print(nav)
                    if 'role' in nav:
                        # print(nav)
                        role_query = Roles.objects.filter(id=nav['role'], organization=organization_id)
                        if not role_query:
                            response['code'] = 400
                            response['message'] = "No Roles exists at this id"
                            return response
                        # print(role_query)
                        if not role_query.filter(role_type__title__iexact='system roles').exists():
                            response['code'] = 400
                            response['message'] = "System roles does not exists at this id"
                            return response
                        
                    
                    if 'navigation' in nav:
                        # print(nav)
                        if not Navigations.objects.filter(id=nav['navigation'], organization=organization_id):
                            response['code'] = 400
                            response['message'] = "No Navigation exists at this id"
                            return response
                    
                    if 'role' in nav:
                        navigation_array['role'] = nav['role']
                        # print(navigation_array['role'])
                    if 'navigation' in nav:
                        navigation_array['navigation'] = nav['navigation']
                        # print("T",nav)
                    
                    if 'can_view' in nav:
                        # print("Testing",nav)
                        navigation_array['can_view'] = nav['can_view']
                        if nav['can_view']:
                            navigation_array['is_active']=True

                        # print(nav)
                    if 'can_action' in nav:
                        navigation_array['can_action'] =  nav['can_action']
                        # print(nav)
                    if 'is_submodule' in nav:
                        # print(nav)
                        navigation_array['is_submodule'] = nav['is_submodule']
                    
                    
                    role_nav_query = RolesNavigations.objects.filter(role = nav['role'], navigation=nav['navigation'], navigation__organization=organization_id)
                    # print(role_nav_query)
                    if role_nav_query.exists():
                        obj = role_nav_query.first()      
                        serializer = UpdateRolesNavigationsViewsetSerializers(obj, data=navigation_array, partial=True)
                    else:
                        serializer = RolesNavigationsViewsetSerializers(data=navigation_array)
                    
                    if serializer.is_valid():
                        serializer.save()
                        child_update = self.updateNavChild(navigation_array)
                    else:
                        serializer_errors.append(serializer.errors)

                
                if (len(navigations) == len(serializer_errors)):
                    response['message'] = "No role navigation data processed, please update it again!"
                elif len(serializer_errors) > 0:
                    response['message'] = "Some of the role navigation data is processed, please update it again!"
                else:
                    response['message'] = "All of the role navigation data is processed Successfully."
                    response['code'] = 200
            else:
                response['message'] = "No data found"
                

            return response
        except Exception as e:
            response['code'] = 400
            response['system_error'] = str(e)
            return response



    def updateNavChild(self, nav_array):
        try:
            child_nav_array = nav_array
            children = Navigations.objects.filter(parent=nav_array['navigation'], is_active=True)
            response = {'code': 200, 'system_error': None}
            if children.exists():
                for child in children:
                    child_nav_array['navigation'] = child.id
                    role_nav_query = RolesNavigations.objects.filter(role = child_nav_array['role'], navigation=child_nav_array['navigation'], navigation__organization=child.organization.id)
                    if role_nav_query.exists():
                        obj = role_nav_query.first()      
                        serializer = UpdateRolesNavigationsViewsetSerializers(obj, data=child_nav_array, partial=True)
                    else:
                        serializer = RolesNavigationsViewsetSerializers(data=child_nav_array)
                    
                    if serializer.is_valid():
                        serializer.save()
                        if Navigations.objects.filter(parent=child.id, is_active=True).exists():
                            self.updateNavChild(child_nav_array)



        except Exception as e:
            response['system_error'] = str(e)
            response['code'] = 400
            return response

def LoginUserNavigationList(organization_id, user_id, is_admin, is_subadmin, is_employee):
     try:
        # Step 1: Get roles assigned to the employee
        # token = token
        # print(token)
        # organization_id = token['organization_id']
        # employee_id = token['employee_id']
    
        
        if is_admin == True and is_subadmin == False:
                root_navigations = Navigations.objects.filter(parent__isnull=True, organization=organization_id, is_active=True, for_admin=True)
                default_navigation_serializer = NavigationHierarchySerializers(root_navigations, many=True)
                # return success(serializer.data)
                # response_data = {
                #     #   'roles': [],
                #       'navigation': default_navigation_serializer.data,
                # }
                return default_navigation_serializer.data
        elif is_admin == True and is_subadmin == True:
            role_ids = SystemRoles.objects.filter(user=user_id,is_active=True).values_list('role_id', flat=True)
            # print(role_ids)
            for role_id in role_ids:
                # print(role_id)
                nav_ids = RolesNavigations.objects.filter(
                    role_id=role_id, can_view=True, navigation__parent__isnull=True, role__organization=organization_id, is_active=True,navigation__for_admin =True
                ).values_list('navigation_id', flat=True)
                # print("Nav_ids",nav_ids)

                roles_based_nav = Navigations.objects.filter(id__in=nav_ids, is_active=True)
                # print(roles_based_nav)
                serializer = NavigationHierarchySerializers(roles_based_nav, many=True)
            # default_navigation_qs = Navigations.objects.filter(organization_id=organization_id, is_active=True, is_default=True)
            # default_navigation_serializer = NavigationHierarchySerializers(default_navigation_qs, many=True)

            # response_data = {
            #     'navigation': serializer.data,
            #     # 'default': default_navigation_serializer.data,
            # }

            return serializer.data
        elif is_employee == True:

            roles_based_nav = Navigations.objects.filter(organization_id=organization_id, for_admin=False, is_active=True)
            serializer = NavigationHierarchySerializers(roles_based_nav, many=True)
            # response_data = {
            #     'navigation': serializer.data,
            #     # 'default': default_navigation_serializer.data,
            # }
            return serializer.data
            
     except Exception as e:
        return exception(e)



    
