from django.urls import path

from reimbursements.views_wfh import EmployeesWFHRequestViewset
from .views_gym import (
    GymAllowanceViewset, EmployeesGymAllowanceViewset, GymStatusLogsViewset, 
    PreviousGymDataScriptsViewset
)
from .views_medical import (
    MedicalAllowanceViewset, EmployeesMedicalAllowanceViewset, MedicalStatusLogsViewset,
    EmployeesRemainingMedicalAllowanceViewset, PreviousMedicalDataScriptsViewset,NewEmployeeMedicalAllowanceViewset
)
from .views_pf import ProvidentFundsViewset, EmployeeProvidentFundsViewset, ProvidentFundStatusLogsViewset

from .views_leaves import (
    LeaveTypesViewset, SetLeavesDurationViewset, EmployeesLeavesViewset, 
    LeavesStatusLogsViewset, EmployeeLeaveCalculationScriptsViewset, EmployeesOfficialHolidaysViewset, 
    NewJoiningEmployeesLeavePreViewset,NewEmployeeLeaveAllowanceViewset,NewEmployeeLeaveNSCAllowanceViewset, CompensatoryLeavesViewset, HRCompensatoryLeavesViewset
)
from .views_pre_data import AllowancesViewset, PreDataReimbursementRequest, PreDataEmployeeReimbursementRequest, PreDataGetEmployeeRequests
from .views_loan import SetLoanRequirementsViewset, EmployeesLoanViewset, LoanStatusLogsViewset

