from django.urls import path
from .views import *

urlpatterns = [    
    path('<emp_uuid>/banks/details/',EmployeeBankDetailsViewset.as_view({'post': 'create', 'get': 'list'})),
    path('<emp_uuid>/banks/details/<bank_id>/', EmployeeBankDetailsViewset.as_view({'get': 'retrieve', 'patch': 'patch',  'destroy': 'delete'})),
]