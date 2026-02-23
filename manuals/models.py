from django.db import models
from profiles_api.models import HrmsUsers
from organizations.models import Organization
from helpers.image_uploads import upload_manuals
from employees.models import Employees
from helpers.model_utils import CommonFieldsModel
import uuid

# Create your models here.
class ManualTypes(CommonFieldsModel):
    title = models.CharField(max_length=250)
    level = models.IntegerField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

class Manuals(CommonFieldsModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    manual_type = models.ForeignKey(ManualTypes, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    document = models.FileField(upload_to=upload_manuals)
    approved_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, related_name='manual_approved_by', null=True, blank=True)

