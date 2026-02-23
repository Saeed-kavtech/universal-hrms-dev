from django.db import models
from profiles_api.models import HrmsUsers
from organizations.models import Organization
from employees.models import Employees

from helpers.image_uploads import upload_organization_attendance_files
import uuid

attendance_type_choices = (
    ('office', 'office'),
    ('WFH', 'WFH'),
    ('hybrid', 'hybrid'),
    ('H','H'),
    ('W','W'),
    ('A','A'),
    ('P','P'),
    ('L','L')
)
dump_status_choices=(
    ('added', 'added'),
    ('skipped', 'skipped'),
)
state_choices=(
    (0, 'check in'),
    (1, 'check out'),
    
)

mode_choices=(
    (1, 'Finger'),
    (2, 'Face'),
    (3, 'Password'),
    (4,'Card')
)


class AttendanceMachines(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    machine_number = models.CharField(max_length=50)
    machine_title = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AttendanceMachineLogFiles(models.Model):
    attendance_machine = models.ForeignKey(AttendanceMachines, on_delete=models.CASCADE)
    attendance_file = models.FileField(upload_to=upload_organization_attendance_files)
    uploaded_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, related_name="uploaded_by")
    approved_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, blank=True, null=True)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    is_processed = models.BooleanField(default=True)
    processed_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, related_name="attendance_process_by", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EmployeesAttendance(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    is_custom_time_set = models.BooleanField(default=False, null=True, blank=True)
    is_check_in = models.BooleanField(default=False)
    check_in = models.TimeField(null=True, blank=True)
    is_check_out = models.BooleanField(default=False)
    check_out = models.TimeField(null=True, blank=True)
    attendance_machine_log_file = models.ForeignKey(AttendanceMachineLogFiles, on_delete=models.CASCADE, blank=True, null=True)
    attendance_type = models.CharField(max_length=30, choices=attendance_type_choices, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    wfh_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Employee attendance status is added in this model
class  EmployeesAttendanceLabel(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    date = models.DateField()
    attendance_status = models.CharField(max_length=50, null=True, blank=True)
    comments = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class  EmployeesAttendanceEmailLogs(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    date = models.DateField()
    message = models.CharField(max_length=100, null=True, blank=True)
    email_sended=models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AttendanceMachineslogs(models.Model):
    employee=models.ForeignKey(Employees, on_delete=models.CASCADE,null=True,blank=True)
    date=models.DateField(null=True, blank=True)
    time=models.TimeField(null=True, blank=True)
    mode=models.IntegerField(choices=mode_choices, null=True, blank=True)
    state=models.IntegerField(choices=state_choices,null=True,blank=True)
    status=models.CharField(max_length=30, choices=dump_status_choices, null=True, blank=True)
    machine_serial_number=models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# contact form for kavtach website







class Screenshot(models.Model):
    attendance = models.ForeignKey('EmployeesAttendance', on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    window_title = models.CharField(max_length=255, default='Unknown')
    screenshot = models.ImageField(upload_to='attendance_screenshots')  # Make required, remove null=True

    # Activity tracking
    is_idle = models.BooleanField(default=False)
    idle_duration_seconds = models.IntegerField(default=0)
    is_productive = models.BooleanField(default=False)
    productivity_score = models.FloatField(default=0.0)
    productive_time_min = models.FloatField(default=0.0)

    # Management fields
    
    is_active = models.BooleanField(default=True)
    deleted_by_user = models.BooleanField(default=False)
    deducted_minutes = models.FloatField(default=0.0)
    deleted_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"{self.attendance.id} | {self.timestamp} | {self.window_title}"

class Heartbeat(models.Model):
    attendance = models.ForeignKey('EmployeesAttendance', on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    tracker_status = models.CharField(max_length=20, default='STARTED')  # STARTED or STOPPED
    machine_info = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['attendance', '-timestamp']),
        ]

    def __str__(self):
        return f"Heartbeat: {self.attendance.id} | {self.timestamp} | {self.tracker_status}"