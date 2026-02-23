from django.urls import path
from .views import *
from .views_candidate_evaluations import *

urlpatterns = [
    
    path('procedures/roles/access/', RoleProcedureAccessViewset.as_view({'get': 'list', 'post': 'create'}), name='procedure_role_accesses'),
    path('procedures/roles/access/<pk>/', RoleProcedureAccessViewset.as_view({'get': 'get', 'patch': 'partial_update', 'delete': 'destroy'}), name='procedure_role_access'),

    path('', EvaluationsViewset.as_view({'get': 'list', 'post': 'create'}), name='evaluations'),
    path('<uuid>/', EvaluationsViewset.as_view({'get': 'get', 'patch': 'partial_update', 'delete': 'destroy'}), name='evaluation'),

    path('<uuid>/procedure/questions/', EvaluationProcedureQuestionsViewset.as_view({'get': 'list', 'post': 'create'}), name='evaluation_questions'),
    path('<uuid>/procedure/questions/<pk>/', EvaluationProcedureQuestionsViewset.as_view({'get': 'get', 'patch': 'partial_update', 'delete': 'destroy'}), name='evaluation_question'),

    path('candidate/job/set/<uuid>/', CandidateEvaluationViewset.as_view({'post': 'set_candidate_evaluation'}), name='set_candidate_evaluation'),
    path('candidate/job/list/<uuid>/', CandidateEvaluationViewset.as_view({'get': 'list_candidate_evaluation'}), name='list_candidate_evaluation'),
    path('candidate/job/get/<uuid>/<pk>/', CandidateEvaluationViewset.as_view({'get': 'get_candidate_evaluation'}), name='get_candidate_evaluation'),
    path('candidate/job/get/by/stage/<uuid>/<stage>/', CandidateEvaluationViewset.as_view({'get': 'get_by_stage_candidate_evaluation'}), name='get_by_stage_evaluation'),
    path('candidate/job/update/<uuid>/<pk>/', CandidateEvaluationViewset.as_view({'patch': 'update_candidate_evaluation'}), name='update_candidate_evaluation'),
    path('candidate/job/start/<uuid>/<pk>/', CandidateEvaluationViewset.as_view({'get': 'start_candidate_evaluation'}), name='start_candidate_evaluation'),
    path('candidate/job/detail/<uuid>/<pk>/', CandidateEvaluationViewset.as_view({'get': 'detail_candidate_evaluation'}), name='detail_candidate_evaluation'),
    path('candidate/job/cancel/<uuid>/<pk>/', CandidateEvaluationViewset.as_view({'patch': 'cancel_candidate_evaluation'}), name='cancel_candidate_evaluation'),
    path('candidate/job/submit/questions/remarks/<uuid>/<pk>/', CandidateEvaluationViewset.as_view({'post': 'submit_candidate_evaluation'}), name='submit_candidate_evaluation'),
    path('candidate/job/recheck/questions/remarks/<uuid>/<pk>/', CandidateEvaluationViewset.as_view({'get': 'recheck_candidate_evaluation'}), name='recheck_candidate_evaluation'),
    path('candidate/job/mark/done/questions/remarks/<uuid>/<pk>/', CandidateEvaluationViewset.as_view({'get': 'mark_as_done_candidate_evaluation'}), name='mark_as_done_candidate_evaluation'),
    path('candidate/job/action/logs/<uuid>/<pk>/', CandidateEvaluationViewset.as_view({'get': 'candidate_evaluation_action_log'}), name='candidate_evaluation_action_log'),
]