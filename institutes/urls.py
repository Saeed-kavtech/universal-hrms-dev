from django.urls import path
from .views import *

urlpatterns = [
     path('<emp_uuid>/institutes/', EmployeeEducationsViewset.as_view({'post': 'create', 'get': 'list'})),
     path('<emp_uuid>/institutes/<institute_id>/', EmployeeEducationsViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),
     path('pre/institutes/data/details/', PreInstituteDataView.as_view()),
]