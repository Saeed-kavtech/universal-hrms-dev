from django.urls import path
from .views import EmployeeRequisitionViewset, HRRequisitionViewset

urlpatterns = [    
    path('request/', EmployeeRequisitionViewset.as_view({ 'post': 'create'})),
    path('view/request/', EmployeeRequisitionViewset.as_view({ 'get': 'employee_view'})),
    path('sendtohr/<pk>/', EmployeeRequisitionViewset.as_view({ 'get': 'sendtohr'})),
    path('delete/request/<pk>/', EmployeeRequisitionViewset.as_view({'delete':'remove'})),
    path('hr/view/request/', HRRequisitionViewset.as_view({ 'get': 'hr_view'})),
    path('hr/status/update/<pk>/', HRRequisitionViewset.as_view({ 'patch': 'hr_status_update'})),
    path('hr/update/<pk>/', HRRequisitionViewset.as_view({ 'patch': 'update'})),
]

