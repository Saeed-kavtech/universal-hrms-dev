from django.urls import path
from .views import *

urlpatterns = [
    path('', StagesViewset.as_view({'get': 'list', 'post': 'create'}), name='stages'),
    path('<pk>/', StagesViewset.as_view({'get': 'get', 'patch': 'partial_update'}), name='stage'),

    path('types/templates/', StageTypeTemplatesViewset.as_view({'get': 'list', 'post': 'create'}), name='stage_types'),
    path('types/templates/<pk>/', StageTypeTemplatesViewset.as_view({'get': 'get', 'patch': 'partial_update'}), name='stage_types'),
    path('types/templates/pre/data/', StageTypeTemplatesViewset.as_view({'get': 'pre_data'}), name='stage_type_pre_data'),
    
]