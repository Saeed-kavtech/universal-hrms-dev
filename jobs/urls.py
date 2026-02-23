from django.urls import path
from .views import JobsViewset, PreJobDataView, GetDataViewset, JobsForKavtechWebsiteViewSet

urlpatterns = [
    path('', JobsViewset.as_view({'get': 'list', 'post': 'create'}), name='jobs'),
    path('<uuid>/', JobsViewset.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete':'destroy'}), name='jobs'),
    path('<uuid>/activate/', JobsViewset.as_view({'patch': 'activate_job'}), name='activate_job'),
    path('<uuid>/deactivate/', JobsViewset.as_view({'get': 'deactivate_job_post'}), name='deactivate_job_post'),
    path('<uuid>/jd/', GetDataViewset.as_view({'get': 'get_jd_data'})),    
    path('pre/data/<org_id>/', PreJobDataView.as_view()),
    
    path('kavtech/website/', JobsForKavtechWebsiteViewSet.as_view({'get': 'list'})),
]
