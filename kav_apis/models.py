from django.db import models

# Create your models here.
class ContactForm(models.Model):
    name = models.CharField(max_length=200) 
    email = models.CharField(max_length=200) 
    company = models.CharField(max_length=200) 
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
