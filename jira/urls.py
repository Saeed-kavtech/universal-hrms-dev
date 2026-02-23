from django.urls import path
from .views import JiraTokensViewset

urlpatterns = [    
    path('tokens/', JiraTokensViewset.as_view({'get': 'list', 'post': 'create'})),
    path('tokens/<pk>/', JiraTokensViewset.as_view({'delete': 'delete'}))
]