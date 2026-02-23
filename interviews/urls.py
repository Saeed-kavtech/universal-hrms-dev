from django.urls import path
from .views import *

urlpatterns = [
    path('mode/', InterviewModeViewset.as_view({'get': 'list', 'post': 'create'}), name='interview_modes'),
    path('mode/<pk>/', InterviewModeViewset.as_view({'get': 'get', 'patch': 'partial_update'}), name='interview_mode'),

    path('candidate/job/<uuid>/', CandidateInterviewsViewset.as_view({'get': 'list', 'post': 'create'}), name='candidate_interviews'),
    path('upcoming/interviews/', CandidateInterviewsViewset.as_view({'get': 'get_upcoming_interviews'})),
    path('today/interviews/',CandidateInterviewsViewset.as_view({'get': 'get_today_interviews'})),
    path('candidate/job/<uuid>/<pk>/', CandidateInterviewsViewset.as_view({'get': 'get', 'patch': 'partial_update'}), name='candidate_interview'),
    path('candidate/job/start/<uuid>/<pk>/', CandidateInterviewsViewset.as_view({'get': 'start_candidate_interview'}), name='start_candidate_interview'),
    path('candidate/job/get/stage/<uuid>/<stage>/', CandidateInterviewsViewset.as_view({'get': 'get_by_stage'}), name='get_by_stage'),
    path('candidate/job/cancel/<uuid>/<pk>/', CandidateInterviewsViewset.as_view({'patch': 'cancel_candidate_interview'}), name='cancel_candidate_interview'),
    path('candidate/job/mark/complete/<uuid>/<pk>/', CandidateInterviewsViewset.as_view({'get': 'mark_complete_candidate_interview'}), name='mark_complete_candidate_interview'),
    # path('candidate/job/mark/complete/<uuid>/<pk>/', CandidateInterviewsViewset.as_view({'get': 'mark_complete_candidate_interview'}), name='mark_complete_candidate_interview'),
    path('candidate/job/reschedule/<uuid>/<pk>/', CandidateInterviewsViewset.as_view({'post': 'reschedule_candidate_interview'}), name='reschedule_candidate_interview'),

]