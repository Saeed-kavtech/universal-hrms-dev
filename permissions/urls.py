from django.urls import path
from .views import AppPermissionsViewset

urlpatterns = [
    path('app/', AppPermissionsViewset.as_view({'post': 'app_permissions'})),
    path('on/role/<role_id>/', AppPermissionsViewset.as_view({'get': 'list'})),
    path('pre/data/view/', AppPermissionsViewset.as_view({'get': 'pre_data'})), 
]
