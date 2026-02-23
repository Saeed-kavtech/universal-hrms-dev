from rest_framework import serializers
from .models import (
    EmployeesAttendance, AttendanceMachines, AttendanceMachineLogFiles, EmployeesAttendanceEmailLogs, EmployeesAttendanceLabel, Screenshot, Heartbeat
)
from employees.models import Employees
import datetime

# comment added
class EmployeesAttendanceViewsetSerializers(serializers.ModelSerializer):
    employee_name =  serializers.SerializerMethodField()
    emp_code = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    class Meta:
        model = EmployeesAttendance
        fields = [
            'id',
            'employee',
            'employee_name',
            'emp_code',
            'date',
            'is_custom_time_set',
            'is_check_in',
            'check_in',
            'is_check_out',
            'check_out',
            'duration',
            'attendance_type',
            'wfh_reason',
            'is_active'
        ]

    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        
        except Exception as e:
            print(str(e))
            return None
        
    def get_emp_code(self, obj):
        try:
            return obj.employee.emp_code
        except Exception as e:
            print(str(e))
            return None
    
    def get_duration(self, obj):
        try:
            time_format = '%H:%M:%S'
            check_out = datetime.datetime.strptime(str(obj.check_out), time_format) if obj.check_out else None
            check_in = datetime.datetime.strptime(str(obj.check_in), time_format) if obj.check_in else None
            if check_out and check_in:
                duration = check_out - check_in
                hours, remainder = divmod(duration.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                return f'{int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds'
            return None
        except Exception as e:
            print(str(e))
            return None


class CUEmployeesAttendanceViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeesAttendance
        fields = ['id', 'employee', 'date', 'is_check_in', 'check_in' ,'is_check_out', 'check_out', 
        'attendance_machine_log_file', 'attendance_type', 'is_active', 'created_at', 'updated_at']


class AttendanceMachinesSerializers(serializers.ModelSerializer):
    class Meta:
        model = AttendanceMachines
        fields = ['id', 'organization', 'machine_number', 'machine_title' ,'is_active']

class CUAttendanceMachineLogFilesSerializers(serializers.ModelSerializer):
    attendance_machine_title=serializers.SerializerMethodField()
    organization=serializers.SerializerMethodField()
    class Meta:
        model = AttendanceMachineLogFiles
        
        fields = ['id',"organization" ,'attendance_machine',"attendance_machine_title", 'attendance_file' ,'uploaded_by', 
            'approved_by','created_at', 'from_date', 'to_date', 'is_processed', 'processed_by', 'is_active']
        
    def get_attendance_machine_title(self, obj):
        try:
            return obj.attendance_machine.machine_title
        except Exception as e:
            print(str(e))
            return None
        
    def get_organization(self, obj):
        try:
            return obj.attendance_machine.organization.id
        except Exception as e:
            print(str(e))
            return None

class EmployeesAttendanceLabelSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeesAttendanceLabel
        fields = [
            'id',
            'employee',
            'date',
            'attendance_status',
            'comments',
            'created_by',
            'is_active',
        ]

class EmployeesLabelSerializers(serializers.ModelSerializer):
    attendance_status_data = serializers.SerializerMethodField()
    class Meta:
        model = Employees
        fields = [
            'id',
            'name',
            'emp_code',
            'attendance_status_data'
        ]

    def get_attendance_status_data(self, obj):
        try:
            query = self.context.get('query')
            query = query.filter(employee=obj.id)
            if not query.exists():
                return None
            
            total_wfh = query.filter(attendance_status = 'WFH').count()
            total_leaves = query.filter(attendance_status = 'L').count()
            total_holidays = query.filter(attendance_status = 'H').count()
            total_absents = query.filter(attendance_status = 'A').count()
            total_presents = query.filter(attendance_status = 'P').count()
            total_weekends = query.filter(attendance_status = 'W').count()
            
            serializer = LabelSerializers(query, many=True)
            data = {
                'total_wfh': total_wfh,
                'total_leaves': total_leaves,
                'total_holidays': total_holidays,
                'total_absesnts': total_absents,
                'total_presents': total_presents,
                'total_weekends': total_weekends,
                'data': serializer.data
            }

            return data
        except Exception as e:
            print(str(e))
            return None
        
class LabelSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeesAttendanceLabel
        fields = [
            'date',
            'attendance_status',
            'comments',
            'created_by',
            'is_active',
        ]

class DashboardEmployeesAttendanceLabelSerializers(serializers.ModelSerializer):
    profile_image=serializers.SerializerMethodField()
    employee_name=serializers.SerializerMethodField()
    employee_uuid=serializers.SerializerMethodField()
    position_title=serializers.SerializerMethodField()
    department_title=serializers.SerializerMethodField()
    check_in_time=serializers.SerializerMethodField()
    
    class Meta:
        model = EmployeesAttendanceLabel
        fields = [
            'id',
            'employee',
            'employee_name',
            'employee_uuid',
            'profile_image',
            'position_title',
            'department_title',
            'date',
            'check_in_time',
            'attendance_status',
            'comments',
            'created_by',
            'is_active',
        ]
        
    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            print(str(e))
            return None
        
    def get_position_title(self, obj):
        try:
            return obj.employee.position.title
        except Exception as e:
            print(str(e))
            return None
        
    def get_department_title(self, obj):
        try:
            return obj.employee.department.title
        except Exception as e:
            print(str(e))
            return None
        
    def get_employee_uuid(self, obj):
        try:
            return obj.employee.uuid
        except Exception as e:
            print(str(e))
            return None
        
    def get_profile_image(self, obj):
        try:
            # organization_id = self.context.get('organization_id')
            if obj.created_by.is_admin:
                return obj.created_by.profile_image.url
            
            query=Employees.objects.filter(hrmsuser=obj.created_by.id,is_active=True)
            if not query.exists():
                return None
            obj=query.get()
            return obj.profile_image.url
        except Exception as e:
            print(str(e))
            return None
        
    def get_check_in_time(self, obj):
        try:
            obj=EmployeesAttendance.objects.filter(employee=obj.employee.id,attendance_type=obj.comments,date=obj.date,is_active=True).first()
            if obj:
                return obj.check_in
            return None
        except Exception as e:
            print(str(e))
            return None

    # def get_check_in_time(self, obj):
    #     try:
    #         # Fetch attendance records for the given employee and date
    #         attendance_records = EmployeesAttendance.objects.filter(
    #             employee=obj.employee.id, date=obj.date, is_active=True
    #         )

    #         if not attendance_records.exists():
    #             return None  # No records found

    #         # Group records by attendance type and get the first record of each type
    #         distinct_records = []
    #         seen_types = set()

    #         for record in attendance_records.order_by('attendance_type', 'id'):
    #             if record.attendance_type not in seen_types:
    #                 distinct_records.append(record)
    #                 seen_types.add(record.attendance_type)

    #         print(distinct_records)

    #         return distinct_records
    #     except Exception as e:
    #         print(str(e))
    #         return None
       
class EmployeesAttendanceEmailLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeesAttendanceEmailLogs
        fields = ['id', 'employee', 'date', 'message', 'email_sended', 'is_active', 'created_at', 'updated_at']
        
        
        
        





class ScreenshotSerializer(serializers.ModelSerializer):
    screenshot_url = serializers.SerializerMethodField()

    class Meta:
        model = Screenshot
        fields = [
            "id",
            "timestamp",
            "window_title",
            "screenshot_url",
            "is_idle",
            "is_productive",
            "idle_duration_seconds",
            "productive_time_min",
            "productivity_score",
            "deleted_by_user",

        ]

    def get_screenshot_url(self, obj):
        request = self.context.get('request')
        if obj.screenshot and request:
            return request.build_absolute_uri(obj.screenshot.url)
        elif obj.screenshot:
            return obj.screenshot.url
        return None


class HeartbeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Heartbeat
        fields = [
            "id",
            "attendance",
            "timestamp",
            "tracker_status",
            "machine_info",
            "is_active",
        ]
        read_only_fields = ["id", "timestamp"]


class TrackerStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    last_seen = serializers.DateTimeField(allow_null=True)









from rest_framework import serializers
import calendar
import datetime


class AttendancePMOSerializer(serializers.ModelSerializer):
    attendance_status_data = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()

    class Meta:
        model = Employees
        fields = (
            'id',
            'emp_code',
            'name',
            'projects',
            'attendance_status_data'
        )

    def get_projects(self, obj):
        return obj.employeeprojects_set.select_related('project').values(
            'project__id',
            'project__name',
            'project__code'
        )


    def get_attendance_status_data(self, obj):
        attendance_qs = self.context['attendance_qs'].filter(employee=obj)
        month = self.context['month']
        year = self.context['year']

        # Map existing labels by date
        attendance_map = {
            att.date: att for att in attendance_qs
        }

        today = datetime.date.today()
        last_day = calendar.monthrange(year, month)[1]

        # If current month, don't go beyond today
        if year == today.year and month == today.month:
            last_day = today.day

        data = []

        total_p = total_a = total_l = total_h = total_wfh = total_w = 0

        for day in range(1, last_day + 1):
            date = datetime.date(year, month, day)

            if date in attendance_map:
                att = attendance_map[date]
                status = att.attendance_status
                comments = att.comments
            else:
                # 👇 AUTO WEEKEND HANDLING
                if date.weekday() in (5, 6):  # Saturday, Sunday
                    status = 'W'
                    comments = 'Weekend'
                    total_w += 1
                    data.append({
                        'date': date,
                        'attendance_status': status,
                        'comments': comments
                    })
                    continue
                else:
                    continue  # no record + not weekend → skip

            # Count totals
            if status == 'P':
                total_p += 1
            elif status == 'A':
                total_a += 1
            elif status == 'L':
                total_l += 1
            elif status == 'H':
                total_h += 1
            elif status == 'WFH':
                total_wfh += 1
            elif status == 'W':
                total_w += 1

            data.append({
                'date': date,
                'attendance_status': status,
                'comments': comments
            })

        return {
            'total_presents': total_p,
            'total_absesnts': total_a,
            'total_leaves': total_l,
            'total_holidays': total_h,
            'total_wfh': total_wfh,
            'total_weekends': total_w,
            'data': data
        }
