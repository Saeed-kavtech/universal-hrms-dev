from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import PermissionsMixin
from .managers import HrmsUsersManager

from helpers.image_uploads import hrms_user_profile_upload

# Create your models here.

user_level_choices = (
    (1, 'single-level'),
    (2, 'multi-level'),
)

# Create your models here.



class HrmsUsers(AbstractUser):
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )
    is_admin = models.BooleanField(default=False, null=True)
    is_employee = models.BooleanField(default=False, null=True)
    user_level = models.IntegerField(choices = user_level_choices, default=1)
    is_privileged = models.BooleanField(default=False, null=True)
    is_subadmin = models.BooleanField(default=False, null=True)
    status = models.BooleanField(default=False, null=True)
    profile_image = models.ImageField(null=True, blank=True, upload_to=hrms_user_profile_upload, default='')
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    username = None
    
    objects = HrmsUsersManager()

    def __str__(self):
        return str(self.email)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin