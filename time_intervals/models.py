from django.db import models
from organizations.models import Organization
from profiles_api.models import HrmsUsers
from roles.models import Roles
from email_templates.models import EmailTemplates

import uuid

class TimeIntervals(models.Model):
	title = models.CharField(max_length=200)
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
	level = models.IntegerField(default=1, null=True, blank=True)
	start_time = models.TimeField(null=True, blank=True)
	end_time = models.TimeField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class TimeSlots(models.Model):
	title = models.CharField(max_length=20)
	from_time = models.TimeField(null=True, blank=True)
	to_time = models.TimeField(null=True, blank=True)
	time_interval = models.ForeignKey(TimeIntervals, on_delete=models.CASCADE, related_name="interval_time_slots")
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class UserTimeSlots(models.Model):
	time_slot = models.ForeignKey(TimeSlots, on_delete=models.CASCADE)
	user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)