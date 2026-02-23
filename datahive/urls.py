from django.urls import path, include
from .views import Documentsviewset
from . import url_enhanced

urlpatterns = [
    path('',Documentsviewset.as_view({'post':'create'})),
    path('list/data/',Documentsviewset.as_view({'post':'list'})),
    path('<pk>/',Documentsviewset.as_view({'delete':'delete','patch':'patch'})),
    path('tags/list/',Documentsviewset.as_view({'post':'get_tags'})),

    # Enhanced routes (separate module so old logic isn't impacted)
    path('enhanced/', include(('datahive.url_enhanced','datahive'), namespace='datahive_enhanced')),
]
