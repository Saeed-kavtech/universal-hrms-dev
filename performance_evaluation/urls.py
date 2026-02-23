from django.urls import path
from .views import *
urlpatterns = [
    # path('organization/kpi/',KIPScaleGroupsViewset.as_view({'get':'list','post': 'create'})),
    # path('employee/kpi/<pk>/',KIPScaleGroupsViewset.as_view({'get': 'retrieve'})),
    # path('evaluator/employee/kpi/',EmployeeKIPScaleGroupsViewset.as_view({'get': 'evaluator_employee_kpis'})),
    path('scale/group/',EmployeeKIPScaleGroupsViewset.as_view({'get': 'scale_group_data'})),
    path('kpi/<pk>/',EmployeeKIPScaleGroupsViewset.as_view({'post':'evaluation'})),
     path('submit/kpi/<pk>/',EmployeeKIPScaleGroupsViewset.as_view({'post':'submit'})),
]