from django.urls import path
from .views import *

urlpatterns = [
    
    path('create/new/',Meetingsviewset.as_view({"post":"create_meetings"})),
    path('create/meet/',Meetingsviewset.as_view({"post":"create_meet"})),
    path('list/',Meetingsviewset.as_view({'get': 'meetings_list'})),
    path('details/<pk>/',Meetingsviewset.as_view({'get': 'meeting_detalis'})),
    path('zak/token/',Meetingsviewset.as_view({"get":"get_zak_token"})),
    path("upcomings/",Meetingsviewset.as_view({"get":"get_upcoming_meetings"})),
    path('participants/<pk>/',Meetingsviewset.as_view({"get":"get_meeting_participants"})),
   

]