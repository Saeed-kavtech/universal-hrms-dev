from django.urls import path
from .views import PositionViewset 

urlpatterns = [
    path('', PositionViewset.as_view({'get': 'list', 'post': 'create'})),
    path('<pk>/', PositionViewset.as_view({'get': 'retrieve', 'patch': 'patch',  'destroy': 'delete'})),
    path('pre/data/', PositionViewset.as_view({'get': 'pre_data'}))
]