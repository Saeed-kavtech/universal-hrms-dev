from django.urls import path
from .views import *

urlpatterns = [
    

    

    path('types/', ScoreTypesViewset.as_view({'get': 'list', 'post': 'create'}), name='score_type'),
    path('types/<pk>/', ScoreTypesViewset.as_view({'get': 'get', 'patch': 'partial_update'}), name='score_types'),

    path('complexity/levels/', ComplexityLevelsViewset.as_view({'get': 'list', 'post': 'create'}), name='complexity_level'),
    path('complexity/levels/<pk>/', ComplexityLevelsViewset.as_view({'get': 'get', 'patch': 'partial_update'}), name='complexity_levels'),

    path('', ScoresViewset.as_view({'get': 'list', 'post': 'create'}), name='score'),
    path('<pk>/', ScoresViewset.as_view({'get': 'get', 'patch': 'partial_update'}), name='scores'),

]