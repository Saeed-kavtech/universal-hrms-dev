from django.urls import path
from .views import *

urlpatterns = [
    path('', TimeIntervalsViewset.as_view({'get': 'list', 'post': 'create'}), name='time_intervals'),
    path('<pk>/', TimeIntervalsViewset.as_view({'get': 'get', 'patch': 'partial_update'}), name='time_interval'),

    path('<ti_pk>/slots/', TimeSlotsViewset.as_view({'get': 'list', 'post': 'create'}), name='interval_slots'),
    path('<ti_pk>/slots/<pk>/', TimeSlotsViewset.as_view({'get': 'get', 'patch': 'partial_update'}), name='interval_slot')
]