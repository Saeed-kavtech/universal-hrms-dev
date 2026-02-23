from django.urls import path
from .views import *

urlpatterns = [
    path('', RolesViewset.as_view({'get': 'list', 'post': 'create'})),
    path('system/roles/', RolesViewset.as_view({'get': 'systemrolelist', 'post': 'create'})),
    path('<uuid>/', RolesViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'delete': 'delete'}))
]