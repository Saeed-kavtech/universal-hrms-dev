from django.urls import path
from .views import EmployeeSalaryRecordsViewset,SalaryRecordsViewset,TaxSlabViewset,PayrollAcountantViewset,SalaryBatchList,PayrollAddonAttributesView,PayrollAttributesViewset, PayrollBatchesViewset, PayrollBatchCompositionsViewset, PrePayrollCompositionDataView, EmployeePayrollConfigurationViewSet, EmployeePayrollConfigurationCreateView, MonthlydistributionView, EligibleEmployeesView, FixedDistributionView, VariableDistributionsView, PayrollBatchAttributesViewset, EmployeesAllowanceList

urlpatterns = [    
    path('attributes/', PayrollAttributesViewset.as_view({'get': 'list', 'post': 'create'})),
    path('attributes/<pk>/', PayrollAttributesViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'delete': 'delete'})),

    path('batch/', PayrollBatchesViewset.as_view({'get': 'retrieve', 'post': 'create', 'delete': 'delete', 'patch':'patch_taxcountry'})),
    # Tax Country
    path('batch/<pk>/', PayrollBatchesViewset.as_view({'patch':'patch_taxcountry'})),

    path('batch/compositions/view/', PayrollBatchCompositionsViewset.as_view({'get': 'list', 'post': 'create'})),
    path('batch/compositions/<pk>/', PayrollBatchCompositionsViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'delete': 'delete'})),
    path('batch/compositions/attributes/<pk>/', PayrollBatchCompositionsViewset.as_view({'patch': 'patch_taxable'})),
    path('lock/batch/compositions/', PayrollBatchCompositionsViewset.as_view({'post': 'lockPayrollComposition'}), name="lock_batch"),
    path('unlock/batch/compositions/', PayrollBatchCompositionsViewset.as_view({'post': 'unlockPayrollComposition'}), name="unlock_batch"),
    path('list/batches/', PayrollBatchCompositionsViewset.as_view({'get': 'listactivepayrollbatches'})),
    
    path('pre/data/view/', PrePayrollCompositionDataView.as_view()),
    
    
path('employee/configuration/', EmployeePayrollConfigurationCreateView.as_view({'post': 'create', 'get': 'list'})),
path('addons/attributes/', PayrollAddonAttributesView.as_view({'post': 'create','get':'list'})),
path('addons/attributes/<pk>/', PayrollAddonAttributesView.as_view({'patch': 'patch'})),
path('deduction/attributes/', PayrollAddonAttributesView.as_view({'get':'deductionlist'})),
path('addons/attributes/<pk>/', PayrollAddonAttributesView.as_view({'delete': 'delete'})),

path('monthly/distribution/limit/', MonthlydistributionView.as_view({'post': 'create', 'get':'list'})),
path('monthly/distribution/limit/<pk>/', MonthlydistributionView.as_view({'delete':'delete', 'patch':'patch'})),

path('monthly/distribution/view/', MonthlydistributionView.as_view({'post':'list'})),

path('monthly/eligible/employees/', EligibleEmployeesView.as_view({'post': 'create'})),
path('monthly/eligible/employees/view/', EligibleEmployeesView.as_view({'post': 'view'})),
# list payroll batch employees
path('batch/employees/records/', EligibleEmployeesView.as_view({'post': 'payrollbatchemployees'})),

path('fixed/amount/', FixedDistributionView.as_view({'post': 'create'})),
path('fixed/amount/view/', FixedDistributionView.as_view({'post': 'view'})),
path('variable/amount/', VariableDistributionsView.as_view({'post': 'create'})),
path('variable/amount/view/', VariableDistributionsView.as_view({'post': 'view'})),

path('batch/add/attributes/', PayrollBatchAttributesViewset.as_view({'post': 'create'})),
path('batch/attributes/view/', PayrollBatchAttributesViewset.as_view({'post': 'list'})),
path('batch/attributes/hrview/', PayrollBatchAttributesViewset.as_view({'post': 'hrlist'})),
path('salary/attributes/list/', PayrollBatchAttributesViewset.as_view({'post': 'salaryattributeslist'})),
path('batch/gym/data/', EmployeesAllowanceList.as_view({'post': 'gymlist'})),
path('batch/pf/data/', EmployeesAllowanceList.as_view({'post': 'pflist'})),
path('delete/emp/pf/<pk>/', EmployeesAllowanceList.as_view({'delete': 'removefrompf'})),
path('add/emp/pf/', EmployeesAllowanceList.as_view({'post': 'addtopf'})),
path('batch/medical/data/', EmployeesAllowanceList.as_view({'post': 'medicallist'})),
path('batch/certifications/data/', EmployeesAllowanceList.as_view({'post': 'certifylist'})),
path('batch/training/data/', EmployeesAllowanceList.as_view({'post': 'traininglist'})),
path('customised/add/batch/', EmployeesAllowanceList.as_view({'post': 'addtoBatch'})),
path('attributes/add/batch/', EmployeesAllowanceList.as_view({'post': 'attributestobatch'})),

path('create/salary/batch/', SalaryBatchList.as_view({'post': 'create'})),
path('get/salary/batch/', SalaryBatchList.as_view({'post': 'view'})),
path('lock/salary/batch/', SalaryBatchList.as_view({'post': 'lockSalaryBatch'})),
path('unlock/salary/batch/', SalaryBatchList.as_view({'post': 'unlockSalaryBatch'})),
path('list/batches/salary/', SalaryBatchList.as_view({'get': 'listactivesalarybatches'})),
path('accountant/view/', PayrollAcountantViewset.as_view({'post': 'view'})),
path('accountant/verify/', PayrollAcountantViewset.as_view({'post': 'verifyemployeesalary'})),
path('accountant/transfer/', PayrollAcountantViewset.as_view({'post': 'transfer'})),

# Tax Slabs
path('add/tax/slab/', TaxSlabViewset.as_view({'post': 'create'})),
path('view/tax/slab/', TaxSlabViewset.as_view({'get': 'View'})),
path('patch/tax/slab/<pk>/', TaxSlabViewset.as_view({'patch': 'Patch'})),
path('delete/tax/slab/<pk>/', TaxSlabViewset.as_view({'delete': 'delete'})),
path('slab/lock/<pk>/', TaxSlabViewset.as_view({'get': 'lock'})),
path('slab/unlock/<pk>/', TaxSlabViewset.as_view({'get': 'unlock'})),

# Salary Records
path('salary/record/batches/', SalaryRecordsViewset.as_view({'get': 'view'})),
path('salary/record/', SalaryRecordsViewset.as_view({'post': 'record'})),

# Employee Side 
path('emp/salary/', EmployeeSalaryRecordsViewset.as_view({'post': 'record'})),

# process employee salary
# process_employee_salary
path('process/employee/salary/', PayrollAcountantViewset.as_view({'post': 'process_employee_salary'})),



]