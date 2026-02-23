from django.urls import path
from .views import *

urlpatterns = [
    path('<emp_uuid>/companies/', EmployeeWorkExperienceViewset.as_view({'post': 'create', 'get': 'list'})),
    path('<emp_uuid>/companies/<company_id>/', EmployeeWorkExperienceViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),
]