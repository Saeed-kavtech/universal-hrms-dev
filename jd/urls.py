from django.urls import path
from .views import JobDescriptionViewSet

urlpatterns = [
    path('', JobDescriptionViewSet.as_view({'get': 'list', 'post': 'create'}), name='job description'),
    path('<int:pk>/', JobDescriptionViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='job_description')
]
