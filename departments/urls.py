from django.urls import path
from .views import GroupHeadsViewset, DepartmentsViewset

urlpatterns = [    
    path('grouphead/', GroupHeadsViewset.as_view({'get': 'list', 'post': 'create'})),
    path('grouphead/<pk>/', GroupHeadsViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'delete': 'delete'})),
    path('department/', DepartmentsViewset.as_view({'get': 'list', 'post': 'create'})),
    path('department/<pk>/', DepartmentsViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'delete': 'delete'})),
]