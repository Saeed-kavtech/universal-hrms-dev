from rest_framework import serializers
from .models import Navigations, RolesNavigations

class NavigationsViewsetSerializers(serializers.ModelSerializer):
    navLink = serializers.SerializerMethodField()
    class Meta:
        model = Navigations
        fields = [
                'id',
                'organization',
                'nav_id',
                'title',
                'url',
                'navLink',
                'icon',
                'level',
                'parent',
                'has_child',              
                'is_active',          
            ]
        
    def get_navLink(self, obj):
        try:
            return obj.url
        except Exception as e:
            print(str(e))
            return None



class UpdateNavigationsViewsetSerializers(serializers.ModelSerializer):
    navLink = serializers.SerializerMethodField()
    class Meta:
        model = Navigations
        fields = [
                'id',
                'nav_id',
                'title',
                'url',
                'navLink',
                'icon',
                'level',
                'parent',
                'has_child',              
                'is_active',            
            ]
        
    def get_navLink(self, obj):
        try:
            return obj.url
        except Exception as e:
            print(str(e))
            return None


class NavigationHierarchySerializers(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent_title=serializers.SerializerMethodField()
    navLink = serializers.SerializerMethodField()
    class Meta:
        model = Navigations 
        fields = [
                'id',
                'nav_id',
                'title',
                'url',
                'navLink',
                'icon',
                'level',
                'parent',
                'parent_title',
                'has_child',              
                'is_active',
                'children'
        ]

    def get_children(self, obj):
        try:
            if obj.children.exists():
                return NavigationHierarchySerializers(obj.children.filter(is_active=True), many=True).data
            return None
        except Exception as e:
            return None


    def get_navLink(self, obj):
        try:
            return obj.url
        except Exception as e:
            print(str(e))
            return None
        
    def get_parent_title(self, obj):
        try:
            return obj.parent.title
        except Exception as e:
            print(str(e))
            return None

     

class LoginNavigationHierarchySerializers(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    navLink = serializers.SerializerMethodField()
    class Meta:
        model = Navigations 
        fields = [
                'id',
                'title',
                'navLink',
                'icon',
                'parent',
                'children'
        ]

    def get_children(self, obj):
        try:
            if obj.children.exists():
                return LoginNavigationHierarchySerializers(obj.children.filter(is_active=True), many=True).data
            return None
        except Exception as e:
            return None


    def get_navLink(self, obj):
        try:
            return obj.url
        except Exception as e:
            print(str(e))
            return None

  

     
class RolesNavigationsViewsetSerializers(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    role_title = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    class Meta:
        model = RolesNavigations
        fields = [
                'id',
                'role',
                'role_title',
                'navigation',
                'title',
                'can_view',
                'can_action',
                'is_submodule',
                'is_active', 
                'children',           
            ]
        
    def get_children(self, obj):
        try:
            if obj.navigation.children.exists():
                return NavigationHierarchySerializers(obj.navigation.children.filter(is_active=True), many=True).data
            return None
        except Exception as e:
            return None

    def get_title(self, obj):
        try:
            return obj.navigation.title
        except Exception as e:
            print(str(e))
            return None
        

    def get_role_title(self, obj):
        try:
            return obj.role.title
        except Exception as e:
            print(str(e))
            return None
        




class LoginRolesNavigationsViewsetSerializers(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    role_title = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    class Meta:
        model = RolesNavigations
        fields = [
                'id',
                'role',
                'role_title',
                'title',
                'navigation',
                'can_view',
                'can_action',
                'children',           
            ]
        
    def get_children(self, obj):
        try:
            if obj.navigation.children.exists():
                return LoginNavigationHierarchySerializers(obj.navigation.children.filter(is_active=True), many=True).data
            return None
        except Exception as e:
            return None

    def get_title(self, obj):
        try:
            return obj.navigation.title
        except Exception as e:
            print(str(e))
            return None
        

    def get_role_title(self, obj):
        try:
            return obj.role.title
        except Exception as e:
            print(str(e))
            return None
        


class UpdateRolesNavigationsViewsetSerializers(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    role_title = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    class Meta:
        model = RolesNavigations
        fields = [
                'id',
                'title',
                'role_title',
                'can_view',
                'can_action',
                'is_submodule',
                'is_active',   
                'children'         
            ]

    def get_children(self, obj):
        try:
            if obj.navigation.children.exists():
                return NavigationHierarchySerializers(obj.navigation.children.filter(is_active=True), many=True).data
            return None
        except Exception as e:
            return None


    def get_title(self, obj):
        try:
            return obj.navigation.title
        except Exception as e:
            print(str(e))
            return None
        
    
    def get_role_title(self, obj):
        try:
            return obj.role.title
        except Exception as e:
            print(str(e))
            return None
        
# class RolesNavigationsViewsetSerializers(serializers.ModelSerializer):
#     title = serializers.SerializerMethodField()
#     role_title = serializers.SerializerMethodField()
#     children = serializers.SerializerMethodField()
#     class Meta:
#         model = RolesNavigations
#         fields = [
#                 'id',
#                 'role',
#                 'role_title',
#                 'navigation',
#                 'title',
#                 'can_view',
#                 'can_update',
#                 'can_add',
#                 'can_delete',
#                 'is_active', 
#                 'children',           
#             ]
        
#     def get_children(self, obj):
#         try:
#             if obj.navigation.children.exists():
#                 return NavigationHierarchySerializers(obj.navigation.children.filter(is_active=True), many=True).data
#             return None
#         except Exception as e:
#             return None

#     def get_title(self, obj):
#         try:
#             return obj.navigation.title
#         except Exception as e:
#             print(str(e))
#             return None
        

#     def get_role_title(self, obj):
#         try:
#             return obj.role.title
#         except Exception as e:
#             print(str(e))
#             return None
   

# class UpdateRolesNavigationsViewsetSerializers(serializers.ModelSerializer):
#     title = serializers.SerializerMethodField()
#     role_title = serializers.SerializerMethodField()
#     children = serializers.SerializerMethodField()
#     class Meta:
#         model = RolesNavigations
#         fields = [
#                 'id',
#                 'title',
#                 'role_title',
#                 'can_view',
#                 'can_update',
#                 'can_add',
#                 'can_delete',
#                 'is_active',   
#                 'children'         
#             ]

#     def get_children(self, obj):
#         try:
#             if obj.navigation.children.exists():
#                 return NavigationHierarchySerializers(obj.navigation.children.filter(is_active=True), many=True).data
#             return None
#         except Exception as e:
#             return None


#     def get_title(self, obj):
#         try:
#             return obj.navigation.title
#         except Exception as e:
#             print(str(e))
#             return None
        
    
#     def get_role_title(self, obj):
#         try:
#             return obj.role.title
#         except Exception as e:
#             print(str(e))
#             return None