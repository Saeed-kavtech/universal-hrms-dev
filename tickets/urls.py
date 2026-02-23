from django.urls import path
from .views import *

urlpatterns = [
    path('department/employee/<department_id>/',TicketDepartmentEmployeeViewset.as_view({"get":"list"})),
    path('employee/', TicketViewset.as_view({'get': 'list','post':'create'})),
    path('employee/<pk>/',TicketViewset.as_view({'patch':'patch','delete': 'delete'})),
    path('team/lead/employee/',TicketViewset.as_view({'get':'get_team_lead_ticket'})),
    path('team/lead/employee/<pk>/',TicketViewset.as_view({'patch':'action_by_team_lead'})),
    path('assign/to/employee/',TicketViewset.as_view({'get':'get_assign_to_procurement'})),
    # path('assign/to/employee/general/',TicketViewset.as_view({'get':'get_assign_to_general'})),
    path('transfer/to/employee/',TicketViewset.as_view({'get':'get_transfer_to'})),
    path('transfer/to/other/employee/<pk>/',TicketViewset.as_view({'patch':'ticket_transfer_to'})),
    path('action/by/transfer/to/employee/<pk>/',TicketViewset.as_view({'patch':'action_by_transfer_to'})),
    path('action/by/assign/to/employee/<pk>/',TicketViewset.as_view({'patch':'action_by_assign_to'})),
    path('descision/resaon/data/<pk>/',TicketViewset.as_view({"get":"get_descicion_data"})),
    path('all/data/',TicketViewset.as_view({"get":"get_hr_ticket_data"})),
    path('hr/ticket/requests/',TicketViewset.as_view({"get":"get_hr_services_ticket_data"})),
    path('action/by/hr/<pk>/',TicketViewset.as_view({"patch":"action_by_hr"})),
    path('counts/data/',TicketViewset.as_view({'get':'ticket_counts'})),
    path('get/department/pre/data/',TicketViewset.as_view({"get":"get_ticket_departement"})),
    path('get/department/pre/data/<department_id>/',TicketViewset.as_view({"get":"get_department_details"})),
    # path('get/department/employee/pre/data/<department_id>/',TicketViewset.as_view({"get":"get_departement_employee"})),
    ]