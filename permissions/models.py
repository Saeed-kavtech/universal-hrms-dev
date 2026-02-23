from django.db import models
from django.contrib.contenttypes.models import ContentType
from roles.models import Roles

# Create your models here.
class AppPermissions(models.Model):
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    can_view = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)