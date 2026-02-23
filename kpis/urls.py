from django.urls import path
from .views import (
    EPYearlySegmentationViewset, EmployeesKpisViewset, KpisEvaluationViewset, 
    KpisCommentsViewset, KpisPreDataViewset
)


urlpatterns = [    
    path('set/yearly/segmentation/', EPYearlySegmentationViewset.as_view({'get': 'list', 'post': 'create'})),
    path('set/yearly/segmentation/<pk>/', EPYearlySegmentationViewset.as_view({'patch': 'patch'})),
    path('set/yearly/segmentation/lock/data/', EPYearlySegmentationViewset.as_view({'get': 'lock_batch'})),
    path('set/yearly/segmentation/complete/batch/<pk>/', EPYearlySegmentationViewset.as_view({'patch': 'complete_batch_only'})),
    path('set/yearly/segmentation/start/batch/<pk>/', EPYearlySegmentationViewset.as_view({'patch': 'start_batch'})),
    path('make/yearly/segmentation/completed/', EPYearlySegmentationViewset.as_view({'patch': 'complete_yearlysegmentation'})),
    path('set/yearly/segmentation/unlock/data/', EPYearlySegmentationViewset.as_view({'get': 'unlock_batch'})),
    
    # employee urls
    path('employees/', EmployeesKpisViewset.as_view({'get': 'list', 'post': 'create'})),
    path('employees/<pk>/', EmployeesKpisViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'delete': 'delete'})),
    path('employees/kpi/data/',EmployeesKpisViewset.as_view({'post':'kpi_data'})),
    path('update/scale/group/script/<pk>/', KpisPreDataViewset.as_view({'patch': 'employee_update_scale_group'})),
    path('update/scale/group/organization/', KpisPreDataViewset.as_view({'patch': 'organization_update_scale_group'})),
    # path('employees/stage/list/', EmployeesKpisViewset.as_view({'get': 'get_approved_by_team_member'})),
    path('employees/approval/list/', EmployeesKpisViewset.as_view({'post': 'get_approval_by_team_member_list'})),
    path('requests/to/employee/', KpisEvaluationViewset.as_view({'get': 'get_request_to_employee'})), 
    path('employee/pervious/batch/kpis/data/', KpisEvaluationViewset.as_view({'post':'get_pervious_batch_employee_kpis'})),
    
    #employee and team lead urls
    path('assign/scale/group/<pk>/', EmployeesKpisViewset.as_view({'patch': 'assign_scale_group'})),
    path('employees/file/script/',EmployeesKpisViewset.as_view({'get':'uploadkpis'})),
    path('team/lead/pervious/batch/kpis/data/', KpisEvaluationViewset.as_view({'post':'get_pervious_batch_team_lead_kpis'})),
    
    #team lead  urls
    path('team/lead/employees/', EmployeesKpisViewset.as_view({'post': 'create_by_team_lead'})),
    path('requests/to/team/lead/', KpisEvaluationViewset.as_view({'get': 'get_request_to_teamlead'})), 
    path('requests/to/team/lead/data/<pk>/', KpisEvaluationViewset.as_view({'get': 'get_request_to_teamlead_data'})),
    path('team/lead/approval/list/', KpisEvaluationViewset.as_view({'post': 'get_approval_by_team_lead_list'})),
    path('team/lead/review/<pk>/', KpisEvaluationViewset.as_view({'patch': 'update_by_team_lead'})), 
    # path('team/lead/approval/<pk>/', KpisEvaluationViewset.as_view({'get': 'get_approval_by_team_lead'})),
    
    # TL recheck urls
    path('recheck/requests/to/team/lead/', KpisEvaluationViewset.as_view({'get': 'get_recheck_request_to_teamlead'})),
    path('recheck/requests/to/team/lead/data/<pk>/', KpisEvaluationViewset.as_view({'get': 'get_recheck_request_to_teamlead_data'})),
    
    # TL cancel urls
    path('cancel/requests/by/team/lead/<pk>/', KpisEvaluationViewset.as_view({'patch': 'cancel_request_by_team_lead'})),
    path('cancel/requests/to/team/lead/', KpisEvaluationViewset.as_view({'get': 'get_cancel_request_to_teamlead'})), 
    path('cancel/requests/to/team/lead/data/<pk>/', KpisEvaluationViewset.as_view({'get': 'get_cancel_request_to_teamlead_data'})),
    # HR urls
    path('hr/approval/list/', KpisEvaluationViewset.as_view({'post': 'get_approval_by_hr_list'})),
    path('requests/to/hr/', KpisEvaluationViewset.as_view({'get': 'get_request_to_hr'})), 
    path('requests/to/hr/data/<pk>/', KpisEvaluationViewset.as_view({'get': 'get_request_to_hr_data'})),
    path('hr/pervious/batch/kpis/data/', KpisEvaluationViewset.as_view({'post':'get_pervious_batch_hr_kpis'})),
    
    # HR recheck urls
    path('hr/recheck/approval/list/', KpisEvaluationViewset.as_view({'post': 'get_recheck_approval_by_hr_list'})),
    path('recheck/requests/to/hr/<pk>/', KpisEvaluationViewset.as_view({'patch': 'recheck_request_to_hr'})), 
    path('recheck/requests/to/hr/', KpisEvaluationViewset.as_view({'get': 'get_recheck_request_to_hr'})), 
    path('recheck/requests/to/hr/data/<pk>/', KpisEvaluationViewset.as_view({'get': 'get_recheck_request_to_hr_data'})),
   
    
    # HR cnacel urls
    path('hr/cancel/approval/list/', KpisEvaluationViewset.as_view({'post': 'get_cancle_approval_by_hr_list'})),
    path('cancle/requests/to/hr/', KpisEvaluationViewset.as_view({'get': 'get_cancle_request_to_hr'})),
    path('cancle/requests/to/hr/data/<pk>/', KpisEvaluationViewset.as_view({'get': 'get_cancle_request_to_hr_data'})), 
    
    # other urls
    path('get/scale/group/data/<pk>/',KpisEvaluationViewset.as_view({'get':'get_kpis_scale_group_data'})),
    path('update/eveluator/<pk>/',KpisPreDataViewset.as_view({'patch':'change_employee_eveluator'})),
    # path('get/data/<pk>/',KpisEvaluationViewset.as_view({'get':'get_kpis_data'})),
    path('hr/requests/count/',KpisPreDataViewset.as_view({'get':'hr_requests_count'})),
    path('hr/dashboard/count/',KpisPreDataViewset.as_view({'post':'kpis_dashboard_count'})),
    path('hr/dashboard/preformance/',KpisPreDataViewset.as_view({'post':'kpis_department_based_preformance'})),
    path('hr/dashboard/objectives/',KpisPreDataViewset.as_view({'post':'kpis_department_based_objectives'})),
    path('hr/dashboard/complexity/',KpisPreDataViewset.as_view({'post':'kpis_department_based_complexity'})),
    path('segmenetation/based/result/',KpisPreDataViewset.as_view({'post':'kpis_segmentation_based_result_all'})),
    path('project/based/result/',KpisPreDataViewset.as_view({'post':'kpis_project_based_result'})),
    path('employee/requests/count/',KpisPreDataViewset.as_view({'get':'employee_requests_count'})),
    path('add/comments/<pk>/', KpisCommentsViewset.as_view({'post': 'create'})),
    path('get/comments/<pk>/', KpisCommentsViewset.as_view({'get': 'list'})),
    path('pre/data/', KpisPreDataViewset.as_view({'get': 'list'})),
    path('report/data/',KpisPreDataViewset.as_view({'post':"kpis_report_data"})),
    path('employee/data/<employee_id>/',KpisPreDataViewset.as_view({"post":"get_kpis_data"}))

]
