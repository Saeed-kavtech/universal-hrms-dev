from django.urls import path
from .views import *
urlpatterns = [

    # Employee Urls
    path('employee/',LNDCertificationsViewset.as_view({'get': 'list','post':'create'})),
    path('employee/<pk>/',LNDCertificationsViewset.as_view({'patch':'patch','delete': 'delete'})),
    path('certificate/submission/<pk>/',SubmissionLNDCertificationsViewset.as_view({'patch':'certificate_submission'})),
    path('submission/employee/',SubmissionLNDCertificationsViewset.as_view({'get':'get_submission_to_employee'})),
    path('submission/employee/<pk>/',SubmissionLNDCertificationsViewset.as_view({'get':'get_specific_submission_to_employee'})),
    # Team Lead Urls
    path('team/lead/list/',LNDCertificationsViewset.as_view({'get':'get_request_to_teamlead'})),
    path('team/lead/approval/<pk>/',LNDCertificationsViewset.as_view({'patch':'approval_by_team_lead'})),
    path('submission/team/lead/',SubmissionLNDCertificationsViewset.as_view({'get':'get_submission_to_team_lead'})),
    path('submission/team/lead/<pk>/',SubmissionLNDCertificationsViewset.as_view({'get':'get_specific_submission_to_team_lead'})),
    # HR Urls
    path('assign/team/lead/<pk>/',LNDCertificationsViewset.as_view({'patch':'assign_team_lead'})),
    path('hr/list/',LNDCertificationsViewset.as_view({'get':'get_request_to_hr'})),
    path('hr/approval/<pk>/',LNDCertificationsViewset.as_view({'patch':'approval_by_hr'})),
    path('hr/approval/reimbursement/<pk>/',SubmissionLNDCertificationsViewset.as_view({'patch':'reimbursement_approval_by_hr'})),
    path('submission/hr/',SubmissionLNDCertificationsViewset.as_view({'get':'get_submission_to_hr'})),
    path('submission/hr/<pk>/',SubmissionLNDCertificationsViewset.as_view({'get':'get_specific_submission_to_hr'})),
    
    #Other Urls
    path('pre/data/',CertificationPreDataViewset.as_view({'get':'list'})),
]