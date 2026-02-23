from django.urls import path
from .views import (
    CustomAttendanceReportViewSet, upload_screenshot, upload_WFH_screenshot, get_screenshots_by_attendance, screenshots_by_employee_date, 
    analytics_by_employee_date, delete_screenshot, generate_tracker_script, 
    generate_stop_tracker_script, tracker_status, EmployeesAttendanceViewset, HrmsEmployeesAttendanceViewset, 
    AttendanceMachineLogFilesViewset, EmployeesAttendanceLabelViewset, AttendanceStatusPMOAPIView

)

# comment added

urlpatterns = [    
    path('organization/<organization_id>/attendance/check_in/<emp_code>/', EmployeesAttendanceViewset.as_view({'post': 'check_in'})),
    path('organization/<organization_id>/attendance/check_out/<emp_code>/', EmployeesAttendanceViewset.as_view({'post': 'check_out'})),
    path('organization/<organization_id>/attendance/list/<emp_code>/', EmployeesAttendanceViewset.as_view({'get': 'list'})),
    path('attendance/check_in/', HrmsEmployeesAttendanceViewset.as_view({'post': 'emp_check_in'})),
    path('attendance/check_in/<pk>/', HrmsEmployeesAttendanceViewset.as_view({'post': 'emp_check_in_pk'})),
    path('attendance/check_out/', HrmsEmployeesAttendanceViewset.as_view({'post': 'emp_check_out'})),
    path('attendance/check_out/<pk>/', HrmsEmployeesAttendanceViewset.as_view({'post': 'emp_check_out_pk'})),
    path('attendance/WFH/check_in/', HrmsEmployeesAttendanceViewset.as_view({'post': 'emp_wfh_check_in'})),
    path('attendance/WFH/check_out/', HrmsEmployeesAttendanceViewset.as_view({'post': 'emp_wfh_check_out'})),
    path('attendance/list/', HrmsEmployeesAttendanceViewset.as_view({'get': 'list'})),
    path('organization/<organization_id>/attendance/report/',EmployeesAttendanceViewset.as_view({'post':'attendance_report'})),
    path('organization/attendance/report/employee/',EmployeesAttendanceViewset.as_view({'post':'attendance_report_employee'})),
    path('attendance/list/all/', HrmsEmployeesAttendanceViewset.as_view({'post': 'emp_attendance_list'})),
    path('attendance/file/data/', AttendanceMachineLogFilesViewset.as_view({'get': 'list_attendance'})),
    path('attendance/list/all/', HrmsEmployeesAttendanceViewset.as_view({'get': 'get_attendance'})),
    path('attendance/machine/data/', AttendanceMachineLogFilesViewset.as_view({'get': 'list', 'post': 'create'})),
    path('attendance/labels/', EmployeesAttendanceLabelViewset.as_view({'get': 'list', 'post': 'create'})),
    path('attendance/status/', EmployeesAttendanceLabelViewset.as_view({'post': 'list_data'})),
    path('all/employee/current/month/atteandance/',EmployeesAttendanceLabelViewset.as_view({'post':"all_employee_working_hours"})),
    path('attendance/sync/', EmployeesAttendanceLabelViewset.as_view({'post': 'add_existing_data_from_ess'})),
    path('attendance/notify/', EmployeesAttendanceLabelViewset.as_view({'post':'notify_wfh'})),
    path('attendance/notify/email/employees/<pk>/',EmployeesAttendanceViewset.as_view({'get':'employee_attendance_email'})),
    path('attendance/notify/email/logs/',EmployeesAttendanceViewset.as_view({'post':"attendance_email_log"})),
    path('get/data/of/machine/<pk>/',EmployeesAttendanceViewset.as_view({'get':"machine_attenadnace_data"})),
    path('get/current/date/data/of/machine/<pk>/',EmployeesAttendanceViewset.as_view({'get':"current_date_machine_attenadnace_data"})),
    path('get/previous/date/data/of/machine/<pk>/',EmployeesAttendanceViewset.as_view({'get':"previous_date_machine_attenadnace_data"})),
    path('get/check_in_data/<pk>/',EmployeesAttendanceViewset.as_view({'get':'machine_attenadnace_check_in'})),
    path('attendance/count/<employee_id>/',EmployeesAttendanceLabelViewset.as_view({'post':"all_employee_attandance_count"})),
    
    # Screenshot URLs
    path('attendance/upload_screenshot/', upload_screenshot, name='upload_screenshot'),
    path('attendance/wfh/upload_screenshot/', upload_WFH_screenshot, name='upload_wfh_screenshot'),

    path('attendance/<int:attendance_id>/screenshots/', get_screenshots_by_attendance, name='get_screenshots'),
    path('screenshots_by_employee_date/', screenshots_by_employee_date, name='screenshots_by_employee_date'),
    path('analytics_by_employee_date/', analytics_by_employee_date, name='analytics_by_employee_date'),
    path('attendance/<int:attendance_id>/screenshots/<int:screenshot_id>/delete/', delete_screenshot, name="delete_screenshot"),
    
    # ✅ FIXED: Tracker URLs with "attendance" prefix
    path('attendance/tracker/<int:attendance_id>/script/', generate_tracker_script, name='generate_tracker_script'),
    path('attendance/tracker/<int:attendance_id>/stop_script/', generate_stop_tracker_script, name='generate_stop_tracker_script'),
    

    path("attendance/<int:attendance_id>/tracker_status/", tracker_status, name="tracker_status"),
    path('attendance/status-pmo/', AttendanceStatusPMOAPIView.as_view()),
    
    path('attendance/custom-report/', CustomAttendanceReportViewSet.as_view({'post': 'generate_report'})),



  ]   


