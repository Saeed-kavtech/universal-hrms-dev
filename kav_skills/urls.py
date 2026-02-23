from django.urls import path
from .views import KavskillsEnrollmentFormViewset, SkillTypesPreDataViewset

urlpatterns = [    
    path('', KavskillsEnrollmentFormViewset.as_view({'get': 'list', 'post': 'create'})),  
    path('<pk>/', KavskillsEnrollmentFormViewset.as_view({'get': 'retrieve', 'delete': 'delete','patch': 'patch'})),  
    path('pre/data/', SkillTypesPreDataViewset.as_view({'get': 'list'})), 

]