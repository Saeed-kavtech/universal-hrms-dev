from django.urls import path

from kpis.views import KpisPreDataViewset
from .views import *

urlpatterns = [    
    path('', ProjectsViewset.as_view({'get': 'list', 'post': 'create'})),
    path('<uuid>/', ProjectsViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),
    path('pre/data/view/', PreProjectDataView.as_view()),
    path('employee/projects/',KpisPreDataViewset.as_view({'post':"employee_projects"}))
]
