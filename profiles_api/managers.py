from django.contrib.auth.base_user import BaseUserManager
# from django.contrib.auth.hashers import make_password
# from django.utils.translation import ugettext_lazy as _



class HrmsUsersManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, profile_image,is_subadmin,password=None, password2=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            profile_image=profile_image
        )
        if is_subadmin:
            user.is_subadmin = True
            
        user.set_password(password)
        user.is_admin = True
        user.is_superuser = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email, password.
        """
        user = self.model(
            email=self.normalize_email(email),
            password=password,
        )
        user.set_password(password)
        user.is_superuser = True
        user.is_admin = False
        user.is_subadmin=False
        user.save(using=self._db)
        return user

    def create_employees(self, first_name, last_name, email, password, password2):

        user = self.model(
            email=self.normalize_email(email),
            first_name = first_name,
            last_name = last_name
        )
        user.set_password(password)
        user.is_active = True
        user.is_admin = False
        user.is_superuser = False
        user.is_subadmin=False
        user.is_employee = True
        user.save(using=self._db)
        return user