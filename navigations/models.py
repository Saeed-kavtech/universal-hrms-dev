from django.db import models
from organizations.models import Organization
from roles.models import Roles

# Create your models here.
class Navigations(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    nav_id = models.CharField(max_length=200, null=True, blank=True)
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200, null=True, blank=True)
    icon = models.CharField(max_length=200, null=True, blank=True)
    level = models.IntegerField(default=0)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="children", null=True, blank=True)
    has_child = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)


class RolesNavigations(models.Model):
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)
    navigation = models.ForeignKey(Navigations, on_delete=models.CASCADE)
    can_view = models.BooleanField(default=False)
    can_action = models.BooleanField(default=False)
    is_submodule = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# class RolesNavigations(models.Model):
#     role = models.ForeignKey(Roles, on_delete=models.CASCADE)
#     navigation = models.ForeignKey(Navigations, on_delete=models.CASCADE)
#     can_view = models.BooleanField(default=False)
#     can_update = models.BooleanField(default=False)
#     can_add = models.BooleanField(default=False)
#     can_delete = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)




# class SubModules(models.Model):
#     code = models.CharField(max_length=20, unique=True, null=True, blank=True) 
#     discription = models.TextField(null=True,blank=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


# # class HrmsModules(models.Model):
    


# class RoleNavigationSubModule(models.Model):
#     role_navigation = models.ForeignKey(RolesNavigations, on_delete=models.CASCADE,null=True,blank=True)
#     sub_module=models.ForeignKey(SubModules, on_delete=models.CASCADE,null=True,blank=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
       

