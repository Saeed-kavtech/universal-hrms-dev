from django.urls import path
from .views import *

urlpatterns = [
    path('', AssessmentTestFilesViewset.as_view({'get': 'list', 'post': 'create'}), name='assessment_list'),
    path('list/<uuid>/', CandidateAssessmentTestViewset.as_view({'get': 'listCandidateAssessmentTests'}), name='candidate_assessments_list'),
    path('<uuid>/<post_uuid>/', CandidateAssessmentTestViewset.as_view({'get': 'checkCandidateElligiblility'}), name='check_candidate_tests'),
    path('candidate/check/job/post/<cnic>/<post_uuid>/', CandidateAssessmentTestViewset.as_view({'get': 'checkCandidateElligiblility'}), name='check_candidate_tests'),
    path('candidate/check/job/post/<cnic>/', CandidateAssessmentTestViewset.as_view({'get': 'checkCandidateJobRecords'})),
    path('list/onboarding/employees/<candidate_job_id>/<candidate_id>/', OnboardingCandidatesviewset.as_view({'get': 'get_onboarding_candidates'})),
    path('deactivate/candidate/<uuid>/', CandidateAssessmentTestViewset.as_view({'get': 'deactivateCandidateTest'}), name='deactivate_candidate_tests'),
    path('candidate/assessment/test/<uuid>/', CandidateAssessmentTestViewset.as_view({'get': 'startCandidateAssessmentTest', 'post': 'saveAndNextQuestion'}), name='start_candidate_tests'),
    path('candidate/assessment/test/<uuid>/', CandidateAssessmentTestViewset.as_view({'post': 'saveAndNextQuestion'}), name='save_next_question'),
    path('list/questions/all/', AssessmentTestFileQuestionsViewset.as_view({'post': 'listAssessmentTestQuestions'}), name='list_questions')
]

