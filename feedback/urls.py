# from django.urls import path
# from .views import (
#     FeedbackRewriteView,
#     FeedbackViewset,
#     FeedbackPreDataView,
#     FeedbackUniversalViewset,
#     GenerateInitialSummaryAPI,
#     MonthlyFeedbackSummaryAPI,
#     WeeklySummaryAPI,
#     FeedbackSentimentAnalysisAPI,  
#     BatchSentimentAnalysisAPI,   
#     UserScoreAPI,                 
#     CategoryActionsAPI,
#     PermissionCheckAPI,
#     FeedbackPermissionDataAPI,      
#     ScorePermissionDataAPI,         
#     ScoreCategoriesAPI,
#     ProjectEmployeesAPI,
#     ScoreProjectEmployeesAPI,
#     UserDashboardInfoAPI
# )

# urlpatterns = [
#     path('user-dashboard-info/', UserDashboardInfoAPI.as_view(), name='user-dashboard-info'),
#     path('check-permissions/', PermissionCheckAPI.as_view(), name='permission-check'),   
#     path('feedback/', FeedbackViewset.as_view({
#         'post': 'create',
#         'get': 'list',
#     }), name='feedback-list-create'),
    
#     path('feedback/<int:pk>/', FeedbackViewset.as_view({
#         'get': 'retrieve',
#         'patch': 'update',
#         'delete': 'destroy',
#     }), name='feedback-detail'),
    
#     path('feedback/pre/data/', FeedbackPreDataView.as_view(), name='feedback-predata'),
#     path('feedback/permission-data/', FeedbackPermissionDataAPI.as_view(), name='feedback-permission-data'),
#     path('feedback/project-employees/', ProjectEmployeesAPI.as_view(), name='feedback-project-employees'),
    
#     path('rewrite/', FeedbackRewriteView.as_view(), name='feedback-rewrite'),
#     path('feedback/received/', FeedbackViewset.as_view({'get': 'received_feedbacks'}), name='feedback-received'),
#     path('employees/<int:employee_id>/feedbacks/', FeedbackViewset.as_view({'get': 'employee_feedbacks'}), name='employee-feedbacks'),
    
#     path('scores-entries/', UserScoreAPI.as_view(), name='user-scores'),
#     path('scores-permission-data/', ScorePermissionDataAPI.as_view(), name='scores-permission-data'),
#     path('scores-project-employees/', ScoreProjectEmployeesAPI.as_view(), name='scores-project-employees'),
    
#     path('weekly-summaries/', WeeklySummaryAPI.as_view(), name='weekly-summaries'),
#     path('weekly-summaries/generate-initial/', GenerateInitialSummaryAPI.as_view(), name='generate-initial-summary'),
    
#     path('sentiment/analyze/', FeedbackSentimentAnalysisAPI.as_view(), name='sentiment-analyze'),
#     path('sentiment/analyze/batch/', BatchSentimentAnalysisAPI.as_view(), name='sentiment-analyze-batch'),
    
#     path('monthly-summaries/', MonthlyFeedbackSummaryAPI.as_view(), name='monthly-summaries'),
    
#     path('scores/categories/', ScoreCategoriesAPI.as_view(), name='scores-categories'),
#     path('scores-categories/categories/', CategoryActionsAPI.as_view(), name='score-categories-old'),
# ]

from django.urls import path
from .views import (
    FeedbackRewriteView,
    FeedbackViewset,
    FeedbackPreDataView,
    FeedbackUniversalViewset,
    GenerateInitialSummaryAPI,
    MonthlyFeedbackSummaryAPI,
    WeeklySummaryAPI,
    FeedbackSentimentAnalysisAPI,  
    BatchSentimentAnalysisAPI,   
    UserScoreAPI,                 
    CategoryActionsAPI,
    PermissionCheckAPI,
    FeedbackPermissionDataAPI,      
    ScorePermissionDataAPI,         
    ScoreCategoriesAPI,
    ProjectEmployeesAPI,
    ScoreProjectEmployeesAPI,
    UserDashboardInfoAPI,
    AnnualFeedbackSummaryAPI
)

urlpatterns = [
    path('user-dashboard-info/', UserDashboardInfoAPI.as_view(), name='user-dashboard-info'),
    path('check-permissions/', PermissionCheckAPI.as_view(), name='permission-check'),   
    path('feedback/', FeedbackViewset.as_view({
        'post': 'create',
        'get': 'list',
    }), name='feedback-list-create'),
    
    path('feedback/<int:pk>/', FeedbackViewset.as_view({
        'get': 'retrieve',
        'patch': 'update',
        'delete': 'destroy',
    }), name='feedback-detail'),
    
    path('feedback/pre/data/', FeedbackPreDataView.as_view(), name='feedback-predata'),
    path('feedback/permission-data/', FeedbackPermissionDataAPI.as_view(), name='feedback-permission-data'),
    path('feedback/project-employees/', ProjectEmployeesAPI.as_view(), name='feedback-project-employees'),
    
    path('rewrite/', FeedbackRewriteView.as_view(), name='feedback-rewrite'),
    path('feedback/received/', FeedbackViewset.as_view({'get': 'received_feedbacks'}), name='feedback-received'),
    path('employees/<int:employee_id>/feedbacks/', FeedbackViewset.as_view({'get': 'employee_feedbacks'}), name='employee-feedbacks'),
    
    path('scores-entries/', UserScoreAPI.as_view(), name='user-scores'),
    path('scores-permission-data/', ScorePermissionDataAPI.as_view(), name='scores-permission-data'),
    path('scores-project-employees/', ScoreProjectEmployeesAPI.as_view(), name='scores-project-employees'),
    
    path('weekly-summaries/', WeeklySummaryAPI.as_view(), name='weekly-summaries'),
    path('weekly-summaries/generate-initial/', GenerateInitialSummaryAPI.as_view(), name='generate-initial-summary'),
    
    path('sentiment/analyze/', FeedbackSentimentAnalysisAPI.as_view(), name='sentiment-analyze'),
    path('sentiment/analyze/batch/', BatchSentimentAnalysisAPI.as_view(), name='sentiment-analyze-batch'),
    
    path('monthly-summaries/', MonthlyFeedbackSummaryAPI.as_view(), name='monthly-summaries'),

    path('feedback/annual-summary/', AnnualFeedbackSummaryAPI.as_view(), name='annual-feedback-summary'),
    
    path('scores/categories/', ScoreCategoriesAPI.as_view(), name='scores-categories'),
    path('scores-categories/categories/', CategoryActionsAPI.as_view(), name='score-categories-old'),
]