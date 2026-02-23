from django.urls import path
from .views import ManualsViewset, ManualPreDataViewset

urlpatterns = [    
    path('', ManualsViewset.as_view({'get': 'list', 'post': 'create'})), 
    path('<pk>/', ManualsViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),  
    path('pre/data/', ManualPreDataViewset.as_view({'get': 'list'})), 
]