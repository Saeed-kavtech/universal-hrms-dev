from django.urls import path
from .views import *

urlpatterns = [
    path('', TrainingViewSet.as_view({'post': 'create','get':'list'})),
    path('<pk>/', TrainingViewSet.as_view({'patch': 'patch','delete':'delete'})),
    path('stop/<pk>/', TrainingViewSet.as_view({'patch': 'stop_training'})),
    path('employee/<pk>/', TrainingViewSet.as_view({'post': 'add_training_employee','get':'get_training_employee','delete':'remove_training_employee'})),
    path('employee/id/<pk>/',TrainingViewSet.as_view({'patch':'update_training_employee','delete':'remove_training_employee_single'})),
    path('upload/invoice/employee/id/<pk>/',EmployeeTrainingViewset.as_view({'patch':'upload_training_invoice'})),
    path('hr/reimbursement/approval/employee/id/<pk>/',TrainingViewSet.as_view({'patch':'reimbursement_approval_by_hr'})),
    path('assignment/<pk>/', TrainingViewSet.as_view({'get':'get_training_assignment','post':'add_training_assignment'})),
    path('assignment/show/to/hr/<pk>/',TrainingViewSet.as_view({'get':'get_training_assignment_uploaded_by_emplyee'})),
    # path('evaluator/training/data', EmployeeTrainingViewset.as_view({'get':'evaluator_training_data'})),
    path('evaluator/data/', EmployeeTrainingViewset.as_view({'get':'traning_evaluator_training_data'})),
    path('evaluator/employee/uploaded/assignment/<pk>/',EmployeeTrainingViewset.as_view({'post':'traning_evaluator_training_upload_assignment'})),
    # Assignmnet id
    path('assignment/id/<pk>/', TrainingViewSet.as_view({'patch':'update_training_assignment','delete':'remove_training_assignment'})),
    
    path('employee/training/data/',EmployeeTrainingViewset.as_view({'get':'get_employee_trainings'})),
    path('employee/start/training/<pk>/',EmployeeTrainingViewset.as_view({'patch':'training_started_by_employee'})),
    # Training  id
    path('assignment/upload/by/employee/<pk>/', EmployeeTrainingViewset.as_view({'get':'list'})),
    # Employee Assignment id
    path('assignment/uploaded/by/employee/<pk>/', EmployeeTrainingViewset.as_view({'patch':'patch','delete':'delete'})),
    path('add/marks/assignment/uploaded/by/employee/<pk>/', EmployeeTrainingViewset.as_view({'patch':'add_assignment_marks'})),
    path('assignment/upload/by/employee/', EmployeeTrainingViewset.as_view({'post':'create'})),
    
    
    # other ulrs
    path('counts/employee/',EmployeeTrainingViewset.as_view({'get':'employee_training_counts'})),
    path('pre/data/',TrainingViewSet.as_view({'get':"pre_data"})),
    path('add/project/in/training/',TrainingViewSet.as_view({'post':'add_project_in_training'})),
    
    path('add/training/in/project/',TrainingViewSet.as_view({'post':'add_training_in_project'})),
    path('project/data/',TrainingViewSet.as_view({'get':"get_list_project_traning"})),
    path('project/remove/<pk>/',TrainingViewSet.as_view({'delete':'remove_project_from_training'})),
    path('project/employee/data/',EmployeeTrainingViewset.as_view({'get':'get_employee_project_based_traninings'})),
    path('employees/date/based/',TrainingViewSet.as_view({'post':'get_list_datewise_traning'})),
]