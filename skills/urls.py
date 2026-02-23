from django.urls import path
from .views import *

urlpatterns = [
    path('<emp_uuid>/skills/', EmployeeSkillsViewset.as_view({'post': 'create', 'get': 'list'})),
    path('<emp_uuid>/skills/<skill_id>/', EmployeeSkillsViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),
    path('pre/skills/data/details/', PreSkillDataView.as_view(),)
]