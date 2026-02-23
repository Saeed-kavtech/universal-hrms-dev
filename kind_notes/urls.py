from django.urls import path
from .views import KindNotesViewset, kindNotesPreDataView, kindNotesUniversalViewset

urlpatterns = [    
    path('kind-notes/', KindNotesViewset.as_view({'post': 'create'})),
    path('kind-notes/sent/', KindNotesViewset.as_view({'get': 'list'}, name='sender-notes')),
    path('kind-notes/received/', KindNotesViewset.as_view({'get': 'received_notes'})),
    path('kind-notes/<note_id>/', KindNotesViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),
    path('kind-notes/pre/data/', KindNotesViewset.as_view({'get': 'pre_data'})),
    
    path('organization/<organization_id>/kind-notes/pre/data/', kindNotesPreDataView.as_view()),
    path('organization/<organization_id>/kind-notes/view/', kindNotesUniversalViewset.as_view({'get': 'list'})),
]
