from django.db import models
from organizations.models import Organization
from profiles_api.models import HrmsUsers
import uuid

# router, system role or project role
class RoleTypes(models.Model):
	title = models.CharField(max_length=250)
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
	level = models.IntegerField(default=1, null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	


class Roles(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
	role_type = models.ForeignKey(RoleTypes, on_delete=models.CASCADE, null=True, blank=True)
	title = models.CharField(max_length=250)
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
	code = models.CharField(max_length=20)
	level = models.IntegerField(default=1, null=True, blank=True)
	user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
	description = models.TextField(blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
