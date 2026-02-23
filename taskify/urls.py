from django.urls import path
from .views import *

urlpatterns = [
    path('task/status/pre/data/',TasksStatusViewset.as_view({"post":"pre_data"})),
    path('task/types/pre/data/',TaskTypesViewset.as_view({"post":"pre_data"})),
     #Groups
    path('group/<project_id>/',TaskGroupsViewset.as_view({"post":"create","get":"list"})),
    path('update/group/<group_id>/',TaskGroupsViewset.as_view({"patch":"patch","delete":"delete"})),
    path('grouping/tasks/<group_id>/',TaskGroupsViewset.as_view({"patch":"task_group_link","post":"get_group_based_tasks"})),
    
    path('projects/pre/data/',TasksStatusViewset.as_view({'get':"taskify_projects"})),
    path('new/task/',TasksViewset.as_view({"post":"create"})),
    path('new/task/<pk>/',TasksViewset.as_view({"patch":"patch","delete":"delete"})),
    path('task/time/log/<pk>/',TaskTimeLogsViewset.as_view({"post":"create",'get':"list"})),
    path('get/single/task/data/<pk>/',TasksViewset.as_view({"get":"get_single_data"})),
    path('delete/task/time/log/<time_log_id>/',TaskTimeLogsViewset.as_view({"delete":"delete"})),
    path('get/task/report/<project_id>/',TaskTimeLogsViewset.as_view({"post":"task_report"})),
    path('get/project/all/task/<project_id>/',TasksViewset.as_view({"post":"list"})),
    path('get/project/',TasksViewset.as_view({"get":"employee_project"})),
    path("update/task/status/<pk>/",TasksViewset.as_view({"patch":"update_task_stauts"})),
    path('get/project/employee/<project_id>/',TasksViewset.as_view({"get":"project_employees"})),
    path('get/project/assign/task/<project_id>/',TasksViewset.as_view({"get":"task_assign_to"})),
    path('get/project/created/task/<project_id>/',TasksViewset.as_view({"get":"task_created_by_employee"})),
    path('attachments/<pk>/',TaskAttachmentsViewset.as_view({"post":"create","get":"list"})),
    path('attachments/list/<pk>/',TaskAttachmentsViewset.as_view({"post":"list"})),
    path('attachments/delete/<attachment_id>/',TaskAttachmentsViewset.as_view({"delete":"delete"})),
    path('comment/<pk>/',TaskCommentViewset.as_view({"post":"create","get":"list"})),
    path('comment/details/<comment_id>/',TaskCommentViewset.as_view({"patch":"patch","delete":"delete"})),
    path('get/project/pre/data/<project_id>/',TaskPreDataviewset.as_view({"get":"get_project_data"})),
    path('get/task/logs/<pk>/',TaskPreDataviewset.as_view({"get":"task_logs_data"})),
    # path('get/task/logs/<pk>/',TaskPreDataviewset.as_view({"get":"task_time_logs_back_log_data"})),
    path('get/child/task/<parent_id>/',TasksViewset.as_view({"get":"get_child_task"})),
    path('get/task/count/report/<project_id>/',TaskTimeLogsViewset.as_view({'get':'get_project_count'})),
   


    

]
