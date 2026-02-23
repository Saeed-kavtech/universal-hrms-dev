from django.urls import path
from .views import *
from .views_procedure_types import *

urlpatterns = [
    path('', OrganizationViewset.as_view({'get': 'list', 'post': 'create'}), name='organization'),
    path('<int:pk>/', OrganizationViewset.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='organization'),
    path('objects/<int:pk>/', OrganizationViewset.as_view({'get': 'organizationObjects'}), name='org_objects'),
    path('data/count/', DashboardSetupCount.as_view({'get': 'list'})),

    path('staff_classification/', StaffClassificationViewset.as_view({'get': 'list', 'post': 'create'})),
    path('staff_classification/<int:pk>/', StaffClassificationViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),
    path('staff_classification/initial/adjustment/', StaffClassificationViewset.as_view({'get': 'initial_adjustment'})),
    
    path('procedures/types/', ProcedureTypesViewset.as_view({'get': 'list', 'post': 'create'}), name='procedure_types'),
    path('procedures/types/<pk>/', ProcedureTypesViewset.as_view({'get': 'get', 'patch': 'partial_update', 'delete': 'destroy'}), name='procedure_type'),
    
    path('apis/keys/',OrganizationApikeysviewset.as_view({'get': 'list', 'post': 'create'})),
    path('tokens/',ThirdPartyTokensviewset.as_view({'get': 'list', 'post': 'create'})),
    path('update/existing/tokens/',ThirdPartyTokensviewset.as_view({'get': 'update_tokens'})),
    path('allow/module/access/',OrganizationModuleAccessViewset.as_view({"post":"create"})),
    path('allow/module/access/list/',OrganizationModuleAccessViewset.as_view({"post":"list"})),
    path('allow/module/access/<pk>/',OrganizationModuleAccessViewset.as_view({"delete":"delete"})),
    # path('create/new/meeting/',ThirdPartyTokensviewset.as_view({"post":"create_meetings"})),
    # path('meetings/list/',ThirdPartyTokensviewset.as_view({'get': 'meetings_list'})),
    # path('meetings/list/<pk>/',ThirdPartyTokensviewset.as_view({'get': 'meeting_detalis'})),
]