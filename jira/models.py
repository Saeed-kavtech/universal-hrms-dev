from django.db import models
from organizations.models import Organization

# Create your models here.
class JiraTokens(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    access_token = models.TextField()
    expires_in = models.IntegerField()
    refresh_token = models.TextField()
    scope = models.TextField()
    token_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)