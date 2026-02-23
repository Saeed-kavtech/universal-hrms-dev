from django.urls import path
from .views import *

urlpatterns = [
    path('', CandidatesViewset.as_view({'post': 'list'})),
    path('<uuid>/', CandidatesViewset.as_view({'get': 'get'})),
    path('apply/job/pre/data/<uuid>/', CandidatesViewset.as_view({'get': 'candidate_job_pre_data'})),
    path('apply/form/<uuid>/', CandidatesViewset.as_view({'post': 'create'})),
    path('filter/pre/data/',CandidatesViewset.as_view({"get":"filter_pre_data"})),
    path('apply/form/<int:pk>/', CandidatesViewset.as_view({'partial_update':'patch', 'update': 'update', 'destroy': 'delete', 'get': 'get'}), name='job'),
    path('stage/update/', CandidateStagesViewset.as_view({'patch':'patch'}), name='candidate_job_stage'),
    path('pre/data/', PreDataCandidateJobsActions.as_view(), name='pre_data_candidate_job_apply'),
    path('job/status/update/<uuid>/', CandidateStatusActionsViewset.as_view({'post': 'update_candidate_status'}), name='update_candidate_status'),
    path('list/job/<uuid>/', CandidateStatusActionsViewset.as_view({'get': 'list_candidate_by_job_post'}), name='list_candidate_by_job_post'),
    path('add/to/job/post/<uuid>/', CandidateStatusActionsViewset.as_view({'post': 'add_candidate_to_job_post'}), name='add_candidate_to_job_post'),
    path('add/list/to/job/post/<uuid>/', CandidateStatusActionsViewset.as_view({'post': 'add_list_of_candidate_to_job_post'}), name='add_list_of_candidate_to_job_post'),
    path('list/by/position/exclude/job/candidates/<uuid>/', CandidateStatusActionsViewset.as_view({'get': 'list_candidate_by_position_exclude_job_candidates'}), name='list_candidate_by_position_exclude_job_candidates')

]

