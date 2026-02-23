from django.urls import path
from .views import NavigationsViewset, RolesNavigationsViewset

urlpatterns = [
    path('', NavigationsViewset.as_view({'post': 'create', 'get': 'list'})),
    path('<pk>/', NavigationsViewset.as_view({'get':'retrieve', 'patch': 'patch', 'delete': 'delete'})),
    path('pre/data/', NavigationsViewset.as_view({'post': 'pre_data'})),
    path('roles/data/', RolesNavigationsViewset.as_view({'post': 'create', 'get': 'list'})),
    path('roles/data/<pk>/', RolesNavigationsViewset.as_view({'patch': 'patch', 'delete': 'delete'})), 
    path('role/based/on/login/user/', RolesNavigationsViewset.as_view({'get': 'LoginUserNavigationList'}))
]