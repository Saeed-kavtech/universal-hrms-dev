from django.urls import path
from .views import *
from .views_candidate_emails import *

urlpatterns = [
    path('', EmailTemplatesViewset.as_view({'get': 'list', 'post': 'create'}), name='email_templates'),
    path('<uuid>/', EmailTemplatesViewset.as_view({'get': 'get', 'patch': 'partial_update', 'delete': 'destroy'}), name='email_template'),

    path('candidate/job/<uuid>/', CandidateEmailsViewset.as_view({'get': 'list', 'post': 'create'}), name='view_candidate_email_templates'),
    path('candidate/job/view/<uuid>/<pk>/', CandidateEmailsViewset.as_view({'get': 'view_candidate_email_template'}), name='view_candidate_email_template'),
    path('candidate/job/get/stage/<uuid>/<stage>/', CandidateEmailsViewset.as_view({'get': 'get_by_stage_candidate_email'}), name='get_by_stage_candidate_email'),
    path('candidate/job/reset/stage/<uuid>/<stage>/', CandidateEmailsViewset.as_view({'post': 're_set_candidate_email'}), name='re_set_candidate_email'),
    path('candidate/job/save/<uuid>/<pk>/', CandidateEmailsViewset.as_view({'patch': 'save_candidate_email_body'}), name='save_candidate_email_body'),
    path('candidate/job/email/send/<uuid>/<pk>/', CandidateEmailsViewset.as_view({'get': 'send_candidate_email'}), name='send_candidate_email'),

]