from django.db import models
from profiles_api.models import HrmsUsers
from organizations.models import Organization

# Create your models here.


class UserLoginLogs(models.Model):
    user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)