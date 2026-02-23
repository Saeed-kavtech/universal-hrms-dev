from django.urls import path
from .views import LearningAndDevelopmentDashboardViewset, EmployeesDashboard

urlpatterns = [    
    path('learning-and-development/worksheets/', LearningAndDevelopmentDashboardViewset.as_view({'get': 'list'})),
    path('learning-and-development/dashboards/', LearningAndDevelopmentDashboardViewset.as_view({'get': 'get_dashboard_data'})),
    path('employees-self-service/homepage/', EmployeesDashboard.as_view({'get': 'get_homepage'})),
    path('today/attendance/leave/data/',EmployeesDashboard.as_view({'post': 'today_attenadnce_leave_data'})),
    path('month/joining/dob/date/',EmployeesDashboard.as_view({'post': 'employee_joining_dates_dob'})),
    path('get/pending/allowance/',EmployeesDashboard.as_view({'get':"pending_allowances"})),
    path('employee/current/date/atteandance/',EmployeesDashboard.as_view({'get':"get_current_date_attendance"})),
    
]