urlpatterns = [    
    path('set/gym/allowance/limit/', GymAllowanceViewset.as_view({'get': 'list', 'post': 'create'})),
    path('set/gym/allowance/limit/<pk>/', GymAllowanceViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),
    path('employees/gym/allowance/', EmployeesGymAllowanceViewset.as_view({'get': 'list', 'post': 'create'})),
    path('employees/gym/allowance/<pk>/', EmployeesGymAllowanceViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),
    path('update/gym/allowance/status/<pk>/', GymStatusLogsViewset.as_view({'get': 'list', 'patch': 'patch'})),
    path('update/multi/gym/allowance/status/', GymStatusLogsViewset.as_view({'patch': 'update_gym_status'})),
    path('previous/gym/data/script/', PreviousGymDataScriptsViewset.as_view({'get': 'list', 'post': 'create'})),
    path('new/employee/leave/set/script/',NewEmployeeLeaveAllowanceViewset.as_view({'post':'NewEmployeeLeaveSet'})),
    path('new/employee/medical/set/script/',NewEmployeeMedicalAllowanceViewset.as_view({'get':'NewEmployeeMedicalSet'})),
    path('new/employee/nsc/leave/set/script/',NewEmployeeLeaveNSCAllowanceViewset.as_view({'post':'NewEmployeeNSCLeaveSet'})),
    path('allowance/script/logs/<pk>/',NewJoiningEmployeesLeavePreViewset.as_view({'get':'scripts_logs_data'})),
    path('set/medical/allowance/limit/', MedicalAllowanceViewset.as_view({'get': 'list', 'post': 'create'})),
    path('set/medical/allowance/limit/<pk>/', MedicalAllowanceViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),
    path('employees/medical/allowance/', EmployeesMedicalAllowanceViewset.as_view({'get': 'list', 'post': 'create'})),
    path('employees/medical/allowance/<pk>/', EmployeesMedicalAllowanceViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),
    path('update/medical/allowance/status/<pk>/', MedicalStatusLogsViewset.as_view({'get': 'list', 'patch': 'patch'})),
    path('update/multi/medical/allowance/status/', MedicalStatusLogsViewset.as_view({'patch': 'update_medical_stauts'})),
    path('employees/medical/allowance/remaining/script/', EmployeesRemainingMedicalAllowanceViewset.as_view({'post': 'sync_data', 'get': 'get'})),
    path('previous/medical/data/script/', PreviousMedicalDataScriptsViewset.as_view({'post': 'create'})),
    path('set/provident-fund/percentage/', ProvidentFundsViewset.as_view({'get': 'list', 'post': 'create', 'destroy': 'delete'})),
    path('employees/provident-fund/', EmployeeProvidentFundsViewset.as_view({'get': 'list', 'post': 'create'})),
    path('update/provident-fund/status/<pk>/', ProvidentFundStatusLogsViewset.as_view({'get': 'list', 'patch': 'patch'})),
    
    path('set/leave/types/', LeaveTypesViewset.as_view({'get': 'list', 'post': 'create'})),
    path('set/leave/types/<pk>/', LeaveTypesViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),
    path('set/leave/duration/limit/', SetLeavesDurationViewset.as_view({'get': 'list', 'post': 'create'})),
    path('set/leave/duration/limit/<pk>/', SetLeavesDurationViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})), 
    path('unlock/leave/duration/limit/<pk>/', SetLeavesDurationViewset.as_view({'patch': 'patch_unlock_leave'})), 
    path('employees/leaves/', EmployeesLeavesViewset.as_view({'get': 'list', 'post': 'create'})),
    path('employees/leaves/<pk>/', EmployeesLeavesViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),
    path('update/leaves/status/<pk>/', LeavesStatusLogsViewset.as_view({'get': 'list', 'patch': 'patch'})),
    path('update/multi/leaves/status/',LeavesStatusLogsViewset.as_view({'patch':'update_leave_status'})),
    path('employees/yearly/official/holidays/', EmployeesOfficialHolidaysViewset.as_view({'get': 'list', 'post': 'create'})),
    path('employees/yearly/official/holidays/<pk>/', EmployeesOfficialHolidaysViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),
    
    path('sync/emp/leave/dates/', EmployeeLeaveCalculationScriptsViewset.as_view({'post': 'sync_emp_leaves_dates'})),
    path('sync/emp/leave/calculation/data/', EmployeeLeaveCalculationScriptsViewset.as_view({'post': 'sync_leave_calculation_data'})),
    path('sync/emp/leave/list/', EmployeeLeaveCalculationScriptsViewset.as_view({'get': 'list'})),
    path('sync/emp/previous/leaves/data/', EmployeeLeaveCalculationScriptsViewset.as_view({'post': 'post_sync_previous_leaves'})),
    path('download/medical/file/',PreviousMedicalDataScriptsViewset.as_view({'get':'download_images'})),
    path('set/loan/requirements/', SetLoanRequirementsViewset.as_view({'get': 'list', 'post': 'create'})),
    path('set/loan/requirements/<pk>/', SetLoanRequirementsViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})), 
    path('unlock/loan/requirements/<pk>/', SetLoanRequirementsViewset.as_view({'get': 'get_unlock_loan'})), 
    path('lock/loan/requirements/<pk>/', SetLoanRequirementsViewset.as_view({'get': 'get_lock_loan'})), 
    path('employees/loans/', EmployeesLoanViewset.as_view({'get': 'list', 'post': 'create'})),
    path('employees/loans/<pk>/', EmployeesLoanViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),
    path('update/loan/status/<pk>/', LoanStatusLogsViewset.as_view({'get': 'list', 'patch': 'patch'})),

    path('pre/data/', PreDataReimbursementRequest.as_view()), 
    path('employee/pre/data/', PreDataEmployeeReimbursementRequest.as_view()), 
    path('employee/recode/gym/data/',EmployeesGymAllowanceViewset.as_view({'post':"get_pre_data"})),
    path('employee/recode/medical/data/',EmployeesMedicalAllowanceViewset.as_view({'post':"get_pre_data"})),
    path('employee/recode/pf/data/',EmployeeProvidentFundsViewset.as_view({'post':"get_pre_data"})),
    path('employee/recode/leave/data/',EmployeesLeavesViewset.as_view({'post':"get_pre_data"})),
    path('employee/recode/loan/data/',EmployeesLoanViewset.as_view({'post':"get_pre_data"})),
    path('employee/requests/gym/data/',GymStatusLogsViewset.as_view({'post':"get_all_gym_requests"})),
    path('employee/requests/medical/data/',MedicalStatusLogsViewset.as_view({'post':"get_all_medical_requests"})),
    path('employee/requests/pf/data/',ProvidentFundStatusLogsViewset.as_view({'post':"get_all_pf_requests"})),
    path('employee/requests/leaves/data/',LeavesStatusLogsViewset.as_view({'post':"get_all_leaves_requests_new"})),
    path('employee/requests/loan/data/',LoanStatusLogsViewset.as_view({'post':"get_all_loan_requests"})),
    path('employee/requests/pre/data/', PreDataGetEmployeeRequests.as_view()),
    path('employee/leave/script/<pk>/',NewEmployeeLeaveAllowanceViewset.as_view({'post':'allow_emp_leaves'})),
    path('employee/medical/script/<pk>/',NewEmployeeMedicalAllowanceViewset.as_view({'post':'allow_emp_medical'})),
    path('employee/nsc/leave/script/<pk>/',NewEmployeeLeaveNSCAllowanceViewset.as_view({'post':'allow_emp_nsc_leaves'})),
    path('download/medical/approved/file/',PreviousMedicalDataScriptsViewset.as_view({'post':'donwload_medical_approved_files'})),
    path('delete/employee/all/allowances/<pk>/',NewJoiningEmployeesLeavePreViewset.as_view({'delete':'delete_employee_allowance'})),
    path('allowance/script/logs/<pk>/',NewJoiningEmployeesLeavePreViewset.as_view({'get':'scripts_logs_data'})),

      # Compensatory Leaves
    path('request/compensatory/leaves/', CompensatoryLeavesViewset.as_view({'post':'create', 'get':'view'})),
    path('remove/compensatory/leaves/<pk>/',CompensatoryLeavesViewset.as_view({'delete':'remove'})),
    path('tl/update/compensatory/<pk>/', CompensatoryLeavesViewset.as_view({'patch':'teamleadupdate'})), 
    path('hr/update/compensatory/<pk>/', HRCompensatoryLeavesViewset.as_view({'patch':'hrupdate'})),
    path('tl/compensatory/list/', CompensatoryLeavesViewset.as_view({'post':'teamleadlist'})),
    path('hr/compensatory/list/', HRCompensatoryLeavesViewset.as_view({'get':'list'})),
    # Custom Query apis
    path('employee/approved/allowance/<employee_id>/',AllowancesViewset.as_view({"post":"get_employee_total_approved_amount"})),
    #Wfh 
    path('employee/wfh/request/', EmployeesWFHRequestViewset.as_view({'get': 'list', 'post': 'create'})),
    path('employee/wfh/request/<pk>/', EmployeesWFHRequestViewset.as_view({'destroy': 'delete'})), 

]

