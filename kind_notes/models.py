from django.db import models
from employees.models import Employees

# Create your models here.
class KindNotes(models.Model):
    sender = models.ForeignKey(Employees, related_name='msg_sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Employees, related_name='msg_receiver', on_delete=models.CASCADE)
    notes = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)