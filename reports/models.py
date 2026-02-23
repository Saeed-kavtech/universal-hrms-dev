# from django.db import models
# from organizations.models import Organization
# from profiles_api.models import HrmsUsers

# REPORT_MODULES = (
# 	('recruitment-and-hiring', 'recruitment-and-hiring'),
# 	('learning-and-development', 'learning-and-development'),
# 	('employee', 'employee')
# )

# class ReportTypes(models.Model):
#     title = models.CharField(max_length=200)
#     report_modules = models.CharField(choices=REPORT_MODULES, max_length=200)
#     organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
#     created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


# class Report(models.Model):
#     report_type = models.ForeignKey(ReportTypes, on_delete=models.CASCADE, null=True, blank=True)
#     action_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)